from django.conf.urls import url
from django_freekassa import views

urlpatterns = [
	url(r'^result/$', views.res, name='buy'),
	url(r'^refill_req/$', views.refill_req, name='refill_req'),
	url(r'^success/$', views.success, name='success'),
	url(r'^fail/$', views.fail, name='fail'),
]
