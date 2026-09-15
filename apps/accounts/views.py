import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .captcha import generate_captcha_code, generate_captcha_image
from .forms import LoginForm

SESSION_FAILURES = "login_failures"
SESSION_CAPTCHA_CODE = "captcha_code"
SESSION_CAPTCHA_TS = "captcha_ts"


def _captcha_required(request):
    """连续错误达到阈值后要求验证码。"""
    failures = request.session.get(SESSION_FAILURES, 0)
    return failures >= settings.ACCOUNTS_MAX_LOGIN_FAILURES


def _refresh_captcha(request):
    """生成新验证码写入 session。"""
    code = generate_captcha_code()
    request.session[SESSION_CAPTCHA_CODE] = code
    request.session[SESSION_CAPTCHA_TS] = int(time.time())
    return code


def _captcha_is_valid(request, raw_value):
    code = request.session.get(SESSION_CAPTCHA_CODE)
    ts = request.session.get(SESSION_CAPTCHA_TS, 0)
    if not code or not raw_value:
        return False
    if int(time.time()) - ts > settings.ACCOUNTS_CAPTCHA_TIMEOUT:
        return False
    return raw_value.strip().upper() == str(code).upper()


def _clear_captcha(request):
    request.session.pop(SESSION_CAPTCHA_CODE, None)
    request.session.pop(SESSION_CAPTCHA_TS, None)


def login_view(request):
    captcha_required = _captcha_required(request)

    if request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        form = LoginForm(request, data=request.POST, captcha_required=captcha_required)

        # 先校验验证码（无论账号密码是否正确），且一次性有效
        captcha_input = request.POST.get("captcha", "")
        captcha_ok = (not captcha_required) or _captcha_is_valid(request, captcha_input)
        # 验证后立即作废，防止同一验证码反复尝试
        _clear_captcha(request)

        if form.is_valid() and captcha_ok:
            user = form.get_user()
            auth_login(request, user)
            request.session[SESSION_FAILURES] = 0
            _clear_captcha(request)
            messages.success(request, f"欢迎回来，{user.username}")

            redirect_to = request.POST.get("next") or request.GET.get("next")
            if redirect_to and url_has_allowed_host_and_scheme(
                url=redirect_to,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return HttpResponseRedirect(redirect_to)
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        # 登录失败：累计次数
        if not captcha_ok:
            messages.error(request, "验证码错误或已失效，请重新输入")
        if form.is_valid() is False:
            # Django 表单会给出账号/密码错误提示；额外记录次数
            failures = request.session.get(SESSION_FAILURES, 0) + 1
            request.session[SESSION_FAILURES] = failures
            if not captcha_required and not captcha_ok:
                pass
            if failures == settings.ACCOUNTS_MAX_LOGIN_FAILURES:
                messages.warning(request, "登录错误次数过多，请输入验证码后重试")
        captcha_required = _captcha_required(request)
    else:
        form = LoginForm(request)

    # 渲染页面时保证存在一个可用验证码（仅需要验证码的场景使用）
    if captcha_required and not request.session.get(SESSION_CAPTCHA_CODE):
        _refresh_captcha(request)

    return render(request, "registration/login.html", {
        "form": form,
        "captcha_required": captcha_required,
        "captcha_threshold": settings.ACCOUNTS_MAX_LOGIN_FAILURES,
        "captcha_url": reverse("captcha-image"),
        "next": request.GET.get("next", ""),
    })


def logout_view(request):
    auth_logout(request)
    request.session[SESSION_FAILURES] = 0
    _clear_captcha(request)
    return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)


def captcha_image(request):
    """返回验证码 PNG 图片，并把答案存进 session。"""
    code = _refresh_captcha(request)
    image_data = generate_captcha_image(code)
    response = HttpResponse(image_data, content_type="image/png")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
