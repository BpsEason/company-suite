# 使用多階段構建或明確版本號以確保穩定性
FROM python:3.12-slim-bookworm

# 1. 安裝 uv：利用官方提供的二進位檔
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /bin/uv

# 2. 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# 3. 安裝系統依賴 (優化：合併指令並清理快取以減少映像檔大小)
# 加入 curl 是為了後續可能需要的健康檢查
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    netcat-openbsd \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. 安裝 Python 依賴 (優化：先複製 requirements 避免程式碼變動導致重複安裝)
COPY requirements.txt .
RUN uv pip install --no-cache -r requirements.txt

# 5. 複製專案檔案
COPY . .

# 6. 處理 Entrypoint 與權限 (優化：建立非 root 使用者提升安全性)
COPY entrypoint.sh /entrypoint.sh
# 關鍵：使用 sed 強制將換行符轉為 LF (解決 Windows Git Bash 上傳後的相容性問題)
RUN sed -i 's/\r$//' /entrypoint.sh && \
    chmod +x /entrypoint.sh && \
    useradd -m django && \
    chown -R django:django /app

# 切換到非 root 使用者
USER django

ENTRYPOINT ["/entrypoint.sh"]