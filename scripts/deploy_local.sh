#!/bin/bash
set -e

# Màu sắc cho log
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Bắt đầu quá trình triển khai Local Docker cho KidCoin...${NC}"

# 1. Dừng các container hiện tại
echo -e "${BLUE}🛑 Đang dừng các container cũ...${NC}"
docker compose down

# 2. Build và Khởi động lại
echo -e "${BLUE}🏗️  Đang build và khởi động lại các services...${NC}"
docker compose up --build -d

# 3. Chờ DB sẵn sàng (Healthcheck đã có trong docker-compose nhưng ta kiểm tra thêm cho chắc)
echo -e "${BLUE}⏳ Đang chờ Database sẵn sàng...${NC}"
# Chờ tối đa 30s cho DB
for i in {1..30}; do
  if docker compose exec -T db pg_isready -U kidcoin_user -d kidcoin_db > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database đã sẵn sàng!${NC}"
    break
  fi
  sleep 1
  if [ $i -eq 30 ]; then
    echo "❌ Lỗi: Database không sẵn sàng sau 30 giây."
    exit 1
  fi
done

# 4. Thông báo và theo dõi logs
echo -e "${GREEN}✅ Ứng dụng đã được triển khai tại http://localhost:8000${NC}"
echo -e "${BLUE}📜 Đang theo dõi logs của Web để xem Migrations và Scheduler...${NC}"
echo -e "${BLUE}(Nhấn Ctrl+C để thoát theo dõi logs, ứng dụng vẫn sẽ chạy ngầm)${NC}"
echo "-------------------------------------------------------------------"
docker compose logs -f web
