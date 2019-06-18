from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import user_username, user_email, setup_user_email
from allauth.utils import get_username_max_length, set_form_field_order
from django import forms
from allauth.account.forms import LoginForm, BaseSignupForm, ResetPasswordForm
from django.contrib.auth import get_user_model

from .models import InvestPlan, InvestActive, Profile
from untitled import settings

from django.utils.translation import gettext_lazy as _, pgettext


class PasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop('render_value',
                                  app_settings.PASSWORD_INPUT_RENDER_VALUE)
        kwargs['widget'] = forms.PasswordInput(render_value=render_value,
                                               attrs={'placeholder':
                                                      kwargs.get("label"),
                                                      'style': 'color:white'})
        super(PasswordField, self).__init__(*args, **kwargs)


class NewLognForm(LoginForm): # TODO change password menu

    password = PasswordField(label=_("Password"))
    remember = forms.BooleanField(label=_("Remember Me"),
                                  required=False,
                                  widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    user = None
    error_messages = {
        'account_inactive':
        _("This account is currently inactive."),

        'email_password_mismatch':
        _("The e-mail address and/or password you specified are not correct."),

        'username_password_mismatch':
        _("The username and/or password you specified are not correct."),
    }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)
        if settings.ACCOUNT_AUTHENTICATION_METHOD == 'email':
            login_widget = forms.TextInput(attrs={'type': 'email',
                                                  'placeholder':_('E-mail address'),
                                                  'autofocus': 'autofocus',
                                                  'style': 'color:white',
                                                  })
            login_field = forms.EmailField(label=_("E-mail"),
                                           widget=login_widget)
        elif settings.ACCOUNT_AUTHENTICATION_METHOD \
                == 'username':
            login_widget = forms.TextInput(attrs={'placeholder':
                                                  _('Username'),
                                                  'autofocus': 'autofocus',
                                                  'style': 'color:white'})
            login_field = forms.CharField(
                label=_("Username"),
                widget=login_widget,
                max_length=get_username_max_length())
        else:
            assert settings.ACCOUNT_AUTHENTICATION_METHOD \
                == 'username_email'
            login_widget = forms.TextInput(attrs={'placeholder':
                                                  _('Username or e-mail'),
                                                  'autofocus': 'autofocus',
                                                  'style': 'color:white'})
            login_field = forms.CharField(label=pgettext("field label",
                                                         "Login"),
                                          widget=login_widget)
        self.fields["login"] = login_field
        set_form_field_order(self, ["login", "password", "remember"])
        # if settings.ACCOUNT_SESSION_REMEMBER is not None:
        #     del self.fields['remember']


class SignupForm(BaseSignupForm):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'type': 'email',
               'placeholder': _('E-mail address'),
                'style': 'color:white',
               'autofocus': 'autofocus'}))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['password1'] = PasswordField(label=_("Password"))
        self.fields['password2'] = PasswordField(
            label=_("Confirm password"))

        if hasattr(self, 'field_order'):
            set_form_field_order(self, self.field_order)

    def clean(self):
        super(SignupForm, self).clean()

        # `password` cannot be of type `SetPasswordField`, as we don't
        # have a `User` yet. So, let's populate a dummy user to be used
        # for password validaton.
        dummy_user = get_user_model()
        user_email(dummy_user, self.cleaned_data.get("email"))
        password = self.cleaned_data.get('password1')
        if password:
            try:
                get_adapter().clean_password(
                    password,
                    user=dummy_user)
            except forms.ValidationError as e:
                self.add_error('password1', e)

        if "password1" in self.cleaned_data \
                and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] \
                    != self.cleaned_data["password2"]:
                self.add_error(
                    'password2',
                    _("The password and confirm password fields do not match."))
        return self.cleaned_data

    def save(self, request):
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class NewResetPasswordForm(ResetPasswordForm):
    email = forms.EmailField(
        label=_("E-mail"),
        required=True,
        widget=forms.TextInput(attrs={
            "type": "email",
            "size": "30",
            "placeholder": _("E-mail address"),
            'style': 'color:white'
        })
    )

class ContactForm (forms.Form):
    name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control text-white'}))
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'class':'form-control text-white'}))
    message = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class':'form-control  md-textarea'}), required=True)


# <<<<<<<<<<<<<<---------- STATIC PAGES FORMS --------->>>>>>>>>>>>>>>>

class CashInForm(forms.Form):
    amount = forms.FloatField(min_value=10,)


class FundsOutForm(forms.Form):
    _amount_widget = forms.NumberInput(attrs={'type': 'number',
                                             'class':'form-control text-white',
                                              'min': '100',
                                              'max': '2000',
                                              })
    amount = forms.IntegerField(label=_("USD"), widget=_amount_widget )
    _card_widget = forms.TextInput(attrs={'class': 'form-control text-white'})
    card = forms.CharField(max_length=128, label=_("Your Card Number or BTC wallet address"), widget=_card_widget)
    error_messages = {
        'not_enouth_money': _("Not enouth money"),

    }


class NewContractForm(forms.Form):
    plan = forms.ModelChoiceField(widget= forms.RadioSelect(attrs={'class':'form-check-input'}),queryset=InvestPlan.objects.filter(active=True).all(), initial=0, required=True)
    invested = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}))
