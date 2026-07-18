from django import forms
from .models import Post
from tinymce.widgets import TinyMCE
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "category", "short_description", "image", "content"]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400 focus:outline-none",
                    "placeholder": "Enter title...",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400 focus:outline-none bg-white"
                }
            ),
            "short_description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400 focus:outline-none",
                    "rows": 3,
                    "placeholder": "Short description...",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400",
                }
            ),
        }
