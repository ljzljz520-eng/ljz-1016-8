"""根路由：登录 / 登出 / 验证码 / 告警概览 / Django admin"""
from django.contrib import admin
from django.urls import include, path

from apps.accounts import views as account_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", account_views.login_view, name="login"),
    path("logout/", account_views.logout_view, name="logout"),
    path("captcha/", account_views.captcha_image, name="captcha-image"),
    path("", include("apps.alarms.urls")),
]
