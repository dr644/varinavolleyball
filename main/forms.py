from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, WorkoutLog
import random

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share something...'})
        }


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = WorkoutLog
        fields = ['workout_type', 'notes']

ROLE_CHOICES = [("supporter", "Supporter"), ("alumni", "Alumni")]


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name  = forms.CharField(max_length=30, required=True)
    email      = forms.EmailField(required=True)
    role       = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    password   = forms.CharField(widget=forms.PasswordInput)

    # CAPTCHA fields
    math_question = forms.CharField(label="Math Question", required=False, disabled=True)
    math_answer   = forms.IntegerField(label="Your Answer", required=True)

    class Meta:
        model  = User
        fields = ["first_name", "last_name", "email", "password"]

    def __init__(self, *args, **kwargs):
        # capture request so we can use the session
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        if self.request:
            # If we don't have a question yet (fresh GET), generate one
            if (
                self.request.method == "GET"
                or "captcha_sum" not in self.request.session
                or "captcha_text" not in self.request.session
            ):
                a, b = random.randint(1, 9), random.randint(1, 9)
                self.request.session["captcha_sum"]  = a + b
                self.request.session["captcha_text"] = f"What is {a} + {b}?"

            # Always show the SAME question during POST retries
            self.fields["math_question"].initial = self.request.session.get(
                "captcha_text", "Solve the sum."
            )

    # ✅ Email validation (shows "Enter a valid email address" or duplicate message)
    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Let Django's built-in email validator handle malformed input automatically
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    # ✅ CAPTCHA validation
    def clean(self):
        cleaned = super().clean()
        if not self.request:
            return cleaned

        expected = self.request.session.get("captcha_sum")
        given    = cleaned.get("math_answer")

        if expected is None:
            raise forms.ValidationError("Verification expired. Please reload and try again.")

        if str(given) != str(expected):
            # keep the same question for the next render
            raise forms.ValidationError("Incorrect answer to the math question. Please try again.")

        return cleaned