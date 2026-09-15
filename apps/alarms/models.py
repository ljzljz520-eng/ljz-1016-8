from django.db import models


class ProductionLine(models.Model):
    name = models.CharField("生产线名称", max_length=64, unique=True)
    code = models.CharField("产线编号", max_length=32, unique=True)
    location = models.CharField("所在车间", max_length=64, blank=True)

    class Meta:
        verbose_name = "生产线"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.code} {self.name}"


class Alarm(models.Model):
    LEVEL_CHOICES = [
        ("critical", "紧急"),
        ("major", "重要"),
        ("minor", "一般"),
        ("info", "提示"),
    ]
    STATUS_CHOICES = [
        ("active", "未处理"),
        ("ack", "处理中"),
        ("resolved", "已恢复"),
    ]

    line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE,
                             related_name="alarms", verbose_name="生产线")
    title = models.CharField("告警标题", max_length=128)
    level = models.CharField("告警级别", max_length=16, choices=LEVEL_CHOICES, default="minor")
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="active")
    message = models.CharField("告警内容", max_length=255, blank=True)
    created_at = models.DateTimeField("发生时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "告警"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return f"[{self.get_level_display()}]{self.title}"
