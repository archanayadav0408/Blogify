from django import forms

from .models import Blog, Comment


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-4",
                "placeholder": "Enter username",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Enter password",
            }
        )
    )


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["title", "subtitle", "author", "content", "image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "subtitle": forms.TextInput(attrs={"class": "form-control"}),
            "author": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": "6"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["name", "comment"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your name"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Share your thoughts about this post",
                    "rows": "4",
                }
            ),
        }
