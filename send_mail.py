import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from jinja2 import Environment,FileSystemLoader

class SendMail:

    env = None
    messageTemplate = None

    def __init__(self):
        pass

    def setMessageTemplate(self,messageTemplate=None,fileSystemPath=None,messageTemplateType = 1):
        if messageTemplateType == 1:
            loader = FileSystemLoader(fileSystemPath)
            self.env = Environment(loader=loader)
            self.messageTemplate = self.env.get_template(messageTemplate)
        return self


    def sendMessageTemplate(self):
        pass

    def sendMail(self,context,subject,my_name=None,senderData={},smtp_port=None,smtp_host=None,from_name=None,email_address=None,password=None,send_email_address=[],to_name=None):
        ret = True
        # try:
        my_sender = email_address # 发件人邮箱账号
        my_pass = password  # 发件人邮箱密码
        my_user = send_email_address
        msg = MIMEText(context, 'html', 'utf-8')
        msg['From'] = formataddr(["zyy", from_name])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["FK", to_name])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = subject  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL(smtp_host,smtp_port)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, my_user, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        # except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        #     ret = False
        return ret

    def setSenderData(self,senderData={}):
        self.data = senderData
        return self

    def renderMessageTemplate(self):
        if self.env == None:
            raise rendertemplateError('没有指定模板')
        if self.data == None:
            raise rendertemplateError('缺少模板参数')
        res = self.messageTemplate.render(self.data)
        return res

class rendertemplateError(Exception):
    message = None
    def __init__(self,message):
        self.message = message