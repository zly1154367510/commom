import datetime
import time

dateFormat = [
    '%Y-%m-%d %H:%M:%S'
]

# 获取当前时间戳
def nowTimestamp():
    return time.time()

# 获取当前日期
def nowDate():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

# 计算date加减days天后的日期
def dateAddAndSubtract(date=None,days=1,option='+'):
    if date == None:
        date = datetime.datetime.now();
    delta = datetime.timedelta(days=days)
    dateformat = None
    if type(date) != datetime.datetime:
        for item in dateFormat:
            date = datetime.datetime.strptime(date,item)
            if type(date) == datetime.datetime:
                break;
    if type(date) != datetime.datetime:
        raise Exception("输入的时间格式错误，无法转换成可用于操作的datetime对象")
    res = None
    if option == "+":
        res = date + delta;
    elif option == "-":
        res = date - delta;
    return res

# 计算两个日期的天数差
def daysDifference(str1,str2):
    date1=datetime.datetime.strptime(str1[0:10],"%Y-%m-%d")
    date2=datetime.datetime.strptime(str2[0:10],"%Y-%m-%d")
    num=(date1-date2).days
    return num

# 计算两个日期的月份差
def monthsDifference(str1,str2):
    year1=datetime.datetime.strptime(str1[0:10],"%Y-%m-%d").year
    year2=datetime.datetime.strptime(str2[0:10],"%Y-%m-%d").year
    month1=datetime.datetime.strptime(str1[0:10],"%Y-%m-%d").month
    month2=datetime.datetime.strptime(str2[0:10],"%Y-%m-%d").month
    num=(year1-year2)*12+(month1-month2)
    return num


# 计算两个日期的小时差
#  c为天数 d为小时 1为大的日期 2为小的日期
def hourDifference(time1,time2):
    format = '%Y-%m-%d %H:%M:%S'
    mini = time.strptime(time2, format)
    big = time.strptime(time1, format)
    t1 = int(time.mktime(big))
    t2 = int(time.mktime(mini))
    a = t1 - t2
    c = int(a / 86400)
    b = int(a % 86400 / 3600)
    return c,b
