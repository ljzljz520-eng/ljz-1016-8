"""登录拦截中间件：未登录访问任意后台路由一律重定向到登录页。"""
from django.conf import settings


class LoginRequiredMiddleware:
    # 始终放行的路径前缀 / 精确路径
    WHITELIST_PREFIXES = (
        "/login/",
        "/captcha/",
        "/admin/login/",
        "/admin/logout/",
        "/static/",
    )
    WHITELIST_EXACT = ("/logout/",)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self._requires_login(request):
            return self.get_response(request)

        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)

        return self.get_response(request)

    def _requires_login(self, request):
        path = request.path
        # 静态资源、健康检查、Django admin 内部资源直接放行
        if path in self.WHITELIST_EXACT:
            return False
        if any(path.startswith(prefix) for prefix in self.WHITELIST_PREFIXES):
            return False
        if path.startswith("/admin/"):
            # admin 自带 staff 权限控制，交给 admin 处理（其登录页已放行）
            return False
        return True
