import platform
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(r"%s/static" % (curPath))
sys.path.append(r"%s" % (curPath))
from database import Redis,Mail
import redis
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import date_build as dateB
class RedisConn:

    conn = None
    redisConfig = Redis.redis

    def __init__(self,selectDb = 1):
        if self.conn == None:
            self.conn = redis.Redis(
                host = self.redisConfig['hostname'],
                port = self.redisConfig['port'],
                db = selectDb,
                password = self.redisConfig['password'],
                decode_responses = True
            )

    def updateRedisNum(self,num,name='thread'):
        redisThreadNum = self.conn.get(name);
        if redisThreadNum != None:
            self.conn.set(name,int(redisThreadNum)+int(num))
        else:
            self.conn.set(name,num)

    def updateRedisContent(self,content,name='weibo_top_search'):
        self.conn.set(name,content)

    def getData(self,name):
        return self.conn.get(name)

class ReportRedis(RedisConn):

    def __init__(self):
        RedisConn.__init__(self)

    def sendReport(self,context):
        ret = True
        # try:
        my_sender = Mail.reportMail['email_address']  # 发件人邮箱账号
        my_pass = Mail.reportMail['password']  # 发件人邮箱密码
        my_user = Mail.reportMail['send_email_address']
        msg = MIMEText(context, 'plain', 'utf-8')
        msg['From'] = formataddr(["zyy", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["FK", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "爬虫信息报表"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL(Mail.reportMail['smtp_host'],Mail.reportMail['smtp_port'])  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        # except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        #     ret = False
        return ret

    def buildRedisReport(self):
#         获取帖子的数量
        threadNum = self.conn.get('thread')
#         获取已经更新回复的数量updateThreadNum
        replyThreadNum = self.conn.get('reply_thread')
#         获取回复的获取数量
        replyNum = self.conn.get('reply')
        # 获取两次发简报的时间差
        lastSendReportDate = self.conn.get('last_send_report_date')
        nowDate = dateB.nowDate()
        context = ''
        if (lastSendReportDate != None):
            daysDifference,hourDifference = dateB.hourDifference(str(nowDate),lastSendReportDate)
            context += '经过 %s 天 %s 小时的运行，'%(daysDifference,hourDifference)
        context += "扑爬虫共获取<br>新帖子：%s 条<br>新回复：%s 条<br>更新帖子：%s 条" %(threadNum,replyNum,replyThreadNum)
        # 初始化redis统计数量
        self.conn.set('thread',0)
        self.conn.set('reply_thread',0)
        self.conn.set('reply',0)
        self.conn.set('last_send_report_date',nowDate)
        return context


if __name__ == '__main__':
    ret = ReportRedis()
    # ret.conn.set('thread', 32)
    # ret.conn.set('reply_thread', 566)
    # ret.conn.set('reply', 231)
    # ret.conn.set('last_send_report_date', "2019-03-10 11:52:51")
    mailContext = ret.buildRedisReport();
    r = ret.sendReport(mailContext)
    if r:
        print("邮件发送成功")
    else:
        print("邮件发送失败")