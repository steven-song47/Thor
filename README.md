# 更新requirements.txt文件
pip freeze >requirements.txt 

# 生成数据库映射
1、在主文件中导入对应Models；
2、在命令行输入如下：
    export FLASK_APP=main.py
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade

# issue
1、映射数据库屎报错：NameError: name ‘_mysql‘ is not defined
    原因：Mysqldb 不兼容 python3.5 以后的版本
    解决办法： 使用pymysql代替MySQLdb
    步骤：
        1、安装pymysql：pip install pymysql
        2、打开项目在setting.py的init.py,或直接在当前py文件最开头添加如下：
            import pymysql
            pymysql.install_as_MySQLdb()

2、db migration过程中，出现错误提示：ERROR [flask_migrate] Error: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods
    解决办法：pip3 install --user cryptography

3、执行命令flask db migrate报错：ERROR [flask_migrate] Error: Can't locate revision identified by '472ff146fdfc'
    解决办法：在执行flask db migrate命令前，执行命令： flask db revision --rev-id 472ff146fdfc
