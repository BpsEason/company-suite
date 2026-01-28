# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from .views import dashboard_home

urlpatterns = [
    # 1. 優先處理 Favicon
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),

    # 2. 網站根目錄
    path('', dashboard_home, name='dashboard'),

    # 3. 💡 核心修正：將 CRM 擴展路由放在原生 Admin 之前
    # 這樣當網址是 /admin/crm/dashboard/ 時，會優先進入你的 App 邏輯
    path('admin/crm/', include('apps.crm.urls')), 

    # 4. 原生 Django Admin 核心
    path('admin/', admin.site.urls), 
    
    # 5. 其他模組
    path('api-auth/', include('rest_framework.urls')),
    path('api/hr/', include('apps.hr.urls', namespace='hr')),
    path('api/finance/', include('apps.finance.urls', namespace='finance')),
]

# 6. 開發環境靜態檔案處理
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 💡 再次提醒：確保 settings.py 裡的 STATIC_URL = '/static/' (有斜線)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)