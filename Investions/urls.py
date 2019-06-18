from django.urls import path, include
from Investions import views
from django_freekassa.views import refill_req

urlpatterns = [
    path('', views.overview),
    path('overview/', views.overview, name='overview'),
    path('referals/', views.page_referal, name='referals'),
    # path('settings/', views.user_settings, name='settings'),
    path('cash_in/', refill_req, name='cash_in'),
    path('cash_out/', views.page_cash_out, name='cash_out'),
    path('new_contract/', views.page_new_contract, name='new_contract'),
    path('history/', views.page_history, name='history'),
    path('dismiss/', views.dismiss, name='dismiss'),
    path('get_money/', views.get_money, name='get_money'),
]