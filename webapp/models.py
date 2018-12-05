from django.db import models
import math
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.text import Truncator
from django.db.models import Count
from django.utils.html import mark_safe
from markdown import markdown
# user :The User model is already defined inside a built-in app named auth, 
#which is listed in our INSTALLED_APPS 
#configuration under the namespace django.contrib.auth.
#----------------------------------------------
#what is models?
#The models are basically a representation of your application’s database layout.
#--------------------------------------------------
#All models(Board,Topic,Post) are subclass of the (django.db.models.Model class).
#Each class will be transformed into (database tables).
#-----------------------------------------------------
class Board(models.Model):
	name = models.CharField(max_length=200,unique=True)# unique=True:this parameter not allowed duplicate names
	description = models.CharField(max_length=4000)
	def __str__(self):
		return self.name

	def get_posts_count(self):
		return Post.objects.filter(topic__board=self).count()

	def get_last_post(self):
		return Post.objects.filter(topic__board=self).order_by('-create_at').first()
#Each (field) is represented by instances of (django.db.models.Field) 
#subclasses (built-in Django core) and will be translated into database columns.
#The fields CharField, DateTimeField, etc., are all subclasses of django.db.models.Field and 
#they come included in the Django core – ready to be used.

class Topic(models.Model):
	subject = models.CharField(max_length= 1000)
	last_update = models.DateTimeField(auto_now_add=True)
#this will instruct Django to set the current date and time (auto_now_add=True).
	board = models.ForeignKey(Board,related_name='topics',on_delete=models.CASCADE)
#To create a relationship between the models(Board to Topic to post) is by using the (ForeignKey field).
	starter = models.ForeignKey(User,related_name='topics',on_delete=models.CASCADE)
	views = models.PositiveIntegerField(default=0)
	def __str__(self):
		return self.subject
	def get_page_count(self):
		count = self.posts.count()
		pages = count / 20
		return math.ceil(pages)

	def has_many_pages(self, count=None):
		if count is None:
			count = self.get_page_count()
		return count > 6

	def get_page_range(self):
		count = self.get_page_count()
		if self.has_many_pages(count):
			return range(1, 5)
		return range(1, count + 1)
	def get_last_ten_posts(self):
		return self.posts.order_by('-created_at')[:10]
#Django automatically creates this reverse relationship – the(related_name) is optional. 
#But if we don’t set a name for it, Django will generate it with the name: (class_name)_set,for exanple(Board_set)
class Post(models.Model):
	message = models.TextField(max_length=4000)
	topic = models.ForeignKey(Topic,related_name='posts',on_delete=models.CASCADE)
	create_at = models.DateTimeField(auto_now_add=True)
	update_at = models.DateTimeField(null=True)
	created_by = models.ForeignKey(User,related_name='posts',on_delete=models.CASCADE)
	updated_by = models.ForeignKey(User,null=True,related_name='+',on_delete=models.CASCADE)
	def __str__(self):
		truncated_message = Truncator(self.message)
		return truncated_message.chars(30)

	def get_message_as_markdown(self):
		return mark_safe(markdown(self.message, safe_mode='escape'))
#the (related_name='+').This instructs Django that we don’t need this reverse relationship, 
#so it will ignore it.

#(after makemigaratios Django created a file named 0001_initial.py inside the boards/migrations directory.
#It represents the current state of our application’s models. In the next step, 
#Django will use this file to create the tables and columns.)
