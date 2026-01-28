from django.apps import AppConfig

class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance'  # 必須加上 apps. 前綴
    verbose_name = '財務管理部'