from django.contrib import admin
from .models import *
# Register your models here.


class Board_Admin(admin.ModelAdmin):
	list_display = ['id','name','description']
admin.site.register(Board,Board_Admin)

class Topic_Admin(admin.ModelAdmin):
	list_display=['id','subject','last_update','board','starter']
admin.site.register(Topic,Topic_Admin)

class Post_Admin(admin.ModelAdmin):
	list_display=['id','message','topic','create_at','update_at','created_by','updated_by']
admin.site.register(Post,Post_Admin)

