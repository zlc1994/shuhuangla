书荒啦——利用协同过滤解决书荒
====

## Prerequisites

 - Python > 3.5
 - Redis
 - MySQL

## 配置

### 安装依赖

```bash
$ pip install -r requirements.txt
```

### 修改`config.py`


### 创建数据库

根据配置在MySQL中创建数据库

### 进行数据库迁移

```bash
$ export FLASK_APP=shuhuang.py
$ flask db upgrade
```

### 将原始小说信息插入数据库

```bash
$ flask shell
>>> Book.insert_book()
```

### 运行rq worker

```bash
$ rq worker email -u "your-redis-uri"
$ rq worker spider -u "your-redis-uri"
$ rq worker cf -u "your-redis-uri"
```

### 计算相似小说结果

```
$ python run_tasks.py
```

### 运行服务器

```bash
$ flask run
```
