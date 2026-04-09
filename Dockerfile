# Sử dụng Python 3.10 slim để tối ưu dung lượng image
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Thiết lập biến môi trường
# PYTHONDONTWRITEBYTECODE: Ngăn Python tạo file .pyc
# PYTHONUNBUFFERED: Đảm bảo log được in ra console ngay lập tức
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Cài đặt các dependencies hệ thống cần thiết (nếu có)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Cấp quyền thực thi cho entrypoint script
RUN chmod +x entrypoint.sh

# Expose port 8000 (mặc định của uvicorn/fastapi)
EXPOSE 8000

# Chạy entrypoint script (tự động chạy alembic upgrade head trước khi khởi động uvicorn)
ENTRYPOINT ["./entrypoint.sh"]
