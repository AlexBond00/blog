from config.settings import RECIPIENTS_EMAIL, DEFAULT_FROM_EMAIL
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.mail import send_mail
from django.http import HttpResponse, BadHeaderError
from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView
from .forms import SignupForm, ProfileForm, UserEditForm, ContactForm
from .models import Profile


class RegistrationLoginView(LoginView):
    """ класс регистрации пользователя """
    template_name = "news/registration.html"


class RegistrationLogOutView(LogoutView):
    """ класс регистрации пользователя """
    template_name = "news/registration_logout.html"


def ok_login(request, *args, **kwargs):
    """ функция успешная регистрация пользователя """
    return render(request, 'news/ok_login.html')


def registration_logout(request, *args, **kwargs):
    """ функция выхода пользователя """
    return render(request, 'news/registration_logout.html')


def signup_view(request):
    """ класс для регистрации пользователя """
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            city = form.cleaned_data['city']
            phone_number = form.cleaned_data['phone_number']
            Profile.objects.create(
                users=new_user,
                phone_number=phone_number,
                city=city
            )
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return render(request, 'news/ok_login.html', {'user_form': new_user})
    else:
        user_form = SignupForm()
        return render(request, 'news/signup.html', {'user_form': user_form})


class UserListView(PermissionRequiredMixin, ListView):
    """ класс просмотра списка пользователей """
    model = User
    template_name = 'news/profile_list.html'
    permission_required = 'request.user.users.verification_flag'


class UserUpdateView(PermissionRequiredMixin, UpdateView):
    """ класс редактирования данных пользователей """
    model = User
    form_class = UserEditForm
    second_form_class = ProfileForm
    template_name = 'news/update_user.html'
    permission_required = 'request.user.users.superuser_flag'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_profile = User.objects.get(username=self.object)
        profile = Profile.objects.get(users_id=user_profile.id)
        user_form = self.form_class(instance=user_profile)
        profile_form = self.second_form_class(instance=profile)
        user_verification_flag = Profile.objects.get(users_id=request.user.id)
        user_superuser_flag = Profile.objects.get(users_id=request.user.id).superuser_flag
        return self.render_to_response(self.get_context_data(object=self.object,
                                                             user_form=user_form, profile_form=profile_form,
                                                             user_verification_flag=user_verification_flag,
                                                             user_superuser_flag=user_superuser_flag))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_profile = User.objects.get(username=self.object)
        profile = Profile.objects.get(users_id=user_profile.id)
        user_form = UserEditForm(request.POST, instance=user_profile)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            if profile_form.cleaned_data.get('superuser_flag'):
                profile.superuser_flag = True
                profile.verification_flag = True
            user_profile.save()
            profile.save()
            return redirect('profile_list')
        else:
            no_valid = "Проблемы с заполнением формы"
            user_verification_flag = Profile.objects.get(users_id=request.user.id)
            user_superuser_flag = Profile.objects.get(users_id=request.user.id).superuser_flag
            return self.render_to_response(self.get_context_data(object=self.object,
                                                          user_form=user_form, profile_form=profile_form,
                                                          user_verification_flag=user_verification_flag,
                                                          user_superuser_flag=user_superuser_flag, no_valid=no_valid))

    def get_success_url(self, **kwargs):
        self.success_url = '/profile_list'
        return str(self.success_url)


class SearchResultView(ListView):
    """
    Реализация поиска статей на сайте
    """
    model = Profile
    context_object_name = 'profile'
    paginate_by = 10
    allow_empty = True
    template_name = 'news/articles_list.html'

    def get_queryset(self):
        query = self.request.GET.get('do')
        search_vector = SearchVector('full_description', weight='B') + SearchVector('title', weight='A')
        search_query = SearchQuery(query)
        return (self.model.objects.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank'))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Результаты поиска: {self.request.GET.get("do")}'
        return context


def contact_view(request):
    # если метод GET, вернем форму
    if request.method == 'GET':
        form = ContactForm()
    elif request.method == 'POST':
        # если метод POST, проверим форму и отправим письмо
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(f'{subject} от {from_email}', message,
                          DEFAULT_FROM_EMAIL, RECIPIENTS_EMAIL)
            except BadHeaderError:
                return HttpResponse('Ошибка в теме письма.')
            return redirect('success')
    else:
        return HttpResponse('Неверный запрос.')
    return render(request, "email.html", {'form': form})

def success_view(request):
    return HttpResponse('Приняли! Спасибо за вашу заявку.')