from django.apps import AppConfig


class AlarmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.alarms"
    label = "alarms"
    verbose_name = "生产线告警"
