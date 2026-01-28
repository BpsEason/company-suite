from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    # 1. 列表顯示優化
    list_display = (
        'display_header',      # 標題 + 分類
        'display_amount',      # 金額 (帶顏色)
        'get_category_label',  # 類別 (標籤)
        'date', 
        'created_by'
    )
    
    # 💡 2. 分頁與效能優化配置
    list_per_page = 20             # 每頁顯示 20 筆 (Laravel 風格)
    list_max_show_all = 200        # 限制「顯示全部」的最大值，防止一次撈取過多導致崩潰
    show_full_result_count = False  # 大數據優化：不跑 COUNT(*) SQL，大幅提升翻頁速度
    
    # 💡 3. 穩定排序：分頁系統必備，確保翻頁時資料一致
    ordering = ('-date', '-id')
    
    # 4. 佈局與過濾器優化
    list_filter = ('category', 'date')
    list_filter_sheet = True     # 側邊抽屜式過濾器
    list_fullwidth = True        # 全寬顯示
    search_fields = ('title',)
    
    # 預防 N+1 查詢
    list_select_related = ('created_by',)
    
    # 5. 自動關聯當前使用者
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # --- 💡 Unfold UI 裝飾器 ---

    @display(description=_("項目/備註"), header=True)
    def display_header(self, instance):
        return instance.title, instance.category

    @display(description=_("金額"))
    def display_amount(self, instance):
        color = "success" if instance.amount >= 0 else "danger"
        formatted_amount = f"{instance.amount:+,.2f}"
        return formatted_amount, color

    @display(description=_("收支類型"), label=True)
    def get_category_label(self, instance):
        colors = {
            'INCOME': 'success',
            'EXPENSE': 'info',
            'INVESTMENT': 'warning',
        }
        return instance.get_category_display(), colors.get(instance.category, 'primary')

    # 6. 底部摘要統計
    def get_list_display_summary(self, request, queryset):
        from django.db.models import Sum
        total = queryset.aggregate(Sum('amount'))['amount__sum'] or 0
        return {
            'display_amount': f"本頁/篩選總計: {total:+,.2f}"
        }