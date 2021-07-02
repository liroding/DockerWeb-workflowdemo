from django.urls import path
from LoginApp.Login import LoginHandleClass,MailNotifyClass


urlpatterns =[
      # request html page
      path('index',LoginHandleClass.index),
      path('signin',LoginHandleClass.signin),
      path('register',LoginHandleClass.register),

      # request handle function
      path('query',LoginHandleClass.db_query),
      path('save',LoginHandleClass.db_save),
      
      #send Email 
      path('sendmail',MailNotifyClass.notify),
]
 
