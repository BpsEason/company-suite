from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# 💡 Unfold 核心組件與美化裝飾器
from unfold.admin import ModelAdmin
from unfold.decorators import display 
from unfold.forms import UserChangeForm, UserCreationForm

# 💡 核心修正：動態匯入保護，確保在各種環境下都能抓到 ImportExport 功能
try:
    # 針對 Unfold 2.0+，這是最能確保 Actions Bar 正常顯示的類別
    from unfold.contrib.import_export.admin import ImportExportActionModelAdmin as BaseImportExportAdmin
except (ImportError, ModuleNotFoundError):
    try:
        from unfold.contrib.import_export.admin import ImportExportModelAdmin as BaseImportExportAdmin
    except (ImportError, ModuleNotFoundError):
        BaseImportExportAdmin = ModelAdmin

from import_export import resources
from .models import User

# 1. 資料匯入匯出資源配置
class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'employee_id', 'role', 'email', 'is_active', 'date_joined')

# 2. User 管理介面
@admin.register(User)
class UserAdmin(BaseImportExportAdmin, BaseUserAdmin):
    # 💡 繼承順序：Unfold 類別置左，確保 Nexus Admin 品牌標籤優先渲染
    
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = UserChangeForm
    
    resource_class = UserResource

    # A. 列表頁展示
    list_display = ('display_header', 'employee_id', 'get_role_label', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'employee_id', 'email')
    ordering = ('-date_joined',)
    
    # 💡 強制啟動批量操作
    list_per_page = 10 
    actions = ["delete_selected"]
    
    # B. 美化顯示邏輯 (Nexus 雙行標題與膠囊標籤)
    @display(description=_("使用者"), header=True)
    def display_header(self, instance):
        return instance.username, instance.email

    @display(description=_("職位角色"), label=True)
    def get_role_label(self, instance):
        color = {
            'HR': 'info',      
            'FINANCE': 'success', 
            'CRM': 'warning',  
            'ADMIN': 'danger', 
        }.get(instance.role, 'primary')
        return instance.get_role_display(), color

    # C. 詳情頁表單分組 (啟用 Unfold Tab 標籤頁模式)
    fieldsets = (
        (_("基本帳號資訊"), {
            "fields": ("username", "password", "employee_id", "role"),
            "classes": ["tab"],
        }),
        (_("個人資料"), {
            "fields": ("first_name", "last_name", "email"),
            "classes": ["tab"],
        }),
        (_("權限與狀態"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "classes": ["tab"],
        }),
        (_("重要日期"), {
            "fields": ("date_joined", "last_login"),
            "classes": ["tab"],
        }),
    )

    # D. 💡 Unfold 專屬 UI 佈局修復
    readonly_fields = ("date_joined", "last_login")
    list_fullwidth = True      # 橫向全寬展現專業感
    list_filter_sheet = True   # 側邊抽屜篩選器
    
    # 💡 這是解決「按鈕消失」的終極關鍵參數
    list_actions_position = "top" 
    actions_on_top = True
    actions_selection_counter = True