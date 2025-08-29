# BYD——Build Your Dictionary

> 自用英语背单词工具

## 启动：

```cmd
python -m venv venv_name

.\venv_name\Scripts\activate

pip install -r requirements.txt

python DBY.py
```

安装完依赖后
可以桌面新建个.bat脚本
内容如下

```bat
@echo off

cd /d "D:\path\to\BYD"
call .\venv_name\Scripts\activate
python BYD.py
```

以后直接双击脚本启动