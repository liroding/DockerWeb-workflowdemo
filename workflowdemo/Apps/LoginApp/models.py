from django.db import models
import xadmin
# Create your models here.

class LoginDB(models.Model):
    user = models.CharField(max_length = 20)
    password = models.CharField(max_length = 20)
    mail = models.CharField(max_length = 20 ,default="")
    profilesetting = models.CharField(max_length = 8 ,default="0")

    def __str__(self):
        return 'name:'+self.user+','+self.password
#    class Meta:
#        verbose_name = "用户信息"
#        verbose_name_plural = verbose_name
