# 生产线告警后台 · 登录模块

基于 Django 5 + Pillow 实现的后台登录模块，包含账号密码校验、登录拦截、
连续错误图形验证码、登出及告警概览示例页面，桌面与手机自适应。

## 功能

- **账号密码登录**：由 Django `AuthenticationForm` + `contrib.auth` 校验（密码哈希存储）。
- **全局登录拦截**：`LoginRequiredMiddleware` 对所有后台路由生效，未登录一律 302
  到 `/login/?next=<原路径>`，登录成功后跳回原页面。
- **图形验证码**：同一 session 连续登录失败达到阈值（默认 3 次）后出现验证码；
  Pillow 动态生成带噪点/干扰线/旋转的 PNG，校验一次性有效、带 5 分钟过期。
- **告警概览**：登录后进入，展示告警统计卡片、各产线分布、最新告警列表。
- **响应式布局**：CSS Grid + 媒体查询，适配桌面、平板、手机（含超小屏）。

## 快速开始

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

演示账号（迁移自动创建）：

| 账号 | 密码 |
| --- | --- |
| `operator` | `Alarm@2026` |

访问 <http://127.0.0.1:8000/> ：

1. 未登录会自动跳到 `/login/`；
2. 连续输错 3 次密码后，登录页出现图形验证码；
3. 登录成功进入告警概览；右上角可退出登录。

## 关键路径

```
apps/accounts/
  views.py        # 登录 / 登出 / 验证码图片
  forms.py        # 带可选验证码字段的 AuthenticationForm
  captcha.py      # Pillow 图形验证码生成
  middleware.py   # 未登录路由拦截
apps/alarms/      # 告警概览（模型 / 视图 / 种子数据迁移）
templates/        # login.html、base.html、alarms/overview.html
static/css/app.css# 响应式样式
config/settings.py# ACCOUNTS_MAX_LOGIN_FAILURES 等配置项
```

## 配置项（config/settings.py）

- `ACCOUNTS_MAX_LOGIN_FAILURES`：连续失败多少次后要求验证码（默认 3）
- `ACCOUNTS_CAPTCHA_TIMEOUT`：验证码有效期秒数（默认 300）
- `ACCOUNTS_CAPTCHA_WIDTH / HEIGHT`：验证码图片尺寸

> 生产环境请关闭 DEBUG、替换 SECRET_KEY，并在反向代理层启用 HTTPS。
