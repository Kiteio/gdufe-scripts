import colorama, threading, sys, ddddocr
from datetime import datetime
from requests import Session
from bs4 import BeautifulSoup


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


if __name__ == "__main__":
    pass
