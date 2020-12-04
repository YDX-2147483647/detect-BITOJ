import time
import logging
import traceback

import generate_C_code

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def detect(browser, page_id, n, data_size=32, input_format_string="", indices=[]):
    """探测保密测试用例

    :param browser: 浏览器的 Web Driver 。
    :param page_id: 页面的id，即 URL 末尾 "?id=" 之后的数字。
    :param n: 每个测试用例中输入的个数，其指可能与用何种方法探测有关。
    :param data_size: 每个输入的最大（二进制）位数。
    :param input_format_string: C语言的格式字符串，例如 "%d,%c %d" 。默认为 "%d%d..." 。
    :param indices: 要探测的输入的下标的列表（或类似物）。（已经探测到部分时可能需要这个参数）
    :return: 记录了所有测试输入的词典，格式为 {<编号>: [<测试输入>]} 。
    """
    if not indices:
        indices = range(n)

    url_head = "http://lexue.bit.edu.cn/mod/programming/"
    result_page = f"{url_head}result.php?id={page_id}"
    submit_page = f"{url_head}submit.php?id={page_id}"

    arguments = {}
    # TODO
    # arguments = {'3': [2, 3, 1, 2, 3, 4, 5, 6, 0, 1023, 0, 296, 1021, 504, 874, 432, 793, 456, 1020],
    #              '4': [5, 7, 534, 1, 543, 3, 2, 4, 6, 12, 3, 45, 3, 2, 13, 22, 1, 33, 56],
    #              '5': [4, 5, 1, 2, 3, 4, 5, 5, 4, 3, 2, 1, 2, 3, 4, 5, 1, 3, 4]}

    logging.info(f"现在开始探测#{page_id}。")
    try:
        is_first_argument = True
        # TODO is_first_argument = False
        for i in indices:
            is_first_digit = True
            for d in range(0, data_size, 2):
                # 访问页面
                browser.get(submit_page)
                WebDriverWait(browser, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role=main]"))
                )
                if browser.find_elements_by_id("submitagain"):
                    # 如果已经AC，网页会有提示
                    browser.find_element_by_id("submitagain").click()

                # 提交代码
                logging.info(f"正在探测第{i}个参数的第{d}和{d + 1}位。")
                browser.find_element_by_id("id_code").send_keys(
                    generate_C_code.get_2_binary_digit(n, i, d, input_format_string))
                browser.find_element_by_name("submitbutton").click()
                WebDriverWait(browser, 20).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "查看结果"))
                )

                # 查看结果并记录
                is_compiled = False
                while not is_compiled:
                    browser.get(result_page)
                    WebDriverWait(browser, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role=main]"))
                    )
                    if browser.find_elements_by_link_text("以文本方式显示"):
                        is_compiled = True
                        rows = browser.find_elements_by_css_selector("#test-result-detail tbody > tr")
                        for r in rows:
                            row_number = r.find_element_by_css_selector("[class~='c0']").text
                            is_secret = r.find_element_by_css_selector("[class~='c4']").text == "保密"
                            if is_secret:
                                result = r.find_element_by_css_selector("[class~='c12']").text.split(":")[0]
                                if is_first_argument and is_first_digit:
                                    arguments[row_number] = []
                                if is_first_digit:
                                    arguments[row_number].append(0)
                                arguments[row_number][i] += generate_C_code.error_dict[result] << d
                        logging.info(f"已探明第{i}个参数的第{d}和{d + 1}位。")
                    else:
                        logging.info("仍在等待编译。")
                        time.sleep(2)
                is_first_digit = False
            is_first_argument = False
            logging.info(f"已探明第{i}个参数。")
        logging.info("已探明全部参数。")
    except Exception:
        traceback.print_exc()
    finally:
        return arguments


def print_arguments(arguments):
    """将测试输入打印成人类易读的形式

    :param arguments: 记录了所有测试输入的词典，格式为 {<编号>: [<测试输入>]} 。
    """
    print("No. | 测试输入")
    for row_number, values in arguments.items():
        print(f"{row_number:2}  |", end="")
        for i in values:
            print(f" {i:3}", end="")
        print("")


# TODO: 自动判断数据大小
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    save_directory = r"arguments.txt"

    questions = eval(input('请输入探测目标。（例：[("205933", 3, 12, "")]）>>'))

    browser = webdriver.Edge(executable_path=r"D:\softwares\edgedriver_win64\msedgedriver.exe")
    browser.get(r"http://lexue.bit.edu.cn")
    if "login" in browser.current_url:
        input("请登录。完成后请按Enter。>>")

    for args in questions:
        # TODO arguments = detect(browser, page_id, n, data_size, input_format_string)
        page_id = args[0]
        arguments = detect(browser, *args)

        print(f"#{page_id}的保密测试用例：")
        print_arguments(arguments)

        with open(save_directory, "a") as f:
            f.write(time.asctime())
            f.write(f"\npage id: {page_id}\n")
            f.write(repr(arguments))
            f.write("\n\n")
        print(f"已存入 {save_directory} 。")

    input("请按 Enter 退出. . . >>")
