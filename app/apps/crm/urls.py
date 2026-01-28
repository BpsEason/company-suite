from django.urls import path
from django.contrib import admin
from .views import CRMDashboardView, crm_stats_api

# 💡 這裡定義了 namespace，之後可以用 reverse('admin:crm-dashboard') 呼叫
app_name = 'crm'

urlpatterns = [
    # 1. 數據看板主頁面
    # 網址：/admin/crm/dashboard/
    # 使用 admin_view 封裝可確保：1.必須登入 2.必須是 staff 3.自動處理後台樣式
    path(
        'dashboard/', 
        admin.site.admin_view(CRMDashboardView.as_view()), 
        name='dashboard'
    ),
    
    # 2. 圖表數據 API 接口
    # 網址：/admin/crm/api/stats/
    # 💡 建議加上結尾斜線，確保與前端 fetch 請求一致
    path(
        'api/stats/', 
        crm_stats_api, 
        name='stats_api'
    ),
]