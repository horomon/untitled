import pytz
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from django.db import models
from decimal import Decimal
import datetime

from django.utils.translation import gettext_lazy as _
from pinax.referrals.models import Referral

from Investions.utils import rhex


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    balance = models.FloatField(verbose_name=_('User balance'), default=0)
    wallet = models.CharField(verbose_name=_('Crypto Wallet'), max_length=255, blank=True)
    email_is_verified = models.BooleanField(default=False, verbose_name=_(u'Email верифицирован'))
    referral = models.OneToOneField(Referral, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "{}'s profile".format(self.user.username)

    class Meta:
        db_table = 'user_profile'

    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def lock_money(self, amount):
        self.balance-=amount


User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])


# class InvestPlanManager(models.Manager):
#     def create_plan(self, name, min, max, period, rate, active):
#         period = datetime.timedelta(days=period)
#         plan = self.create(
#             plan_name=name,
#             min_lim =min,
#             max_lim =max,
#             period =period,
#             rate =rate,
#             active =active,
#         )
#         return plan


class InvestPlan(models.Model):

    # objects = InvestPlanManager()

    plan_name = models.CharField(
        verbose_name=_("Plan Name"),
        max_length=255
    )
    min_lim = models.IntegerField(
        verbose_name=_('Minimal Investition'),
    )
    max_lim = models.IntegerField(
        verbose_name=_('Maximal Investition Limit'),
    )
    period = models.PositiveSmallIntegerField(
        verbose_name=_("Period"),
        help_text=_('Investition period in days'),
    )
    rate = models.FloatField(
        verbose_name=_('Daily Rate'),
    )
    active = models.BooleanField(verbose_name=_('Is Active?'),
                                 default=False,
                                 help_text=_('Plan visibility for new investitions')
                                )

    def __str__(self):
        return self.plan_name

    class Meta:
        verbose_name = _('Investition Plan')
        verbose_name_plural = _('Investition Plans')

    @property
    def rate_int(self):
        raint = int(self.rate)
        return raint

    @property
    def rate_month_int(self):
        raint = int(self.rate * 30)
        return raint

    @property
    def payout_index(self):
        return self.rate*self.period/100

    @property
    def present(self):
        return datetime.datetime.now() + datetime.timedelta(days=self.period)

# create/save/delete and other
class InvestActiveManager(models.Manager):
    def create_active(self, user, plan, invested):
        ghid = rhex(8)
        while InvestActive.objects.filter(ghid=ghid).exists():
            ghid = rhex(8)
        active = self.create(
                    ghid=ghid,
                    user=user,
                    plan=plan,
                    invested=invested,
                    start_date=datetime.datetime.now(),
                    status='open'
                )
        return active

class InvestActive(models.Model):
    ghid = models.CharField(max_length=10,
                           unique=True,
                            default='x'
                          )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User')
    )
    plan = models.ForeignKey(
        InvestPlan,
        related_name='associated_active',
        on_delete=models.PROTECT,
        verbose_name=_('Investition Plan')
    )
    start_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Start Date'))
    invested = models.FloatField(verbose_name=_('Invested'))
    status = models.CharField(max_length=255, verbose_name=_('Status'))

    objects = InvestActiveManager()

    def __str__(self):
        return "Active: %s (%s)" %(self.user.username, self.plan.plan_name)

    class Meta:
        verbose_name = _('Investition Active')
        verbose_name_plural = _('Investition Actives')
        indexes = [models.Index(fields=['ghid'])]

    @property
    def payouts(self):
        return round(self.invested+(self.invested*self.plan.payout_index), 2)

    @property
    def end_date(self):
        return self.start_date + datetime.timedelta(days=self.plan.period)

    @property
    def end_date_js(self):
        d = self.end_date
        return d.strftime('%Y/%m/%d %H:%M')

    @property
    def is_finished(self):
        utc = pytz.timezone('UTC')
        e_date = self.end_date.replace(tzinfo=None)
        now_date = utc.localize(datetime.datetime.utcnow()).replace(tzinfo=None)
        if now_date >= e_date:
            return True
        else: return False

    @property
    def percent_stat(self):
        period_timedelta = datetime.timedelta(days=self.plan.period)
        delta = self.end_date - datetime.datetime.now(datetime.timezone.utc)
        result = (period_timedelta - delta)*100/period_timedelta
        return round(result, 2)


class Contacts(models.Model):
    class Meta:
        verbose_name=_("Site Contact")
        verbose_name_plural= _('Site Contacts')

    def __str__(self):
        return "{}:{}".format(self.element, self.data)

    ELEMENTS = (
        ('fas fa-phone',_('Phone')),
        ('fas fa-map-marked-alt',_('Address')),
        ('fab fa-telegram', _('Telegram')),
        ('fab fa-whatsapp', _('WhatsApp')),
        ('fab fa-viber', _('Viber')),
        ('fab fa-facebook-f', _('Facebook')),
        ('fas fa-at', _('E-mail')),
        ('fab fa-vk', _('Vk.com')),
        # ('btc', _('BTC')),
    )
    element = models.CharField(choices=ELEMENTS,
                               max_length=32,
                               default=ELEMENTS[0],
                               verbose_name=_('Contact type'),
                               )
    data = models.CharField(max_length=255,
                            null=True,
                            verbose_name=_('Contact Data')
                            )
