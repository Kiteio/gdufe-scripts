# 选课脚本

> 本模块未测试，请使用 [gdufe-course](https://github.com/Kiteio/gdufe-course) 代替

> 温馨提示：该脚本会轮询服务器（简单比喻就是有个人一直在催促你事情做好了没有），请不要长时间运行。
> 现在是退选分离，我们也给了时间的参数，看不懂可以提 issue，我们会改进文档。

## 快速上手

1. 下载 Python（推荐最新版）
2. 将 [course.py](course.py) 保存到电脑
3. 在 [course.py](course.py) 中配置参数<br/>
   参数说明：

   | 参数               | 类型    | 描述                                                                         |
   |------------------|-------|----------------------------------------------------------------------------|
   | `USERNAME`       | `int` | 学号                                                                         |
   | `PASSWORD`       | `str` | 门户密码                                                                       |
   | `SORT`           | `str` | 课程分类。有效值：`必修课`、`选修课`、`通识课`、`专业内计划课`、`跨年级`、`跨专业`                            |
   | `PAGE`           | `int` | 页码，对应选课系统中课程列表最下方的页码。从`1`开始。                                               |
   | `INDEX`          | `int` | 目标课程在当前页码的列表中的下标。若为`-1`则不会进行选课。如果不知道填什么可以先设置为`-1`运行一遍，从运行日志的课程列表开头中括号获取数字。 |
   | `ENTER_TIME`     | `str` | 进入选课系统的时间，可以为空。例如`9:30`，则会在运行时登录教务系统，等到9点30分再尝试进入选课系统                      |
   | `ENTER_INTERVAL` | `int` | 进入选课系统的重试间隔，单位：秒。                                                          |
   | `PICK_TIME`      | `str` | 选课的时间，可以为空。例如`9:30`，则会在运行时登录教务系统，进入选课系统并查找课程（如果能进的话），等到9点30分再开始选课（点击选课按钮）  |
   | `PICK_INTERVAL`  | `int` | 选课的重试间隔，单位：秒。                                                              |

   以下参数对应的是`通识课`、`专业内计划课`、`跨年级`、`跨专业`顶部的搜索功能，只有你将`SORT`参数设置为这些分类，这些参数才会被用到。
   你在搜索功能设置了什么，可以一并填写到这里。

   | 参数            | 类型    | 描述                                                 |
   |---------------|-------|----------------------------------------------------|
   | `NAME`        | `str` | 课程名称。可以为空                                          |
   | `TEACHER`     | `str` | 教师名。可以为空                                           |
   | `DAY_OF_WEEK` | `str` | 星期几。可以为空，有效值：`1`、`2`、`3`、`4`、`5`、`6`、`7`           |
   | `SECTION`     | `str` | 节次。可以为空，有效值：`1-2`、`3-4`、`5-6`、`7-8`、`9-10`、`11-12` |
4. 运行代码
