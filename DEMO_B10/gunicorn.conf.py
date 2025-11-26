# gunicorn.conf.py
import multiprocessing

# Tên process hiển thị trong lệnh 'top'
proc_name = 'book_store_api'

# Chạy ở cổng 8000, chấp nhận mọi IP
bind = "0.0.0.0:8000"

# Số lượng worker để xử lý song song (Công thức: 2 * CPU + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# Cấu hình log của Gunicorn (Log hệ thống)
# In ra màn hình console (để Docker logs bắt được)
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Timeout: Nếu request xử lý quá 30s -> Kill worker (Tránh treo hệ thống)
timeout = 30