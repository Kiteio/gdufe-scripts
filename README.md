# 广东财经大学脚本集

<p>

[![](https://img.shields.io/static/v1?label=Python&message=3.7+%2B&labelColor=white&color=white&logo=python)](https://www.python.org/downloads/)

</p>

> **请勿滥用 概不负责**

## 功能
点击即可前往对应目录，详细的使用描述在目录中的 ***README.md*** 文件中。

- [自动选课](course)
- [校园网登录](network)
- [自动教学评价](evaluation)（未测试）


## 目录说明
```
gdufe-scripts
├── course               # 选课脚本
├── evaluation           # 教学评价脚本
├── network              # 校园网登录脚本
├── requiremenet.txt     # template.py 依赖库
└── template.py          # 教务系统脚本模板文件
```


## 开发者
前面提到的功能都是基于 [template.py](template.py) 做的开发，为了方便使用我们将模板的代码放置在同一文件中。

这是一份教务系统登录模板，您可以在此基础上进行二次开发，相关的依赖放置于 [requirements.txt](requirements.txt)。