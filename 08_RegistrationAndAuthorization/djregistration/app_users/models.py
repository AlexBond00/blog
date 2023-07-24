from django.db import models


class News(models.Model):
    hedline_news = models.CharField(max_length=100, verbose_name='Заголовок новости')
    text_news = models.TextField(verbose_name="Текст новости")
    update_news = models.DateTimeField(auto_now=True)
    created_news = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey('News_status', on_delete=models.CASCADE, verbose_name='Статус новости')
    print_flag = models.BooleanField(default=False, verbose_name="Одобрить в печать")
    tag_news = models.CharField(max_length=100, verbose_name='Тег новости', null=True, blank=True)

    class Meta:
        ordering = ['-created_news']

    def __str__(self):
        return self.hedline_news


class News_status(models.Model):
    str_status = models.CharField(max_length=50, verbose_name='Статус новости')


    def __str__(self):
        return self.str_status


class Comment(models.Model):
    news_comment = models.ForeignKey('News', default=None, null=True, blank=True,
                                     on_delete=models.CASCADE, related_name='news_comment')
    text_comment = models.CharField(max_length=150, verbose_name='Текст комментария')
    name_commentator = models.CharField(max_length=50, verbose_name='Имя комментатора', null=True, blank=True)
    date_comment = models.DateTimeField(auto_now_add=True, verbose_name="Дата комментария")

    class Meta:
        ordering = ['-date_comment']

    def __str__(self):
        return self.text_comment