from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 1. 定義角色枚舉 (Enumeration)
    # 這樣做的好處是未來在程式碼中可以使用 User.Role.ADMIN 避免硬編碼字串
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', '系統管理員'
        HR = 'HR', '人事專員'
        FINANCE = 'FINANCE', '財務會計'
        CRM = 'CRM', '業務代表'

    # 2. 欄位定義：加入 choices 參數
    # 這會讓 Django 自動生成 .get_role_display() 方法
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.ADMIN,
        verbose_name="職位角色"
    )

    employee_id = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True, 
        verbose_name="員工編號"
    )

    class Meta:
        verbose_name = "使用者"
        verbose_name_plural = "使用者列表"

    def __str__(self):
        # 讓 Admin 後台顯示更直觀，例如：admin (系統管理員)
        return f"{self.username} ({self.get_role_display()})"