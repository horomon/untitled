from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render

from Investions.forms import ContactForm
from Investions.models import Contacts

from django.utils.translation import gettext_lazy as _


def page_contact(request):
    sent = False
    mailfrom = settings.EMAIL_HOST_USER
    mailto = [settings.EMAIL_HOST_USER]
    context = {}
    context['contacts'] = Contacts.objects.all()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            subject = 'Новое письмо от {}'.format(cd['name'])
            message = 'Прислал {}. Пишет: {}'.format(cd['email'], cd['message'])
            send_mail(subject, message, mailfrom, mailto)
            sent = True
            form = ContactForm()
            context['notification'] = _("The mail was sent successfuly! Thank you for contact. We will answer as soon, as possible.")
    else:
        form = ContactForm()
    context['form'] = form
    context['sent'] = sent
    return render(request, 'contact.html', context)