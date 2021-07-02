from django.contrib import admin
from .models import LoginDB
import builtins
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .AutoSendMail import MailHandleClass 

import json
#包装csrd 请求，避免django分为其实跨站攻击脚本
#from django.views.decorators.csrf import csrf_exempt
#from django.template.context_processors import csrf
# Register your models here.



class LoginHandleClass():
    def db_save(request):
        mail_is_null = 0  #0:null 1: no null
        mailstr = ""
        
       # id   = request.POST['id']
        has_regiter = 0
        user = request.POST['username']
        password = request.POST['password']
        mail = request.POST['mail']
        tmp = LoginDB()
        
        all_user = LoginDB.objects.all() 
        i = 0
        while i < len(all_user):
            
            if user in all_user[i].user:
                has_regiter = 1
               #print('has regiter!!!')
            i +=1

        if has_regiter == 0:
            tmp.user = user
            tmp.password = password
            tmp.mail = mail
            tmp.profilesetting = str(int(tmp.profilesetting)+ 1<<0) #mailflag = 1 otherflag = 1<<(10^n)
            tmp.save()
            ############### send mail functuon ###########
            if mail:
                 mail_is_null = 1
                 mailstr = mail
                 print("[serverlog] MailAddr: " + mailstr)
            else:
                 print("[serverlog] MailAddr: " + mailstr)
            if mail_is_null == 1:
                 #add by liro 2020/11/13
                 Instance = MailHandleClass("原生态实验室-工单系统注册成功通知","欢迎您的到来,希望您使用愉快~ "+"\r\n用户: " + user + "\r\n密码：" + password,"11","34",mailstr)
                 Instance.AutoSendMail()
            ############################################
            #storage to Django db
            User.objects.create_user(username=user,password=password)
            return HttpResponse("login success")           
        else :
            return HttpResponse("该账号存在")           
#return HttpResponseRedirect("/q")
        
    def db_query(request):
        user_true = 0
        pw_true = 0
        user = request.POST['user']
        password = request.POST['password']
        tmp = LoginDB()

        all_user = LoginDB.objects.all() 
        i = 0
        while i < len(all_user):
            
            if user == all_user[i].user:
                user_true = 1
                if password == all_user[i].password:
                    pw_true = 1
                    break
                else:
                    print('password error!!!')
                    break
            else:
                print('user name error !!!')
               #print('has regiter!!!')
            i +=1

        if (user_true == 1 and pw_true == 1):
            context = {}
            context['username'] = '用户:'+user
            #return HttpResponseRedirect(redirecturl)
            return HttpResponse("success")

        else :
            #return HttpResponse("登陆失败")           
            return HttpResponse("fail")           



    def index(request):
           return render(request,'login.html',{"username":"liroding"})

    def signin(request):
            return render(request,'signin.html',{"username":"liroding"})

    def register(request):
            return render(request,'register.html',{"username":"liroding"})


class MailNotifyClass():
    def notify(request):
        print('enter notify')
        #title = request.POST['title_result']
        #content = request.POST['content_result']
        #body = request.GET.get('title_result','11')
        #print(body)
        #body = request.POST.get('title_result','11')
        #print(body)
        body = request.body
        strdata = str(body,'utf-8')
        jsondata = json.loads(strdata)
        print(jsondata)
        title = jsondata['title_result']
        content = jsondata['content_result']
        statename = jsondata['last_flow_log']['state']['state_name']
        print('p1')
        creator = jsondata['ticket_value_info']['creator']
        print('p2')
        print(statename)
        to_user = jsondata['ticket_value_info']['to_user']
        print(to_user)
        #Search email address from mysql db 
        all_data = LoginDB.objects.all() 
        i = 0
        while i < len(all_data):
            print(all_data[i].user)
            if to_user in all_data[i].user:
          
                print('p3')
                mailstr = all_data[i].mail
                print("[serverlog] MailAddr: " + mailstr)
                if len(mailstr) > 0:
                    print('p4')
                    Instance = MailHandleClass(title,"您有一个工单待处理，请查看工单系统"+"\r\n网址: " + "http://10.32.64.101:9000" + "\r\n上一状态:" + statename +"\r\n表单创建者:"+ creator +"\r\n" + content,"xx","xx",mailstr)
                    print('p5')
                    Instance.AutoSendMail()
                else:
                    print("mail address is null")
            i +=1
        
        print('end notify')







