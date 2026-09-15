import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def seed_data(apps, schema_editor):
    ProductionLine = apps.get_model("alarms", "ProductionLine")
    Alarm = apps.get_model("alarms", "Alarm")
    User = apps.get_model("auth", "User")

    if not User.objects.filter(username="operator").exists():
        User.objects.create_user(
            username="operator",
            password="Alarm@2026",
            is_staff=True,
            first_name="值班",
            last_name="操作员",
        )

    line_defs = [
        ("L01", "一号灌装线", "一号车间"),
        ("L02", "二号包装线", "一号车间"),
        ("L03", "三号装配线", "二号车间"),
        ("L04", "四号检测线", "二号车间"),
    ]
    lines = []
    for code, name, location in line_defs:
        lines.append(ProductionLine.objects.create(code=code, name=name, location=location))

    alarm_defs = [
        (lines[0], "灌装温度超出上限", "critical", "active", "出口温度 88.6℃，阈值 85℃"),
        (lines[1], "包装膜余量不足", "major", "active", "剩余 12%，请及时更换"),
        (lines[2], "机械臂 3 号轴通讯中断", "critical", "ack", "PLC 心跳丢失已超过 30 秒"),
        (lines[3], "视觉检测误检率偏高", "minor", "active", "近 1 小时误检率 2.3%"),
        (lines[0], "传送带速度波动", "minor", "resolved", "速度波动 ±6%，已自动恢复"),
        (lines[2], "气压低于工作阈值", "major", "resolved", "气压 0.42MPa，已回升至 0.6MPa"),
        (lines[3], "定时保养提醒", "info", "active", "设备累计运行 480 小时，建议保养"),
    ]
    for line, title, level, status, message in alarm_defs:
        Alarm.objects.create(line=line, title=title, level=level,
                             status=status, message=message)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductionLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64, unique=True, verbose_name="生产线名称")),
                ("code", models.CharField(max_length=32, unique=True, verbose_name="产线编号")),
                ("location", models.CharField(blank=True, max_length=64, verbose_name="所在车间")),
            ],
            options={"verbose_name": "生产线", "verbose_name_plural": "生产线"},
        ),
        migrations.CreateModel(
            name="Alarm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=128, verbose_name="告警标题")),
                ("level", models.CharField(
                    choices=[("critical", "紧急"), ("major", "重要"), ("minor", "一般"), ("info", "提示")],
                    default="minor", max_length=16, verbose_name="告警级别")),
                ("status", models.CharField(
                    choices=[("active", "未处理"), ("ack", "处理中"), ("resolved", "已恢复")],
                    default="active", max_length=16, verbose_name="状态")),
                ("message", models.CharField(blank=True, max_length=255, verbose_name="告警内容")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="发生时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("line", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="alarms", to="alarms.productionline", verbose_name="生产线")),
            ],
            options={"verbose_name": "告警", "verbose_name_plural": "告警", "ordering": ("-created_at",)},
        ),
        migrations.RunPython(seed_data, migrations.RunPython.noop),
    ]
