# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth, messages
from django import forms
from django.dispatch import receiver
from django.http import HttpResponse
from hashlib import sha256, md5
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, pgettext

from .models import Refill

# Страница купить
def buy(request):
    return render(request, 'templates/sys.html')

# Формирование запроса для оплаты
def popoln(request):
    if request.method == "POST":
        amount =  int(request.POST.get('amount'))
        if 5000 > amount > 0:
            mrh_login = "146760"
            mrh_pass1 = "8lcvqono"
            operation = Refill.objects.create(user=request.user, sum= amount)
            inv_id  = operation.id
            #Формирование контрольной суммы
            result_string = "{}:{}:{}:{}".format(mrh_login, amount, mrh_pass1, inv_id)
            sign_hash = md5()
            sign_hash.update(result_string.encode())
            crc = sign_hash.hexdigest()
            url = "http://www.free-kassa.ru/merchant/cash.php?m={}&oa={}&o={}&s={}".format(mrh_login, amount, inv_id, crc)

            #К примеру запись в талицу пополнения

            #Переход на страницу оплаты в робокасса
            return redirect(url)
    return render(request, 'cash_in.html')

#Проверка плотежа
@csrf_exempt
def res(request):
    if not request.method == 'POST':
        return HttpResponse('error')
    mrh_pass2 = "qxdf2iuw"
    #Проверка заголовка авторизации
    if request.method == 'POST':
        out_summ = request.POST['OutSum']
        inv_id = request.POST['InvId']
        crc = request.POST['SignatureValue']
        crc = crc.upper()
        crc = str(crc)
        #Формирование своей контрольной суммы
        result_string = "{}:{}:{}".format(out_summ, inv_id, mrh_pass2)
        sign_hash = sha256(result_string.encode())
        my_crc = sign_hash.hexdigest().upper()
        #Проверка сумм
        if my_crc not in crc:
            # Ответ ошибки
            context = "bad sign"
            return HttpResponse(context)
        else:
            #Ответ все верно
            context = "OK{}".format(inv_id)
            return HttpResponse(context)

#Платеж принят
@csrf_exempt
def success(request):
    if not request.method == 'POST':
        return HttpResponse('error')
    mrh_pass1 = "Ваш пароль 1"
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
            context = "bad sign"
            return HttpResponse(context)
        else:
            #Показ страницы успешной оплаты
            return render(request, 'templates/success.html')

#Платеж не принят
@csrf_exempt
def fail(request):
    if request.method == "POST":
        return render(request, 'templates/fail.html')
