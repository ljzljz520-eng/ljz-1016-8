from django.test import TestCase
from django.urls import reverse


class LoginFlowTests(TestCase):
    USERNAME = "operator"
    PASSWORD = "Alarm@2026"

    def setUp(self):
        from django.contrib.auth.models import User
        user, _ = User.objects.get_or_create(
            username=self.USERNAME,
            defaults={"password": "unused"},
        )
        user.set_password(self.PASSWORD)
        user.save()

    def test_anonymous_blocked_from_backend_routes(self):
        """未登录访问任意后台路由都被拦截到登录页，并携带 next。"""
        resp = self.client.get("/")
        self.assertRedirects(resp, "/login/?next=/")
        resp = self.client.get("/overview/")
        self.assertRedirects(resp, "/login/?next=/overview/")

    def test_login_success_redirects_to_overview(self):
        """正确账号密码经 Django 校验后进入告警概览。"""
        resp = self.client.post(reverse("login"), {
            "username": self.USERNAME,
            "password": self.PASSWORD,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/")
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "告警概览")

    def test_next_redirect_after_login(self):
        resp = self.client.post("/login/?next=/overview/", {
            "username": self.USERNAME,
            "password": self.PASSWORD,
            "next": "/overview/",
        })
        self.assertRedirects(resp, "/overview/")

    def test_logout_blocks_again(self):
        self.client.force_login(self.user) if False else None
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.assertEqual(self.client.get("/").status_code, 200)
        self.client.post(reverse("logout"))
        self.assertRedirects(self.client.get("/"), "/login/?next=/")

    def test_captcha_required_after_three_failures(self):
        """连续错误 3 次后出现验证码；不带验证码或验证码错误均无法登录。"""
        for _ in range(3):
            resp = self.client.post(reverse("login"), {
                "username": self.USERNAME, "password": "wrong-password",
            })
            self.assertEqual(resp.status_code, 200)

        # 此时页面应要求验证码
        resp = self.client.get(reverse("login"))
        self.assertContains(resp, "验证码")
        session = self.client.session
        self.assertIn("captcha_code", session)

        # 没有验证码 -> 仍登录失败
        resp = self.client.post(reverse("login"), {
            "username": self.USERNAME, "password": self.PASSWORD,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

        # 错误验证码 -> 登录失败，且旧验证码已作废
        resp = self.client.post(reverse("login"), {
            "username": self.USERNAME,
            "password": self.PASSWORD,
            "captcha": "ZZZZ",
        })
        self.assertEqual(resp.status_code, 200)

        # 取当前 session 中的验证码（验证码一次性，需要再刷一次页面）
        self.client.get(reverse("login"))
        code = self.client.session["captcha_code"]
        resp = self.client.post(reverse("login"), {
            "username": self.USERNAME,
            "password": self.PASSWORD,
            "captcha": code,
        })
        self.assertRedirects(resp, "/")
        # 成功后失败计数清零，不再需要验证码
        self.assertEqual(self.client.session.get("login_failures", 0), 0)

    def test_captcha_image_endpoint(self):
        resp = self.client.get(reverse("captcha-image"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "image/png")
        self.assertIn("captcha_code", self.client.session)
