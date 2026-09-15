from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from .models import Alarm, ProductionLine


@login_required
def overview(request):
    """告警概览：统计卡片 + 各产线分布 + 最新告警列表。"""
    alarms = Alarm.objects.select_related("line")

    stats = {
        "total": alarms.count(),
        "active": alarms.filter(status="active").count(),
        "critical": alarms.filter(status="active", level="critical").count(),
        "resolved": alarms.filter(status="resolved").count(),
    }

    level_breakdown = dict(
        alarms.filter(status="active")
        .values_list("level")
        .annotate(n=Count("id"))
    )
    stats.update({
        "major": level_breakdown.get("major", 0),
        "minor": level_breakdown.get("minor", 0),
        "info": level_breakdown.get("info", 0),
    })

    lines = (
        ProductionLine.objects.annotate(
            active_count=Count("alarms", filter=Q(alarms__status="active")),
            critical_count=Count(
                "alarms",
                filter=Q(alarms__status="active", alarms__level="critical"),
            ),
        ).order_by("-critical_count", "-active_count")
    )

    latest = alarms.all()[:15]

    return render(request, "alarms/overview.html", {
        "stats": stats,
        "lines": lines,
        "latest": latest,
    })
