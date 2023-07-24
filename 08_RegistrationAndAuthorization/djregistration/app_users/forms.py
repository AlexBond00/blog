from django.forms import ModelForm
from .models import News, Comment

class NewsForm(ModelForm):
    class Meta:
        model = News
        fields = '__all__'


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('name_commentator', 'text_comment', )