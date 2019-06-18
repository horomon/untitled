from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from notifications.signals import notify

from Investions.models import InvestActive, Profile
from django.utils.translation import gettext_lazy as _


@login_required
def overview(request):
    context = {}
    context['actives']=InvestActive.objects.filter(user=request.user)
    return render(request, 'overview.html', context)


@login_required
def dismiss(request):
    contr_id = request.POST.get('contract')
    contr = InvestActive.objects.filter(id=contr_id).first()
    if contr.user == request.user:
        amount = contr.invested
        profile = Profile.objects.filter(user=request.user).first()
        profile.balance+=amount
        profile.save()
        contr.delete()
        notify.send(request.user, recipient=request.user, level='success',
                    verb=_('The contract was canseled.'))
    return redirect(reverse('overview'))


@login_required
def get_money(request):
    contr_id = request.POST.get('contract')
    contr = InvestActive.objects.filter(id=contr_id).first()
    if contr.user == request.user:
        if contr.is_finished:
            amount = contr.payouts
            profile = Profile.objects.filter(user=request.user).first()
            profile.balance += amount
            profile.save()
            contr.status = "payed"
            contr.save()
            notify.send(request.user, recipient=request.user, level='success',
                        verb=_('Congratulations, the contract payout was successful.'))
    return redirect(reverse('overview'))