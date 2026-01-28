from django.views.generic import TemplateView
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from .models import Customer

# 1. 數據看板頁面渲染
@method_decorator(staff_member_required, name='dispatch')
class CRMDashboardView(TemplateView):
    """
    負責渲染 Dashboard 的 HTML 骨架與頂部統計卡片
    """
    template_name = "admin/crm/customer/crm_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 取得所有客戶數據進行匯總
        queryset = Customer.objects.all()
        stats = queryset.aggregate(
            total_val=Sum('estimated_value'),
            count=Count('id')
        )
        
        # 排除已結案與流失的作為「活躍商機」
        active_deals = queryset.exclude(stage__in=['WON', 'LOST']).count()

        context.update({
            "title": _("CRM 數據戰情室"),
            "cards": [
                {
                    "title": _("總客戶數"),
                    "value": f"{stats['count'] or 0:,}",
                    "icon": "groups",
                },
                {
                    "title": _("預估總案量"),
                    "value": f"${(stats['total_val'] or 0):,.0f}",
                    "icon": "payments",
                },
                {
                    "title": _("活躍商機"),
                    "value": f"{active_deals:,}",
                    "icon": "trending_up",
                },
            ]
        })
        return context

# 2. 圖表數據 API 接口
@staff_member_required
def crm_stats_api(request):
    """
    提供給前端 Chart.js 使用的格式化 JSON 數據
    """
    # 💡 核心修正：手動定義映射表，確保與資料庫中的大寫 Key 完全匹配
    STAGE_DISPLAY_MAP = {
        'LEAD': '潛在客戶',
        'NEGOTIATION': '需求確認',
        'PROPOSAL': '提案/報價',
        'WON': '成交結案',
        'LOST': '客戶流失',
    }
    
    # 💡 定義圖表顯示的邏輯順序（由淺入深）
    SORT_ORDER = ['LEAD', 'NEGOTIATION', 'PROPOSAL', 'WON', 'LOST']
    
    # 從資料庫抓取原始聚合數據
    raw_stats = Customer.objects.values('stage').annotate(
        count=Count('id'),
        total_value=Sum('estimated_value')
    )
    
    # 將查詢結果轉為字典以利查找：{ 'WON': {'count': 5, ...}, ... }
    data_map = {item['stage']: item for item in raw_stats}

    labels, counts, values = [], [], []

    # 依照定義好的順序填入數據
    for key in SORT_ORDER:
        # 取得顯示名稱，若資料庫出現預期外的 Key 則顯示原始碼
        labels.append(STAGE_DISPLAY_MAP.get(key, key))
        
        # 取得統計數值，若該階段無資料則補 0
        data = data_map.get(key, {'count': 0, 'total_value': 0})
        counts.append(data['count'])
        values.append(float(data['total_value'] or 0))

    return JsonResponse({
        "status": "success",
        "labels": labels,
        "counts": counts,
        "values": values
    })