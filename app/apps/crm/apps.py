from django.apps import AppConfig

class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crm'     # 必須加上 apps. 前綴
    verbose_name = '客戶關係部'