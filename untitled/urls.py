import notifications.urls
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path

from django_freekassa.views import res
from Investions import views
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path('merchant/result/', res)

      # path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
              ]  # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    url(r'^merchant/', include('django_freekassa.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),
    path('overlord/', admin.site.urls),
    path('account/', include('Investions.urls')),
    path('about/', views.page_about, name='about'),
    path('faq/', views.page_faq, name='faq'),
    path('terms/', views.page_rules, name='rules'),
    url('^notifications/', include(notifications.urls, namespace='notifications')),
    url(r"^referrals/", include("pinax.referrals.urls", namespace="pinax_referrals")),
    # path('news/', include(news_patterns, namespace='news')),
    path('contact/', views.page_contact, name='contact'),
    path('', views.index, name='index'),
)
