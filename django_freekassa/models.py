from django.core import validators
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from Investions.utils import rint
from django.utils.translation import gettext_lazy as _

#Модель пополнения


class Refill(models.Model):
    class Meta():
        db_table = 'refill'
        verbose_name = _("Refill")
        verbose_name_plural = _("Refills")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sum = models.FloatField(_('Amount'), default = 50.00)
    date = models.DateTimeField(_('Transact Date'), default=timezone.now)
    success = models.BooleanField(_('Success'), default=False)

    def __str__(self):
        return self.user.username


class FundsOutManager(models.Manager):
    def create_payout(self, person, amount, card_number, card_type, comment=''):
        pass

class FundsOut(models.Model):
    class Meta():
        db_table = 'withdrawal'
        verbose_name = _("Withdrawal")
        verbose_name_plural = _("Withdrawals")

    objects = FundsOutManager()
    STATUSES = (
        ('opened', _('Opened')),
        ('payed', _('Payed')),
        ('canceled', _('Canceled')),
        ('error', _('Error'))
    )
    CARD_TYPES = (
        ('visa','VISA'),
        ('btc','BTC'),
    )
    rid = models.IntegerField(primary_key=True,default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.TextField()
    amount = models.PositiveSmallIntegerField(default=10,
                                              validators=[validators.MaxValueValidator(5000, message=_(                                              "Invalid amount, allowed sum for transaction is 5000$"))])
    card_type = models.CharField(max_length=128,
                                 choices=CARD_TYPES,
                                 default=CARD_TYPES[0],
                                 )
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name=_('Created at:'),
                                   )
    status = models.CharField(max_length=128,
                              choices=STATUSES,
                              default=STATUSES[0],
                              verbose_name=_('Status'),
                              )
    comment = models.TextField(verbose_name=_('Comment'),
                               help_text=_('Explanation for the transaction'),
                               null=True)