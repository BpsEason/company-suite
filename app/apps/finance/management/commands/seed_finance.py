import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "專門填充 Finance 財務流水帳數據"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("💰 開始執行財務數據填充..."))

        # 1. 動態獲取模型，確保跨 App 調用穩定
        try:
            Transaction = apps.get_model('finance', 'Transaction')
        except LookupError:
            self.stdout.write(self.style.ERROR("❌ 找不到 Transaction 模型，請檢查 apps/finance/models.py"))
            return

        # 2. 獲取超級管理員作為預設建立者
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR("❌ 找不到管理員，請確認 entrypoint 已建立 admin"))
            return

        # 3. 清理舊數據（可選，建議保留以維持開發環境乾淨）
        Transaction.objects.all().delete()

        # 4. 準備批量建立資料 (效能優化)
        transactions = []
        categories = ['SALARY', 'EQUIPMENT', 'REVENUE', 'OFFICE']
        
        self.stdout.write(f"正在生成過去 30 天的交易紀錄...")
        
        for i in range(30):
            # 從今天往回推 i 天
            current_date = datetime.now().date() - timedelta(days=i)
            
            # 每天隨機產生 1-3 筆交易
            for j in range(random.randint(1, 3)):
                cat = random.choice(categories)
                
                # 邏輯：REVENUE 為正值，其餘為負值（支出）
                if cat == 'REVENUE':
                    amount = random.randint(20000, 150000)
                    title = f"專案入帳 - {current_date.strftime('%m%d')}-{j}"
                elif cat == 'SALARY':
                    amount = -random.randint(40000, 60000)
                    title = f"薪資發放 - {current_date.strftime('%B')}"
                else:
                    amount = -random.randint(500, 8000)
                    title = f"日常支出 ({cat}) - {j}"

                transactions.append(
                    Transaction(
                        title=title,
                        amount=amount,
                        category=cat,
                        date=current_date,
                        created_by=admin_user
                    )
                )

        # 5. 一次性寫入資料庫
        Transaction.objects.bulk_create(transactions)
        
        self.stdout.write(self.style.SUCCESS(f"✅ 成功建立 {len(transactions)} 筆財務流水帳！"))