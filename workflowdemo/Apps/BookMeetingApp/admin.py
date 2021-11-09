from django.contrib import admin
from . models import Room,Book 
# Register your models here.



#admin.site.register(models.Room,RoomConfig)
#admin.site.register(models.Book,BookConfig)
admin.site.register(Room)
admin.site.register(Book)
