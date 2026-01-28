import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group  # 匯入內建群組模型
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = "建立 HR 測試資料與權限群組"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🚀 開始執行 HR 數據填充 (含群組分配)...'))
        
        with transaction.atomic():
            # 1. 先確保群組存在
            self.stdout.write("檢查權限群組...")
            groups = self.create_groups()
            
            # 2. 建立員工並分配群組
            self.seed_users(groups)

        self.stdout.write(self.style.SUCCESS('✅ HR 數據填充完成！'))

    def create_groups(self):
        """建立職能群組並回傳字典供後續使用"""
        group_names = ['HR_Managers', 'Finance_Staff', 'Sales_Team']
        group_dict = {}
        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f"已建立群組: {name}")
            group_dict[name] = group
        return group_dict

    def seed_users(self, groups):
        roles = [User.Role.HR, User.Role.FINANCE, User.Role.CRM]
        first_names = ["小明", "志豪", "雅婷", "春嬌", "大衛"]
        last_names = ["王", "陳", "李", "張", "林"]

        # 角色與群組的對照表
        role_to_group = {
            User.Role.HR: groups['HR_Managers'],
            User.Role.FINANCE: groups['Finance_Staff'],
            User.Role.CRM: groups['Sales_Team'],
        }

        for i in range(1, 11):
            username = f"employee_{i}"
            if not User.objects.filter(username=username).exists():
                role = random.choice(roles)
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@company.com",
                    password="password123",
                    first_name=random.choice(last_names),
                    last_name=random.choice(first_names),
                    role=role,
                    employee_id=f"EMP{i:03d}"
                )
                
                # 分配群組 (關鍵步驟)
                target_group = role_to_group.get(role)
                if target_group:
                    user.groups.add(target_group)
                
                self.stdout.write(f"已建立員工: {user.username} -> 加入群組: {target_group.name}")