from django.urls import path
from LoginApp.Login import LoginHandleClass


urlpatterns =[
      # request html page
      path('admin',LoginHandleClass.admin),
      path('signin',LoginHandleClass.signin),
      path('register',LoginHandleClass.register),

      # request handle function
      path('query',LoginHandleClass.db_query),
      path('save',LoginHandleClass.db_save),
]
 
