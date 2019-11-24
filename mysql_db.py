import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(r"%s/static" % (curPath))
import threading
from database import Mysql
from mysql_conn import mysqlConn
import time;
class MysqlDb:

    _instance_lock = threading.Lock()
    mysqlConfig = Mysql.mysqlConfig
    tableList = None
    cursor = None
    error = ''
    whereOption = [
        '=','>','<','<>','like','in','not in'
    ]
    printSqlOpen = False


    @property
    def conn(self):
        return MysqlDb.conn

    @conn.setter
    def conn(self,conn):
        MysqlDb.conn = conn

    def __init__(self,table):
        if self.cursor == None:
            self.cursor = mysqlConn.getCurosr()
        # 初始化所有表格
        self.__getDbTableList(self.cursor)
        if (self.tableList.count(table) == 0):
            self.error += '指定的数据表“%s”不存在'%(table)
        # 初始化当前表的所有字段
        self.__getDbTableField(self.cursor,table)
        self.selectSql = 'select {field} from '+table+' {where} {order by} {limit}'
        self.sql = 'select {field} from '+table+' {where} {order by} {limit}'
        self.updateSql = 'update '+table+' set {field_var} where {where}'
        self.insertSql = 'insert into '+table+' ({field}) values {values}';
        self.deleteSql = 'delete from '+table+' where {where}';
        self.where = []
        self.order = ''
        self.group = ''
        self.soft = ''
        self.field = ''
        self.limit = ''

    #获取所有表格
    def __getDbTableList(self,cursor):
        # 获取所有表格
        if self.tableList == None:
            cursor.execute("show tables");
            self.tableList = [tuple[0] for tuple in cursor.fetchall()]
        else:
            return;

    def __getDbTableField(self,cursor,tableName):
        if (self.tableList.count(tableName) == 0):
            raise Exception(self.error)
        cursor.execute("select * from %s" % tableName)
        self.tableField= [tuple[0] for tuple in cursor.description]

    def dbWhere(self,field=None,option=None,var=None,array={}):
        if len(array) != 0:
            for index,item in array.items():
                where = "%s %s %s" % (index, '=', item)
                self.where.append(where)
        else:
            if type(var) != str:
                var = str(var)
            if (MysqlDb.whereOption.count(option) == 0):
                self.error += "查询方式“%s”错误 "%(option)
            if (self.tableField.count(field) == 0):
                self.error += "查询的字段“%s”不存在"%(field)
            if option == 'in' or option == 'not in':
            #     处理的in的查询方式
                var = var.replace('[','')
                var = var.replace(']','')
                var = "("+var+")"
            else:
                var = '"'+var+'"'
            where = "%s %s %s"%(field,option,var)
            self.where.append(where)


    def dbSelect(self,isAll = True,isFields = True):
        if self.error != '':
            raise Exception(self.error)
        self.__sqlPlaceholderReplace()
        if self.printSqlOpen:
            print(self.sql)
        self.cursor.execute(self.sql)
        self.sql = self.selectSql;
        self.where = []
        self.order = ''
        self.group = ''
        self.soft = ''
        self.field = ''
        res = [];
        if isAll:
            value = self.cursor.fetchall()
            if isFields == False:
                res = [];
                for i in value:
                    res.append(i[0])
                return res
            field = self.cursor.description
            for item in value:
                list1 = {}
                for resItem,fieldItem in zip(item,field):
                    list1[fieldItem[0]] = resItem
                res.append(list1)
        self.cursor = mysqlConn.getCurosr()
        self.where = []
        return res

    def dbFields(self,field):
       self.field = field

    def dbOrder(self,field,soft=None):
        self.soft = 'DESC'if soft==None else soft
        self.order = field

    def dbLimit(self,offset,num):
        self.limit = "limit %s,%s" %(str(offset),str(num))

    def __sqlPlaceholderReplace(self):
        self.__genranalReplace("where",self.where,"and")
        self.__orderReplace("order by");
        self.__limitReplace("limit");
        self.__strReplace("field",self.field)

    #处理where这类型的占位符
    def __strReplace(self,option,var):
        placeholder = "{"+option+"}"
        if (var!= ""):
            self.sql = self.sql.replace(placeholder,var)
        else:
            self.sql = self.sql.replace(placeholder, "*")

    def __orderReplace(self, option):
        placeholder = "{" + option + "}"
        if (self.order != ''):
            self.sql = self.sql.replace(placeholder, option +" "+ self.order + " " + self.soft)
        else:
            self.sql = self.sql.replace(placeholder, "")

    def __limitReplace(self,option):
        placeholder = "{" + option + "}"
        if (self.limit != ''):
            self.sql = self.sql.replace(placeholder,self.limit)
        else:
            self.sql = self.sql.replace(placeholder, "")

    def __genranalReplace(self,option,var,connector):
        placeholder = "{"+option+"}"
        if (len(var) != 0):
            var = " and ".join(var)
            self.sql = self.sql.replace(placeholder,option+" "+var)
        else:
            self.sql = self.sql.replace(placeholder,"")

    def __genranalConnectorReplace(self,option,var,connector):
        placeholder = "{"+option+"}"
        res = ''
        if (len(var) != 0):
            res = " and ".join(var)
        return res

    def dbGroup(self):
        print('s')

    def dbInsertAll(self,field,var,insertDataBuildType = 1):
        checkRes = self.__checkInsertList(field,var)
        if (checkRes == False and self.error != ''):
            raise Exception(self.error)
        if insertDataBuildType == 1:
            self.insertSql = self.__buildInsertSql(field,var)
        else:
            pass
        insertRes = self.cursor.execute(self.insertSql)
        mysqlConn.commit();
        return insertRes

    def dbInsertReturnId(self,field,var,insertDataBuildType = 1):
        checkRes = self.__checkInsertList(field,var)
        insertIdList = [];
        if (checkRes == False and self.error != ''):
            raise Exception(self.error)
        if insertDataBuildType == 1:
            for item in var:
                insertSql = self.__buildInsertSql(field,[item])
                if self.printSqlOpen:
                    print(insertSql)
                self.cursor.execute(insertSql)
                insertIdList.append(self.cursor.lastrowid)
                mysqlConn.commit()
        else:
            pass
        return insertIdList

    def dbUpdate(self,field,var):
        if (self.where == []):
            self.error = "缺少更新条件"
            raise Exception(self.error)
        updateSql = self.__buildUpdateSql(field,var)
        updateSql = updateSql.replace('{where}',self.__genranalConnectorReplace("where",self.where,"and"))
        if self.printSqlOpen:
            print(updateSql)
        res = self.cursor.execute(updateSql)
        mysqlConn.commit()
        self.cursor = mysqlConn.getCurosr()
        self.where = [];
        return res

    def dbDelete(self):
        if (self.where == []):
            self.error = "缺少删除条件"
            raise Exception(self.error)
        deleteSql = self.deleteSql.replace('{where}', self.__genranalConnectorReplace("where", self.where, "and"))
        if self.printSqlOpen:
            print(deleteSql)
        res = self.cursor.execute(deleteSql)
        mysqlConn.commit()
        self.cursor = mysqlConn.getCurosr()
        self.where = [];
        return res

    def __checkInsertList(self,field,var):
        insertValueRes = []
        #去除传入数组中不属于数据表字段的元素
        for item in field:
            if item not in self.tableField:
                self.error += '指定插入的字段中存在不属于数据库的字段%s' %(item)
                return False
        for item in var:
            if (len(item) != len(field)):
                self.error += " 插入字段和插入数据数量不一致"
                return False;

    def __buildInsertSql(self,field,var):
        if 'creation_time' in self.tableField:
            nowDate = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            for item in var:
                item.append(nowDate)
        if "creation_time" not in field:
            field.append('creation_time')

        field = ",".join(field)
        insertSql = self.insertSql.replace('{field}',field)
        insertDataList = []
        for item in var:
            tempItem = []
            for valueItem in item:
                tempItem.append('"'+str(valueItem)+'"')
            insertDataList.append("("+','.join(tempItem)+")")
        insertValue = ','.join(insertDataList)
        insertSql = insertSql.replace('{values}',insertValue)
        return insertSql

    def ___buildDeleteSql(self):

        pass

    def __buildUpdateSql(self,field,var):
        if 'last_update_time' in self.tableField:
            nowDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            var.append(nowDate)
        if "last_update_time" not in field:
            field.append('last_update_time')
        fieldVarSql = []
        for fieldItem,varItem in zip(field,var):
            if fieldItem not in self.tableField:
                continue
            else:
                fieldVarSql.append('%s = "%s"' %(fieldItem,varItem))
        fieldVarSql = ','.join(fieldVarSql)
        updateSql = self.updateSql.replace('{field_var}',fieldVarSql)
        return updateSql







# if __name__ == '__main__':
#     mysql = MysqlDb('thread')
    # mysql.dbWhere("title","=","买车")
    # mysql.dbWhere("author","=","我")
    # mysql.dbUpdate(['title'],['hhhh'])
#     mysql = MysqlDb('thread')
#     mysql.dbInsert(['title','author','posted_time'],[['我要买宝马','我','1570777666'],['我要买奔驰','你','1570777622']])
#     # mysql.dbWhere("title","=","买车")
#     # mysql.dbWhere("author","=","我")
#     # mysql.dbSelect(True)
#     # print(mysql.sql)
#     # mysql1 = MysqlDb('thread')
#     # print(mysql1.sql)
    

