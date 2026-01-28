from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Transaction(models.Model):
    """
    財務交易流水帳模型
    紀錄公司所有的收支明細，支援分類與自動統計。
    """
    class Category(models.TextChoices):
        SALARY = 'SALARY', _('薪資支出')
        EQUIPMENT = 'EQUIPMENT', _('設備採購')
        REVENUE = 'REVENUE', _('專案收入')
        OFFICE = 'OFFICE', _('行政雜支')

    # 欄位定義
    title = models.CharField(
        max_length=200, 
        verbose_name="項目名稱",
        help_text="請輸入簡短的交易摘要（如：12月份房租）"
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="金額",
        help_text="正數為收入，負數為支出"
    )
    category = models.CharField(
        max_length=20, 
        choices=Category.choices, 
        verbose_name="費用分類",
        db_index=True  # 增加索引提升報表查詢效能
    )
    date = models.DateField(
        verbose_name="交易日期",
        db_index=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name="經手人"
    )
    
    # 自動紀錄時間
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="系統建立時間", null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="最後更新時間", null=True)

    class Meta:
        verbose_name = "財務單據"
        verbose_name_plural = "財務流水帳"
        ordering = ['-date', '-created_at']  # 預設由新到舊排序
        # 建立聯合索引，優化按日期與分類的篩選速度
        indexes = [
            models.Index(fields=['date', 'category']),
        ]

    def __str__(self):
        # 讓管理後台的搜尋與關聯顯示更易讀
        return f"[{self.date}] {self.get_category_display()} - {self.title} ({self.amount})"

    @property
    def is_income(self):
        """判斷是否為收入，方便前端渲染顏色"""
        return self.amount > 0