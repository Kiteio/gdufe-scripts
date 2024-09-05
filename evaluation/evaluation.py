import colorama, threading, sys, ddddocr
from datetime import datetime
from requests import Session
from bs4 import BeautifulSoup
from dataclasses import dataclass

"""
WARN 未测试，本行注释移除前请谨慎使用
请使用 https://github.com/Kiteio/gdufe-evaluate 代替
"""

"""配置"""
# 学号
USERNAME = 12345678910
# 门户密码
PASSWORD = "abcd1234"
# 是否提交
SUBMIT = False


class Log:
    """日志"""

    @staticmethod
    def __log(tag: str, color: colorama.Fore, username: int, message: str, offset: int = 0):
        """
        日志输出
        :param tag: 标签
        :param color: 标签颜色
        :param username: 学号
        :param message: 消息
        :param offset: 标签后偏移量
        """
        # 日期时间 yyyy-mm-dd HH:MM:SS
        _ = (colorama.Fore.LIGHTBLUE_EX +
             datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
             colorama.Fore.RESET)
        # 线程名
        current_thread_name = threading.current_thread().name

        # 时间 [线程] [标签][偏移] <学号> 消息
        print(f"{_} [{current_thread_name}] {color}[{tag}]{colorama.Fore.RESET}{' ' * offset} <{username}> {message}")

    @staticmethod
    def i(username: int, message: str):
        """
        INFO 日志输出
        :param username: 学号
        :param message: 消息
        """
        Log.__log("INFO", colorama.Fore.LIGHTGREEN_EX, username, message, 1)

    @staticmethod
    def e(username: int, message: str):
        """
        ERROR 日志输出
        :param username: 学号
        :param message: 消息
        """
        Log.__log("ERROR", colorama.Fore.RED, username, message)
        sys.exit(1)


class Router:
    def __init__(self, root: str):
        """
        路由
        :param root: 根路径
        """
        self.root = root

    def route(self, path: str = "") -> str:
        """
        路由拼接
        :param path: 二级路径
        :return: 拼接后的路径
        """
        return self.root + (path if path.startswith("/") else "/" + path)


@dataclass
class EvaluateItem:
    """评教项"""
    id: str  # 课程编号
    name: str  # 课程名称
    teacher: str  # 教师
    sort: str  # 课程类别
    route: str  # 评教路由


class EduSystem(Router):
    def __init__(self, name: int, pwd: str):
        """
        教务系统
        :param name: 学号
        :param pwd: 门户密码
        """
        super().__init__("http://jwxt.gdufe.edu.cn")

        with Session() as session:
            # 获取验证码和 Cookie
            response = session.get(self.route("/jsxsd/verifycode.servlet"))

            # 识别验证码
            ocr = ddddocr.DdddOcr(show_ad=False)
            code = ocr.classification(response.content)

            # 登录
            data = {
                "USERNAME": name,
                "PASSWORD": pwd,
                "RANDOMCODE": code
            }
            response = session.post(self.route("/jsxsd/xk/LoginToXkLdap"), data=data)
            soup = BeautifulSoup(response.text, "html.parser")

            # 确认登录结果
            title = soup.find("title").text
            if title == "学生个人中心":
                self.name = name
                self.pwd = pwd
                self.__session = session
                Log.i(name, "登录成功")
            elif title == "广东财经大学综合教务管理系统-强智科技":
                Log.e(name, soup.find("font").text)
            else:
                Log.e(name, f"未知的标题：{title}")

    def evaluate_items(self) -> list[EvaluateItem]:
        """
        获取评教项列表
        :return: 评教项列表
        """
        response = self.__session.get(self.route("/jsxsd/xspj/xspj_find.do"))
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="Nsb_r_list Nsb_table")
        rows = table.find_all("tr")

        if len(rows) > 1:
            # 表格中的分类项
            elements = rows[1].find_all("td")[6].find_all("a")

            items = []

            for element in elements:
                sort = element.text

                # 每一个分类中的课程列表
                response = self.__session.get(self.route(element["href"]))
                soup = BeautifulSoup(response.text, "html.parser")
                inner_rows = soup.find("table", id="dataList").find_all("tr")

                for index in range(1, len(inner_rows)):
                    infos = inner_rows[index].find_all("td")

                    try:
                        # onclick 参数如果没有则表示已评价
                        route = infos[7].a["onclick"][7:-12]
                    except (AttributeError, IndexError):
                        # 跳过已评价
                        continue

                    items.append(
                        EvaluateItem(
                            id=infos[1].text,
                            name=infos[2].text,
                            teacher=infos[3].text,
                            sort=sort,
                            route=route
                        )
                    )

            return items
        else:
            Log.e(self.name, "教学评价未开放")
            return []

    def evaluate(self, items: list[EvaluateItem], submit: bool = True):
        """
        评价评教列表
        :param items: 评教列表
        :param submit: 是否提交
        """
        if len(items) == 0:
            Log.i(self.name, "没有待评价项")
            return

        # 逐一评价
        for item in items:
            response = self.__session.get(self.route(item.route))
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", id="Form1")
            elements = table.find_all("input")
            rows = table.find("table", id="table1").find_all("tr")

            data = []

            # 基础信息
            for index in range(len(elements) - 2):
                key = elements[index]["name"]
                value = ("1" if submit else "0") if key == "issubmit" else elements[index].attr("value")
                data.append((key, value))

            # 选项
            for index in range(1, len(rows)):
                infos = rows[index].find_all(recursive=False)

                if len(infos) == 2:
                    first = infos[0].contents[0]
                    data.append((first["name"], first["value"]))

                    options = infos[1].find_all(recursive=False)
                    for option_index in range(1, len(options), 2):
                        if option_index == 1:
                            data.append((options[0]["name"], options[0]["value"]))

                        data.append((options[option_index]["name"], options[option_index]["value"]))

            # 上传表单
            self.__session.post(self.route("/jsxsd/xspj/xspj_save.do"), data=data)
            Log.i(self.name, f"{'已评价' if submit else '已保存'} {item.id} {item.name} {item.teacher}")


if __name__ == "__main__":
    edu_system = EduSystem(USERNAME, PASSWORD)
    evaluate_items = edu_system.evaluate_items()
    edu_system.evaluate(evaluate_items, SUBMIT)
