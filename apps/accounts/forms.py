from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """带可选图形验证码的登录表单（连续失败后必填）。"""

    captcha = forms.CharField(
        required=False,
        max_length=8,
        widget=forms.TextInput(attrs={
            "class": "input",
            "placeholder": "请输入图中验证码",
            "autocomplete": "off",
        }),
    )

    def __init__(self, *args, captcha_required=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "input",
            "placeholder": "账号",
            "autocomplete": "username",
        })
        self.fields["password"].widget.attrs.update({
            "class": "input",
            "placeholder": "密码",
            "autocomplete": "current-password",
        })
        self.captcha_required = captcha_required

    def clean_captcha(self):
        value = (self.cleaned_data.get("captcha") or "").strip().upper()
        if self.captcha_required and not value:
            raise forms.ValidationError("请输入验证码")
        return value
