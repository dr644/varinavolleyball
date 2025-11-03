from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    link_url = forms.CharField(required=False)   # 👈 override to text input
    video_url = forms.CharField(required=False)  # 👈 same idea if you want

    class Meta:
        model = Post
        fields = ['title', 'content', 'post_type', 'image', 'video_url', 'link_url']

    def clean_link_url(self):
        url = self.cleaned_data.get('link_url', '').strip()
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

    def clean_video_url(self):
        url = self.cleaned_data.get('video_url', '').strip()
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a comment...'}),
        }
