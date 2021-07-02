from sys import argv
import smtplib
from email.mime.text import MIMEText
from email.header import Header
#from models import LoginDB  
import os
 
# 第三方 SMTP 服务
mail_host="smtp.126.com"  #设置服务器
mail_user="liroding@126.com"    #用户名
mail_pass="RJPUJQLSEVZSLPJC"   #口令 liroding@126.com

#mail_user="dingyinglai@126.com"    #用户名
#mail_pass= "XKNRRKSAISFWOIDC"   #口令 dingyinglai@126.com
mail_postfix="126.com"




class MailHandleClass():
    def __init__(self,_SubjectArg,_ContentArg,_FromArg,_ToMesgArg,_ReceiversMailArg):
       self.subject = _SubjectArg
       self.content = _ContentArg
       self.message = MIMEText(self.content, 'plain', 'utf-8')
       self.message['Subject'] = Header(self.subject, 'utf-8')
       self.message['From'] = "liroding<liroding@126.com>"
       self.message['To'] =  _ReceiversMailArg
       #self.message['To'] =  "dingyinglai<dingyinglai@126.com>"
      
       AdminMailArg = "liroding@126.com"    
 
       self.sender = "liroding@126.com"
#       self.sender = "liroding@126.com"
       #receivers = ["liroding@126.com","LiroDing@zhaoxin.com"]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
       self.receivers = [_ReceiversMailArg,AdminMailArg] 
       #print(self.subject) 
    def AutoSendMail(self): 	 

       try:
           smtpObj = smtplib.SMTP()
           smtpObj.connect(mail_host,25)    # 25 为 SMTP 端口号
          # smtpObj = smtplib.SMTP_SSL(mail_host,465) #for SSL aliyun 
           smtpObj.set_debuglevel(1) 
           smtpObj.login(mail_user,mail_pass)  
           smtpObj.sendmail(self.sender,self.receivers, self.message.as_string())
           smtpObj.close()
           print( "success")
       except smtplib.SMTPException:
           print( "Error: ")
#Instance = MailHandleClass("zheshiyigeceshude","欢迎您的到来,希望您使用愉快~ "+"\r\n用户:" + "nihao" + "\r\n密码：" + "123456","11","34","liroding@zhaoxin.com")
#Instance.AutoSendMail()
