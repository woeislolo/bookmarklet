from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.postgres.search import SearchVector
from django.db.models import Count
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView, TemplateView, UpdateView
from django.views.decorators.http import require_POST

from .forms import *


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'account/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context

    def get_success_url(self):
        return reverse_lazy('dashboard')


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    return render(request,
    'account/dashboard.html',
    {'section': 'dashboard'})

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'account/register.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(user=user)
        login(self.request, user)
        messages.success(self.request, 'Вы успешно зарегистрировались.')
        return redirect('dashboard')
    

class UserProfile(DetailView):
    template_name = 'account/profile.html'
    context_object_name = 'user_profile'

    def get_object(self):
        user_pk = User.objects.filter(pk=self.kwargs['user_pk'])[0].pk
        profile = Profile.objects.filter(user_id=user_pk).select_related('user').get()
        return profile
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_object().user.username
        return context


class UpdateUserProfile(UpdateView):
    template_name = 'account/profile_update.html'
    context_object_name = 'user_profile'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('home')

    def get_object(self):
        user_pk = User.objects.filter(pk=self.kwargs['user_pk'])[0].pk
        profile = Profile.objects.filter(user_id=user_pk).select_related('user').get()
        return profile

    def get_context_data(self, **kwargs):
        context = super(UpdateUserProfile, self).get_context_data(**kwargs)
        user = self.request.user
        context['profile_form'] = ProfileUpdateForm(
            instance=self.request.user.profile,
            initial={'first_name': user.first_name, 
                     'last_name': user.last_name}
            )
        context['title'] = self.get_object().user.username
        return context

    def form_valid(self, form):
        profile = form.save()
        user = profile.user
        user.last_name = form.cleaned_data['last_name']
        user.first_name = form.cleaned_data['first_name']
        user.save()
        messages.success(self.request, 'Профиль успешно изменен.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Возникла ошибка при редактировании профиля.')
        return self.render_to_response(self.get_context_data(form=form))
