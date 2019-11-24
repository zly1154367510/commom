import sys
import platform
import os
curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(r"%s/static" % (curPath))
from database import Mysql
import threading
import pymysql
class MysqlConn:

    _instance_lock = threading.Lock()
    conn = None
    cursor = None
    mysqlConfig = Mysql.mysqlConfig

    def __init__(self):
        if (self.conn == None):
            self.conn = pymysql.connect(
                host=self.mysqlConfig['hostname'],
                user=self.mysqlConfig['username'],
                password=self.mysqlConfig['password'],
                database=self.mysqlConfig['database'],
                use_unicode=self.mysqlConfig['use_unicode'],
                charset="UTF8"
            )

    def getCurosr(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

#模块中实例化MysqlConn对象
mysqlConn = MysqlConn()