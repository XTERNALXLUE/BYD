# BYD——Build Your Dictionary

> 自用背(B)英语(Y)单词(D)工具
>
> “背，是为了不背。”——高中化学老师

## 启动：

```cmd
python -m venv venv_name

.\venv_name\Scripts\activate

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

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