from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import datetime

from django.urls import reverse
from notifications.signals import notify
from pinax.referrals.models import Referral

from django_freekassa.models import FundsOut
from Investions.models import InvestPlan, Profile, InvestActive
from Investions.forms import FundsOutForm, NewContractForm
from Investions.utils import rhex, rint

from django.utils.translation import gettext_lazy as _



def index(request):
    context = {}
    plans = InvestPlan.objects.filter(active=True).order_by('period')
    context['plans'] = plans
    return render(request, 'index.html', context)

@login_required
def user_settings(request):
    context = {}
    return render(request, 'settings.html', context)


def page_about(request):
    context = {}
    return render(request, 'about.html', context)


def page_faq(request):
    context = {}
    return render(request, 'faq.html', context)


def page_rules(request):
    context = {}
    return render(request, 'rules.html', context)


@login_required
def page_new_contract(request):
    context = {}
    if request.method == 'POST':
        form = NewContractForm(request.POST)
        if form.is_valid():
            cd  = form.cleaned_data
            prof = Profile.objects.get(user=request.user)
            inv = float(cd['invested'])
            if prof.balance >= inv:
                act = InvestActive.objects.create_active(
                    user=request.user,
                    plan=cd['plan'],
                    invested=cd['invested']
                )
                prof.balance-=inv
                prof.save()
                notify.send(request.user, recipient=request.user, level='success', verb=_('Congratulations! The contract created successfuly!'))
                return redirect(reverse('overview'))
            else:
                context['form'] = form
                form.add_error(field=None, error=_("Not enouth money"))
        else:
            form = NewContractForm()
            context['form'] = form
    else:
        form = NewContractForm()
        context['form']=form
    return render(request, 'new_contract.html', context)


@login_required
def page_cash_out(request): # TODO payout list and statuses
    context = {}
    if request.method == 'POST':
        form = FundsOutForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cashout = FundsOut.objects.create(
                user=request.user,
                amount=cd['amount'],
                card_number=cd['card']
            )
            notify.send(request.user, recipient=request.user, level='success', verb=_('Withdrawal request successfuly created. Payout will be done during one banking day.'))
            return redirect(reverse('overview'))
    else:
        form = FundsOutForm()
        context['form'] = form
    return render(request, 'cash_out.html', context)


@login_required
def page_referal(request):
    context = {}
    reff = Referral.objects.get_or_create(user=request.user, redirect_to=reverse('index'))[0]
    profile = Profile.objects.get(user=request.user)
    profile.referral = reff
    profile.save()
    context['reff'] = reff
    return render(request, 'referal.html', context)


@login_required
def page_history(request):
    context = {}
    actives = InvestActive.objects.filter(user=request.user)
    context['actives'] = actives
    return render(request, 'history.html', context)