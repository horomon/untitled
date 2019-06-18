# -*- coding: utf-8 -*-
from notifications.signals import notify
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth, messages
from django import forms
from django.conf import settings
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseRedirect
from hashlib import sha256, md5
from django.utils.translation import gettext_lazy as _, pgettext

from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# Страница купить
from Investions.models import Profile
from django_freekassa.models import Refill


def buy(request):
    return render(request, 'sys.html')

# Формирование запроса для оплаты
def refill_req(request): # TODO convert USD to RUB if freekassa RUB
    if request.method == "POST":
        oa = int(request.POST.get('oa'))
        m = getattr(settings, "FREEKASSA_ID", None)
        pass1 = getattr(settings, "FREEKASSA_SECRET_1", None)
        operation = Refill.objects.create(user=request.user, sum=oa)
        o  = operation.id
        #Формирование контрольной суммы
        result_string = "{}:{}:{}:{}".format(m, oa, pass1, o)
        sign_hash = md5(result_string.encode())
        crc = sign_hash.hexdigest()
        url = "https://www.free-kassa.ru/merchant/cash.php?m={}&oa={}&o={}&s={}&i={}".format(m, oa, o, crc, 115)
        return redirect(url)
    return render(request, 'cash_in.html', )


#Проверка плотежа
@csrf_exempt
def res(request):
    if not request.method == 'POST':
        return HttpResponse('error')
    mrh_pass2 = getattr(settings, "FREEKASSA_SECRET_2", None)
    #Проверка заголовка авторизации
    if request.method == 'POST':
        merchant = request.POST['MERCHANT_ID']
        out_summ = request.POST['AMOUNT']
        inv_id = request.POST['MERCHANT_ORDER_ID']
        crc = request.POST['SIGN']
        crc = crc.upper()
        crc = str(crc)
        #Формирование своей контрольной суммы
        result_string = "{}:{}:{}:{}".format(merchant, out_summ, mrh_pass2, inv_id)
        sign_hash = md5(result_string.encode())
        my_crc = sign_hash.hexdigest().upper()
        #Проверка сумм
        if my_crc not in crc:
            # Ответ ошибки
            context = "bad sign"
            return HttpResponse(context)
        else:
            operation = Refill.objects.get(id=inv_id)
            prof = Profile.objects.get(user=operation.user)
            prof.balance+= operation.sum
            prof.save()
            operation.success = True #TODO add referrals percent
            operation.save()
            context = "OK{}".format(inv_id)
            return HttpResponse(context)

#Платеж принят
@csrf_exempt
def success(request):
    if not request.method == 'POST':
        return HttpResponse('error')
    mrh_pass1 =  getattr(settings, "FREEKASSA_SECRET_1", None)
    #Проверка заголовка авторизации
    if request.method == 'POST':
        out_summ = request.POST['OutSum']
        inv_id = request.POST['InvId']
        crc = request.POST['SignatureValue']
        crc = crc.upper()
        crc = str(crc)
        #Формирование своей контрольной суммы
        result_string = "{}:{}:{}".format(out_summ, inv_id, mrh_pass1)
        sign_hash = sha256(result_string.encode())
        my_crc = sign_hash.hexdigest().upper()
        #Проверка сумм
        if my_crc not in crc:
            #Ошибка
            notify.send(request.user, recipient=request.user, level='error', verb=_("Bad sign token, please contact the support if you don't got the money"))
            return HttpResponseRedirect(reverse('overview'))
        else:
            notify.send(request.user, recipient=request.user, level='success', verb=_("Congratulation! The payment was successful."))
            return HttpResponseRedirect(reverse('overview'))

#Платеж не принят
@csrf_exempt
def fail(request):
    if request.method == "POST":
        notify.send(request.user, recipient=request.user, level='error', verb=_("The payment unsuccessful, please try again, or contact the support."))
        return HttpResponseRedirect(reverse('overview'))
