from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    """
    CRM 客戶資料模型
    管理從潛在客戶到成交的完整生命週期。
    """
    class Stage(models.TextChoices):
        LEAD = 'LEAD', _('潛在客戶')
        DISCOVERY = 'DISCOVERY', _('需求確認')
        PROPOSAL = 'PROPOSAL', _('方案報價')
        NEGOTIATION = 'NEGOTIATION', _('商議談判')
        WON = 'WON', _('成功結案')
        LOST = 'LOST', _('開發失敗')

    # 客戶基本資訊
    name = models.CharField(max_length=100, verbose_name="客戶姓名")
    company = models.CharField(max_length=100, verbose_name="所屬企業", db_index=True)
    email = models.EmailField(verbose_name="聯繫郵箱", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="聯絡電話", blank=True)
    
    # 業務進度與價值
    stage = models.CharField(
        max_length=20, 
        choices=Stage.choices, 
        default=Stage.LEAD, 
        verbose_name="開發階段",
        db_index=True
    )
    estimated_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name="預估價值",
        help_text="預計成交的合同金額"
    )
    
    # 權限與關聯
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        # limit_choices_to={'role': 'CRM'},
        verbose_name="負責業務專員",
        related_name="assigned_customers"
    )
    
    # 系統紀錄
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="系統建立時間", null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="最後更新時間", null=True)

    class Meta:
        verbose_name = "客戶"
        verbose_name_plural = "客戶資料庫"
        # 預設按建立時間倒序，且將成交金額高的排前面
        ordering = ['-created_at', '-estimated_value']
        indexes = [
            models.Index(fields=['stage', 'company']),
        ]

    def __str__(self):
        return f"{self.company} - {self.name} ({self.get_stage_display()})"

    @property
    def is_hot_lead(self):
        """判斷是否為高價值潛在客戶（金額大於 100 萬）"""
        return self.estimated_value >= 1000000