# CVEupdates

A CVE monitoring system. When a NVD is updated or a CVE is added, the new info for NVD will be added into database.

Info Crawled from NVD:

* description
* priority
* solution status
* attack vector
* impact
* affacted components
* solutions
* vendor advisories
* references

## 项目部署
（在本目录下执行）
```
1. 安装mysql   
    sudo apt-get install mysql-server
    安装过程中输入密码（默认123456）
    sudo apt-get install mysql-client
    sudo apt-get install libmysqlclient-dev

2. 登录mysql数据库并导入数据库文件
    mysql -u root -p
    (输入密码)
    mysql> use timo
    mysql> source nvds.sql

3. 安装python3.4+
    p
```

```
    (搭建python虚环境)
    python -m venv cveupdates_venv
    source cveupdates_venv/bin/activate
    pip install requirements.txt
    deactivate

    （安装screen)
    sudo apt-get update
    sudo apt-get install screen 
```

## CVE监测部分爬虫部署
（在本目录下执行）

```
    screen -S spider
    (跳入新窗口)

    source cveupdates_venv/bin/activate
    (激活虚环境)
    python dailyUpdate.py

    Ctrl+A 
    D 

```
