from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .forms import *
from actions.utils import create_action
from actions.models import Action
from .tasks import *


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
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',
                                                       flat=True)
    if following_ids:
        actions = actions.filter(user_id__in=following_ids)
        # если есть подписки на кого-то, то получаем их действия
    actions = actions.select_related('user', 'user__profile')[:10].prefetch_related('target')[:10]
    return render(request=request,
                  template_name='account/dashboard.html',
                  context={'section': 'dashboard',
                           'actions': actions,})


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
        create_action(user, 'создал аккаунт')

        subject = 'Registration'
        task_send_email.delay_on_commit(user.pk, subject=subject)

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
    success_url = reverse_lazy('dashboard')

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

        subject = "Profile's update"
        task_send_email.delay_on_commit(user.pk, subject=subject)

        messages.success(self.request, 'Профиль успешно изменен.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Возникла ошибка при редактировании профиля.')
        return self.render_to_response(self.get_context_data(form=form))


class UserListView(LoginRequiredMixin, ListView):
    queryset= User.objects.filter(is_active=True)
    context_object_name = 'users'
    template_name = 'account/user/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'people'
        return context


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'account/user/detail.html'

    def get_object(self):
        user = get_object_or_404(klass=User,
                                username=self.kwargs['username'],
                                is_active=True)
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'people'
        return context


@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    # почему-то могу подписаться сама на себя)
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user)
                create_action(request.user, 'подписался на', user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
