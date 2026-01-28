#!/bin/bash
set -e

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}===> [Nexus Admin] 啟動初始化程序...${NC}"

# 1. 檢查資料庫連線
echo "等待資料庫 (db:5432) 啟動..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo -e "${GREEN}資料庫已就緒！${NC}"

# 2. 自動檢查與初始化 (避免重複初始化)
if [ ! -f "manage.py" ]; then
    echo -e "${YELLOW}偵測到空的專案目錄，正在初始化 Django 專案結構...${NC}"
    django-admin startproject core .
    mkdir -p apps/hr apps/finance apps/crm
    echo -e "${GREEN}專案結構初始化完成。${NC}"
fi

# 3. 資料庫遷移
echo "檢查模型變更 (makemigrations)..."
python manage.py makemigrations --noinput
echo "執行資料庫遷移 (migrate)..."
python manage.py migrate --noinput

# 4. 自動建立超級管理員 (加入自定義欄位)
echo "檢查超級管理員帳戶..."
cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin', 
        email='admin@example.com', 
        password='admin123',
        employee_id="ADMIN-001",
        role="ADMIN"
    )
    print("超級管理員 admin/admin123 建立成功。")
EOF

# 5. 數據填充 (Seed Data)
if [ "$SEED_DATA" = "True" ] || [ "$SEED_DATA" = "1" ]; then
    echo -e "${YELLOW}執行 Seed Data 填充亮點數據...${NC}"
    python manage.py seed_hr || true
    python manage.py seed_finance || true
    python manage.py seed_crm || true
fi

# 6. 🚀 亮點關鍵：強制刷新靜態檔案
echo "清理舊的靜態檔案緩存..."
rm -rf /app/staticfiles/*
echo "收集靜態檔案 (collectstatic)..."
python manage.py collectstatic --noinput --clear

# 7. 啟動服務
echo -e "${BLUE}偵測到環境變數 DEBUG=$DEBUG${NC}"

if [[ "$DEBUG" == "True" || "$DEBUG" == "true" || "$DEBUG" == "1" ]]; then
    echo -e "${YELLOW}開發模式啟動: Django Runserver${NC}"
    exec python manage.py runserver 0.0.0.0:8000
else
    echo -e "${GREEN}生產模式啟動: Gunicorn${NC}"
    exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi