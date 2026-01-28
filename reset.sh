#!/bin/bash
# reset.sh - 徹底重置開發環境

echo "🔥 正在銷毀當前環境 (移除 Volumes 與本地 Images)..."
docker-compose down -v --rmi all

echo "🛠️ 重新編譯並啟動容器..."
# 這裡會觸發上面的 init-web.sh
docker-compose up -d --build

echo "⏳ 等待系統初始化 (15s)..."
sleep 15

echo "🚀 [SUCCESS] 系統已重置！"
echo "請登入: http://localhost:8888/admin/"
echo "帳密: admin / admin123"