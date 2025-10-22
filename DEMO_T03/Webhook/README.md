# Webhook (Extensibility)
- **Extensibility** đề cập đến khả năng cho phép bên thứ 3 (third parites) tùy chỉnh hoặc thêm chức năng mới vào API thông qua cơ chế được thiết kế sẵn (như Webhook, Plugin hoặc Custom Field)
- Nó cho phép API thay đổi hoặc phát triển mà không cần sửa đổi mã nguồn cốt lõi để đáp ứng một nhu cầu tùy chỉnh cụ thể 
- **Webhook** là một cơ chế cho phép một ứng dụng tự động gửi thông tin (dữ liệu) đến một ứng dụng ngay lập tức khi có một sự kiện cụ thể xảy ra, mà không cần bên nhận phải phải liên tục hỏi thăm (polling)
    - Ví dụ : Người dùng đăng nhập vào App A để xem giá Iphone có mức giá 25 triệu, người dùng muốn khi nào giá giảm xuống còn 20 triệu thì gửi thông báo cho người dùng mà không cần đăng nhập vào để xem giá, đó là việc sử dụng Webhook 
## Demo Webhook 
- Demo về quản lý sách : Người dùng sẽ mượn sách ở App A và khi đến ngày trả sách thì người dùng sẽ nhận được thông báo đến ngày trả sách mà không cần đăng nhập vào App A để xem đã hết hạn hay chưa
```python
api.add_resource(BorrowBookAPI, '/api/borrow')
api.add_resource(CheckDueDateAPI, '/api/check_due_dates')
api.add_resource(NotificationWebhook, '/webhook/notify') 
```