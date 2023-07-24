from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from .forms import CommentForm
from .models import News
from django.forms import HiddenInput


def home_page(request, *args, **kwargs):
    """"функция главной страницы"""
    if not request.user.is_authenticated:
        verification_flag = False
        superuser_flag = False
    else:
        verification_flag = request.user.users.verification_flag
        superuser_flag = request.user.users.superuser_flag
    return render(request, 'news/home_page.html', {'verification_flag': verification_flag,
                                                   'superuser_flag': superuser_flag})



class NewsListView(ListView):
    """класс создает список новостей. Реализована сортировка по дате и тегу"""
    model = News
    template_name = 'news/news_list.html'


    def get_queryset(self):
        ordering = self.request.GET.get('orderby')
        queryset = self.queryset

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()

        if ordering:
            if ordering not in ['created_news', '-created_news']:
                queryset = News.objects.filter(tag_news=ordering)
                ordering = 'tag_news'
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset


class NewsDetailView(DetailView, FormMixin):
    """класс детализирует новость. Реализована возможность добавления комментариев к новости"""
    model = News
    template_name = 'news/news_detail.html'
    form_class_user = CommentForm

    def get_success_url(self, **kwargs):
        self.success_url = f'/app_users/news_detail/{self.get_object().id}'
        return str(self.success_url)

    def get_form(self, form_class=form_class_user):
        form = super().get_form(form_class)
        if self.request.user.is_authenticated:
            form.fields['name_commentator'].widget = HiddenInput()
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        user_form_news = form.save(commit=False)
        user_form_news.news_comment = self.get_object()
        if self.request.user.is_authenticated:
            user_form_news.name_commentator = self.request.user
        else:
            user_form_news.name_commentator = f"Аноним {self.request.POST['name_commentator']}"
        user_form_news.save()
        return super().form_valid(form)


class NewsCreateView(PermissionRequiredMixin, CreateView):
    """ класс добавления новости. В классе реализован счетчик новостей"""
    model = News
    template_name = 'news/create_news.html'
    fields = '__all__'

    def has_permission(self):
        return self.request.user.users.verification_flag

    def get_success_url(self, **kwargs):
        self.success_url = '/app_users/create_news'
        return str(self.success_url)


class NewsUpdateView(PermissionRequiredMixin, UpdateView):
    """класс редактирования новости"""
    model = News
    template_name = 'news/update_news.html'
    fields = '__all__'

    def has_permission(self):
        return self.request.user.users.verification_flag

    def get_success_url(self, **kwargs):
        self.success_url = '/app_users/news_list'
        return str(self.success_url)