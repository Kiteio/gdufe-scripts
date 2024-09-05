# 教学评价脚本

> 本模块未测试，请使用 [gdufe-evaluate](https://github.com/Kiteio/gdufe-evaluate) 代替

> 一键评教，解放双手

## 快速上手

1. 下载 Python（推荐最新版）
2. 将 [evaluation.py](evaluation.py) 保存到电脑
3. 在 [evaluation.py](evaluation.py) 中配置账号信息<br/>
   参数说明：

   | 参数         | 类型     | 描述                                                                                    |
   |------------|--------|---------------------------------------------------------------------------------------|
   | `USERNAME` | `int`  | 11位学号                                                                                 |
   | `PASSWORD` | `str`  | 门户密码                                                                                  |
   | `SUBMIT`   | `bool` | `True` 则运行后提交；`False` 则运行后只保存。建议先设置为 `False`，运行一次后打开网站看保存结果是否正确，无误后再设置为 `True` 重新运行一遍 |
4. 运行代码