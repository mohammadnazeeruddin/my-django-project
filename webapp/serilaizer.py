from rest_framework import serializers
from django.contrib.auth.models import User
from webapp.models import Board




class EmployeeSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Board
		fields = ('name','description')
		





