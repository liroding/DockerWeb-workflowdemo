from django.contrib import admin
from . models import LoginDB
import builtins
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
                 Instance = MailHandleClass("原生态实验室注册成功通知","欢迎您的到来,希望您使用愉快~ "+"\r\n用户:" + user + "\r\n密码：" + password,"11","34",mailstr)
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


