import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()

class Command(BaseCommand):
    help = "專門填充 CRM 客戶測試資料"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🤝 開始執行 CRM 數據填充..."))

        # 1. 動態獲取模型，確保跨 App 調用穩定
        try:
            Customer = apps.get_model('crm', 'Customer')
        except LookupError:
            self.stdout.write(self.style.ERROR("❌ 找不到 Customer 模型，請檢查 apps/crm/models.py"))
            return

        # 2. 清理舊數據 (避免每次重啟都塞入重複資料)
        Customer.objects.all().delete()

        # 3. 獲取業務員 (過濾角色或使用超級管理員)
        sales_reps = User.objects.filter(role='CRM')
        if not sales_reps.exists():
            # fallback: 如果沒業務，就找超級管理員
            admin = User.objects.filter(is_superuser=True).first()
            sales_reps = [admin] if admin else []

        if not sales_reps:
            self.stdout.write(self.style.ERROR("❌ 找不到任何使用者來分配客戶，請先執行 seed_hr"))
            return

        # 4. 準備批量建立資料
        company_prefixes = ["模擬", "宏達", "國泰", "富邦", "台塑", "遠東"]
        company_suffixes = ["科技", "實業", "顧問", "媒體", "物流", "資訊"]
        names = ["王大明", "李小龍", "張華", "趙敏", "郭靖", "黃蓉", "令狐沖", "任盈盈"]
        
        customers_pool = []
        for i in range(20):
            # 組合更真實的企業名稱
            company_name = f"{random.choice(company_prefixes)}{random.choice(company_suffixes)} ({i+1:02d})"
            
            # 從 Stage Choices 中取出所有的 Key (如 'LEAD', 'WON')
            # 假設你的 Stage 定義在 Customer 模型內
            stage_keys = [choice[0] for choice in Customer.Stage.choices]
            
            customer_instance = Customer(
                name=random.choice(names),
                company=company_name,
                email=f"sales_contact_{i}@testmail.com",
                phone=f"09{random.randint(10, 88)}-{random.randint(100, 999)}-{i:03d}",
                stage=random.choice(stage_keys),
                estimated_value=random.randint(100000, 5000000),
                assigned_to=random.choice(list(sales_reps))
            )
            customers_pool.append(customer_instance)

        # 5. 一次性寫入資料庫
        Customer.objects.bulk_create(customers_pool)
        
        self.stdout.write(self.style.SUCCESS(f"✅ 成功建立 {len(customers_pool)} 筆 CRM 客戶資料！"))