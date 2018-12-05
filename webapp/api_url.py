from django.conf.urls import url,include
from rest_framework import routers
from webapp.views import EmployeeViewset

router = routers.DefaultRouter()
router.register('employee/',EmployeeViewset),

urlpatterns = [
			url('employee/',include(router.urls)),

]