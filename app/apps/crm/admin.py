import logging
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Customer

logger = logging.getLogger('apps.crm')

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    # 💡 核心修正：強制覆蓋模板路徑，避開失效的 list_before_canvas 屬性
    change_list_template = "admin/crm/customer/change_list.html"
    
    list_display = (
        'display_customer_info', 
        'get_stage_label', 
        'display_value', 
        'assigned_to', 
        'is_hot_lead_status'
    )
    list_display_links = ('display_customer_info',)
    list_per_page = 20
    list_filter_sheet = True
    list_fullwidth = True    
    list_select_related = ('assigned_to',)
    list_filter = ('stage', 'assigned_to', 'created_at')
    search_fields = ('company', 'name', 'email')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        try:
            # 1. 獲取當前過濾後的 QuerySet（這讓統計圖表能隨搜尋結果連動）
            cl = self.get_changelist_instance(request)
            queryset = cl.get_queryset(request)
            
            stats = queryset.aggregate(
                total_val=Sum('estimated_value'),
                count=Count('id')
            )

            # 2. 封裝數據
            dashboard_data = {
                'custom_dashboard_cards': [
                    {"title": _("當前篩選客戶"), "value": f"{stats['count'] or 0}", "icon": "groups"},
                    {"title": _("預估篩選總量"), "value": f"${(stats['total_val'] or 0):,.0f}", "icon": "payments"},
                    {"title": _("活躍商機"), "value": f"{queryset.exclude(stage__in=['WON', 'LOST']).count()}", "icon": "trending_up"},
                ],
                'chart_labels': ["8月", "9月", "10月", "11月", "12月", "1月"],
                'chart_data': [15, 28, 22, 45, 38, stats['count'] or 0],
            }

            extra_context.update(dashboard_data)

        except Exception as e:
            logger.error(f"CRM Dashboard Data Error: {str(e)}", exc_info=True)

        # 3. 呼叫父類並執行
        response = super().changelist_view(request, extra_context=extra_context)

        # 4. 暴力補丁：確保 TemplateResponse 的上下文包含我們的數據
        if hasattr(response, 'context_data'):
            response.context_data.update(extra_context)

        return response

    @display(description=_("客戶資訊"), header=True)
    def display_customer_info(self, instance):
        return instance.company, instance.name

    @display(description=_("預估價值"), label=True)
    def display_value(self, instance):
        color = "warning" if instance.estimated_value >= 500000 else "success"
        return f"${instance.estimated_value:,.2f}", color

    @display(description=_("開發階段"), label=True)
    def get_stage_label(self, instance):
        colors = {
            'LEAD': 'info', 'DISCOVERY': 'primary', 'PROPOSAL': 'warning', 
            'NEGOTIATION': 'warning', 'WON': 'success', 'LOST': 'danger'
        }
        return instance.get_stage_display(), colors.get(instance.stage, 'primary')

    @display(description=_("高價值"), boolean=True)
    def is_hot_lead_status(self, instance):
        return instance.is_hot_lead