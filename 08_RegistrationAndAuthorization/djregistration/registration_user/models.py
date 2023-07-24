from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    users = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name='users')
    phone_number = models.IntegerField(verbose_name="Номер телефона")
    verification_flag = models.BooleanField(default=False, verbose_name="Флаг верификации")
    superuser_flag = models.BooleanField(default=False, verbose_name="Флаг супер юзера")
    city = models.CharField(max_length=30, verbose_name="Город проживания")
    count_news = models.IntegerField(default=0, verbose_name="Количество опубликованных новостей")

    def __str__(self):
        return str(self.users)
