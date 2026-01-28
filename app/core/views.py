from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
# 💡 修正關鍵：從正確的 App (apps.crm) 匯入模型
from apps.crm.models import Customer 

@staff_member_required
def dashboard_home(request):
    """
    Nexus Admin 首頁數據導覽
    """
    # 獲取統計數據
    queryset = Customer.objects.all()
    stats = queryset.aggregate(
        total_val=Sum('estimated_value'),
        count=Count('id')
    )
    
    # 準備渲染給 crm_dashboard.html 的內容
    context = {
        'username': request.user.username,
        'cards': [
            {
                "title": "總客戶數",
                "value": f"{stats['count'] or 0:,}",
                "icon": "groups",
            },
            {
                "title": "預估總案量",
                "value": f"${(stats['total_val'] or 0):,.0f}",
                "icon": "payments",
            },
            {
                "title": "活躍商機",
                "value": queryset.exclude(stage__in=['WON', 'LOST']).count(),
                "icon": "trending_up",
            },
        ],
    }
    
    # 💡 指向正確的模板路徑
    return render(request, 'admin/crm/customer/crm_dashboard.html', context)