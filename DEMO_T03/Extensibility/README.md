# Extensibility and Versioning API 
Tìm hiểu về Extensibility và Versioning trong API

## Extensibility 
- **Extensibility** trong API là khả năng cho phép API được mở rộng hoặc tùy chỉnh chức năng mà không cần thay đổi mã nguồn cốt lõi của API
- **Extensibility** là khả năng cho phép bên ngoài (third parties) tùy chỉnh hoặc thêm chức năng mới vào API thông qua một cơ chế được thiết kế sẵn (như Webhook, Plugin hoặc Custom Field)
- Cho phép API thay đổi hoặc phát triển mà không cần sửa đổi code để đáp ứng một nhu cầu tùy chỉnh cụ thể
    -  Ví dụ : Cho phép người dùng đăng ký một Webhook để chạy logic riêng khi một cuốn sách được cập nhật 


## Versioning 
**Versioning** (quản lý phiên bản) trong API là quá trình quản lý và phát hành các phiên bản khác nhau của một API theo thời gian

Nó cho phép nhà phát triển API thực hiện các thay đổi không tương thích (breaking changes) hoặc thêm các tính năng mới mà vẫn đảm bảo rằng các ứng dụng (client) đang sử dụng phiên bản cũ vẫn có thể hoạt động mà không bị gián đoạn

## Demo Extensibility and Versioning 
- Tạo folder **versions** để quản lý các phiên bản (Versioning)
```python
from versions.book_v1 import BookListV1
from versions.book_v2 import BookListV2

api.add_resource(BookListV1, "/api/v1/books")
api.add_resource(BookListV2, "/api/v2/books")
```
- Phiên bản mới sẽ có thêm tính năng tìm kiếm, sắp xếp theo tên tác giả và mở rộng phản hồi (Response Extensibility) như là phản hồi trả ra một danh sách mới, cung cấp thông tin bổ sung (sắp xếp thông tin) theo tên các tác giả
```powershell
/api/v2/books?sort=author
```
- Metadata mới (<mark>sorted_by</mark>) được thêm vào, không phá vỡ client cũ 
```python
response = {
            "metadata": {
                "version": "v2",
                "total": len(filtered_books),
                "filter_by": {"author": args["author"]} if args["author"] else {},
                "sorted_by": args["sort"] if args["sort"] else None
            },
            "books": filtered_books
        }
```
