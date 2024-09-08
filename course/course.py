import colorama, threading, sys, ddddocr, time, re
from datetime import datetime
from requests import Session, Response
from bs4 import BeautifulSoup
from enum import Enum
from dataclasses import dataclass
from urllib.parse import quote

"""配置"""
# 学号
USERNAME = 12345678910
# 门户密码
PASSWORD = "abcd1234"
# 课程分类，有效值：必修课 | 选修课 | 通识课 | 专业内计划课 | 跨年级 | 跨专业
SORT = "必修课"
# 页码，从 1 开始
PAGE = 1
# 课程序号，请先设置为 -1，查看运行结果每一行开头方括号里的数字
INDEX = -1

# 进入选课系统开始时间，例如：9:30
# 如果不为空，则会先登录教务系统，等到该时间再开始进入选课系统
ENTER_TIME = ""
# 进入选课系统的间隔，单位：秒（教务系统没开会重试）
ENTER_INTERVAL = 1
# 选课操作开始时间，例如：9:30，
# 如果不为空，则会先进入选课系统并找到课程（如果能进的话），等到该时间时再开始选课操作
PICK_TIME = ""
# 选课间隔，单位：秒（选课未选上会重试）
PICK_INTERVAL = 1

"""
搜索配置（来自选课系统顶部的搜索功能）
只对 SORT 值为[通识课 | 专业内计划课 | 跨年级 | 跨专业]有效
"""
# 课程名
NAME = ""
# 教师
TEACHER = ""
# 星期几上课，空则不限制，填入特定数字，如 1，则表示只显示星期一的课程
# 有效值：空值 | 1 | 2 | 3 | 4 | 5 | 6 | 7
DAY_OF_WEEK = ""
# 节次
# 有效值：空值 | 1-2 | 3-4 | 5-6 | 7-8 | 9-10 | 11-12
SECTION = ""


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


class Sort(Enum):
    BASIC = "bx"
    OPTIONAL = "xx"
    GENERAL = "ggxxk"
    MAJOR = "bxqjh"
    CROSS_MAJOR = "knj"
    CROSS_YEAR = "faw"

    def __init__(self, route: str):
        """
        课程分类
        :param route: 路由
        """
        self.route = route

    def searchable(self) -> bool:
        """
        该课程分类是否可搜索
        :return True 该课程为 Sort.BASIC 或 Sort.OPTIONAL，False 则为带有搜索功能的分类
        """
        return self != Sort.BASIC and self != Sort.OPTIONAL


@dataclass
class Course:
    """课程"""
    operate_id: str  # 选退课操作 id
    id: str  # 课程编号
    name: str  # 课程名
    teacher: str  # 教师
    time: str  # 上课时间
    area: str  # 上课地点
    sort: Sort  # 分类

    def __str__(self) -> str:
        return f"{self.name} | {self.teacher} | {self.time} | {self.area}"


