# 教学评价脚本

> 本模块未测试，请使用 [gdufe-evaluate](https://github.com/Kiteio/gdufe-evaluate) 代替

> 一键评教，解放双手

## 快速上手

1. 安装 [Python](https://www.python.org/downloads/)（推荐最新版，记得勾选`Add Python [版本号] to PATH`）。
2. 在命令行使用`pip`下载 [requirements.txt](requirements.txt) 提到的依赖<br/>
   例如：
   ```
   pip install colorama
   ```
   如果熟悉用 [requirements.txt](requirements.txt) 安装也可以保存该文件，在命令行定位到该文件所在文件夹，并输入以下命令：
   ```
   pip install -r requirements.txt
   ```
3. 将 [evaluation.py](evaluation.py) 保存到电脑
4. 在 [evaluation.py](evaluation.py) 中配置账号信息<br/>
   参数说明：

   | 参数         | 类型     | 描述                                                                                    |
   |------------|--------|---------------------------------------------------------------------------------------|
   | `USERNAME` | `int`  | 11位学号                                                                                 |
   | `PASSWORD` | `str`  | 门户密码                                                                                  |
   | `SUBMIT`   | `bool` | `True` 则运行后提交；`False` 则运行后只保存。建议先设置为 `False`，运行一次后打开网站看保存结果是否正确，无误后再设置为 `True` 重新运行一遍 |
5. 运行代码