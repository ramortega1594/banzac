"""Transacciones views."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, View
from django.urls import reverse_lazy, reverse

# Models 
from transacciones.models import Transaccion
from users.models import Profile
from django.contrib.auth.models import User

# Forms
from transacciones.forms import DepositoForm, RetiroForm

class SolicitarSaldoView(ListView, LoginRequiredMixin):
    model = Profile
    template_name = 'transacciones/saldo.html'

class TransactionCreate(LoginRequiredMixin, CreateView):
    model = Transaccion
    success_url = reverse_lazy('transaccion:retiro')
    form_class = RetiroForm

class RetiroView(LoginRequiredMixin, View):
    form_class = RetiroForm
    template_name = 'transacciones/retiro.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        saldo_transaccion = Profile.objects.filter(id = request.user.profile.id).latest('created')
        saldo = saldo_transaccion.saldo
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            retiro = float(request.POST['retiro'])
            if saldo - retiro >= 0:
                saldo = saldo - retiro
            
                transaccion = Transaccion(transferencia=0, retiro=retiro, user_id = request.user.id)
                transaccion.save()

                profile = Profile.objects.get(user = request.user)
                profile.saldo = saldo
                profile.save()

            else:
                saldo = saldo
                return render(request, 'transacciones/retiro.html', { 'error': 'Saldo insuficiente' })
        else:
            form = DepositoForm()
        return render(request, 'transacciones/deposito.html', {'form': form})

@login_required
def retiro(request):
    """ Agregamos Retiro """
    saldo_transaccion = Profile.objects.filter(id = request.user.profile.id).latest('created')
    saldo = saldo_transaccion.saldo

    if request.method == 'POST':
        form = RetiroForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            retiro = float(request.POST['retiro'])
            if saldo - retiro >= 0:
                saldo = saldo - retiro
            
                transaccion = Transaccion(transferencia=0, retiro=retiro, user_id = request.user.id)
                transaccion.save()

                profile = Profile.objects.get(user = request.user)
                profile.saldo = saldo
                profile.save()

            else:
                saldo = saldo
                return render(request, 'transacciones/retiro.html', { 'error': 'Saldo insuficiente' })

    else:
        form = RetiroForm()

    return render(
        request=request, 
        template_name = 'transacciones/retiro.html',
        context = {
            'form' : form
        }
    )

@login_required
def deposito(request):
    """Agregamos deposito""" 

    saldo_transaccion = Profile.objects.filter(id = request.user.profile.id).latest('created')
    saldo = saldo_transaccion.saldo

    if request.method == 'POST':
        form = DepositoForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            deposito = float(request.POST['deposito'])
            saldo = saldo + deposito

            transaccion = Transaccion(transferencia=deposito, retiro=0, user_id = request.user.id)
            transaccion.save()

            profile = Profile.objects.get(user = request.user)
            profile.saldo = saldo
            profile.save()
    else:
        form = DepositoForm()

    return render(
        request=request,
        template_name='transacciones/deposito.html',
        context={
            'form': form
        }
    )

class CajeroPrincipal(LoginRequiredMixin, TemplateView):
    """Cajero Principal View"""

    template_name = 'transacciones/base.html'