class CourseSystem(Router):
    def __init__(self, name: int, pwd: str, session: Session):
        """
        选课系统
        :param name: 学号
        :param pwd: 门户密码
        :param session: 教务系统会话
        """
        super().__init__("http://jwxt.gdufe.edu.cn")

        self.name = name
        self.pwd = pwd
        self.__session = session

    def course_list(self, sort: Sort, page: int) -> list[Course]:
        """
        课程列表
        :param sort: 分类
        :param page: 页码下标
        :return: 课程列表
        """
        self.__check_sort(sort, not sort.searchable())

        return self.__parse(
            self.__session.post(
                self.route(f"/jsxsd/xsxkkc/xsxk{sort.route.capitalize()}xk"),
                self.__form(page)
            ),
            sort
        )

    def course_search(
            self, sort: Sort, page: int, name: str, teacher: str, day_of_week: str, section: str
    ) -> list[Course]:
        """
        课程搜索
        :param sort: 分类
        :param page: 页码下标
        :param name: 课程名
        :param teacher: 教师
        :param day_of_week: 星期几
        :param section: 节次
        :return: 课程列表
        """
        self.__check_sort(sort, sort.searchable())

        section = section if section == "" or section.endswith("-") else section + "-"
        params = {
            "kcxx": self.__encode(name),
            "skls": self.__encode(teacher),
            "skxq": self.__encode(day_of_week),
            "skjc": self.__encode(section),
            "sfym": "false",
            "sfct": "false"
        }

        return self.__parse(
            self.__session.post(
                self.route(f"/jsxsd/xsxkkc/xsxk{sort.route.capitalize()}xk"),
                self.__form(page),
                params=params
            ),
            sort
        )

    @staticmethod
    def __encode(text: str) -> str:
        """
        二次编码
        :param text: 待编码字符串
        :return: 二次编码后字符串
        """
        return quote(quote(text))

    def __check_sort(self, sort: Sort, predicate: bool):
        """
        检验课程分类是否正确
        :param sort: 课程分类
        :param predicate: False 则课程分类错误
        """
        if not predicate:
            Log.e(self.name, f"错误的课程分类 {sort}")

    @staticmethod
    def __form(page: int, count=15) -> dict:
        """
        获取课程列表需要提交的表单
        :param page: 页面下标
        :param count: 单页数量
        :return: 表单
        """
        return {
            "iDisplayStart": count * page,
            "iDisplayLength": count
        }

    @staticmethod
    def __parse(response: Response, sort: Sort) -> list[Course]:
        """
        将网络请求结果解析为课程列表
        :param response: 网络请求结果
        :param sort: 课程分类
        :return: 课程列表
        """
        return [
            Course(
                operate_id=course["jx0404id"],
                id=course["kch"],
                name=course["kcmc"],
                teacher=course["skls"],
                time=course["sksj"],
                area=course["skdd"],
                sort=sort
            ) for course in response.json()["aaData"]
        ]

    def pick(self, course: Course, interval: int):
        """
        递归选课
        :param course: 课程
        :param interval: 操作间隔
        """
        params = {
            "jx0404id": course.operate_id,
            "xkzy": "",
            "trjf": "",
            "cxxdlx": 1
        }
        json = self.__session.get(self.route(f"/jsxsd/xsxkkc/{course.sort.route}xkOper"), params=params).json()

        try:
            if json["success"]:
                Log.i(self.name, "选课成功")
            else:
                Log.i(self.name, json["message"])
                time.sleep(interval)

                self.pick(course, interval)
        except KeyError:
            Log.e(self.name, "账号在别处登录")
        except RecursionError:
            self.pick(course, interval)


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

    def course_system(self, interval: int) -> CourseSystem:
        """
        递归进入选课系统
        :param interval: 递归间隔
        :return: 选课系统
        """
        # 获取进入选课系统链接
        route = None
        response = self.__session.get(self.route("/jsxsd/xsxk/xklc_list"))
        soup = BeautifulSoup(response.text, "html.parser")
        tags = soup.find("table", id="tbKxkc").find_all("a")
        for tag in tags:
            if tag.text == "进入选课":
                route = tag["href"]
                break

        if route is None:
            Log.i(self.name, f"没有进入选课链接，{interval} 秒后重试")
            time.sleep(interval)
            return self.course_system(interval)

        self.__session.get(self.route(route))
        Log.i(self.name, "进入选课系统")
        return CourseSystem(self.name, self.pwd, self.__session)


def get_sort_by_key(key: str) -> Sort:
    """
    通过 key 获取课程分类
    :param key: 课程分类 key
    :return: 课程分类
    """
    return {
        "必修课": Sort.BASIC,
        "选修课": Sort.OPTIONAL,
        "通识课": Sort.GENERAL,
        "专业内计划课": Sort.MAJOR,
        "跨年级": Sort.CROSS_YEAR,
        "跨专业": Sort.CROSS_MAJOR
    }[key]


def waiting(name: int, t: str):
    """
    在 t 之前阻塞线程
    :param name: 学号
    :param t: 时间，格式：[小时][单个非数字分隔符][分钟]
    """
    if t == "":
        return

    nums = re.findall(r"\d+", t)
    while not check_time(name, nums[0], nums[1]):
        time.sleep(1)


def check_time(name: int, h: int, m: int):
    """
    检查当前时间是否符合提供的小时分钟
    :param name: 学号
    :param h: 小时
    :param m: 分钟
    """
    now = datetime.now()
    Log.i(name, f"等待中 {h}:{m}")
    return now.hour >= h and now.minute >= m - 1 and now.second > 50


if __name__ == "__main__":
    edu_system = EduSystem(USERNAME, PASSWORD)

    waiting(USERNAME, ENTER_TIME)

    course_system = edu_system.course_system(ENTER_INTERVAL)
    mSort = get_sort_by_key(SORT)

    # 获取课程列表
    if mSort.searchable():
        courses = course_system.course_search(mSort, PAGE - 1, NAME, TEACHER, DAY_OF_WEEK, SECTION)
    else:
        courses = course_system.course_list(mSort, PAGE - 1)
    Log.i(
        course_system.name,
        f"课程列表：\n{'\n'.join([f"[{index}] {course}" for index, course in enumerate(courses)])}"
    )

    # 选课
    if INDEX != -1:
        waiting(USERNAME, PICK_TIME)
        course_system.pick(courses[INDEX], PICK_INTERVAL)
