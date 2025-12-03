import hmac
import hashlib
import json
import time
import requests
from flask import Flask, request, jsonify, url_for

app = Flask(__name__)

# --- DATABASE GIẢ LẬP (In-Memory) ---
orders = []
# Lưu các webhook mà client đăng ký (Pattern: Event Subscription)
webhooks = [] 

# Secret key dùng để ký payload (Pattern: Webhook Security)
WEBHOOK_SECRET = "my_super_secret_key_123"

# --- HELPER FUNCTIONS ---

def sign_payload(payload_body, secret):
    """Tạo chữ ký HMAC SHA256 để bảo mật Webhook"""
    return hmac.new(
        key=secret.encode(), 
        msg=payload_body.encode(), 
        digestmod=hashlib.sha256
    ).hexdigest()

def dispatch_webhooks(event_type, order_data):
    """
    Pattern: Event-Driven / Webhook Dispatcher
    Gửi thông báo đến tất cả URL đã đăng ký khi có sự kiện.
    """
    payload = {
        "event": event_type,
        "timestamp": int(time.time()),
        "data": order_data
    }
    payload_json = json.dumps(payload)
    signature = sign_payload(payload_json, WEBHOOK_SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}" # Để client xác thực
    }

    print(f"\n[SYSTEM] Triggering Webhook Event: {event_type}")
    for hook in webhooks:
        try:
            # Trong thực tế, việc này nên đẩy vào Queue (RabbitMQ/Kafka) để xử lý bất đồng bộ
            print(f" -> Sending to {hook['target_url']} with Signature: {signature}")
            # Giả lập gửi request (Trong demo này, target_url chính là 1 endpoint khác của app này)
            requests.post(hook['target_url'], data=payload_json, headers=headers, timeout=1)
        except Exception as e:
            print(f" -> Failed to send webhook: {e}")

def add_hateoas_links(order):
    """
    Pattern: HATEOAS
    Thêm các liên kết điều hướng dựa trên trạng thái hiện tại (State Machine).
    """
    order_id = order['id']
    links = {
        "self": f"/orders/{order_id}",
        "collection": "/orders"
    }
    
    # Logic điều hướng thông minh
    if order['status'] == 'pending':
        links['pay'] = {"url": f"/orders/{order_id}/pay", "method": "POST"}
        links['cancel'] = {"url": f"/orders/{order_id}/cancel", "method": "POST"}
    elif order['status'] == 'paid':
        links['ship'] = {"url": f"/orders/{order_id}/ship", "method": "POST"}
        links['invoice'] = {"url": f"/orders/{order_id}/invoice", "method": "GET"}
    elif order['status'] == 'shipped':
        links['track'] = {"url": f"/tracking/{order_id}", "method": "GET"}
        
    order['_links'] = links
    return order

# --- API ENDPOINTS ---

@app.route('/orders', methods=['POST'])
def create_order():
    """Pattern: CRUD (Create)"""
    data = request.json
    new_order = {
        "id": str(len(orders) + 1),
        "item": data.get("item"),
        "amount": data.get("amount"),
        "status": "pending" # Default status
    }
    orders.append(new_order)
    
    # Kích hoạt Webhook khi có đơn mới
    dispatch_webhooks("order.created", new_order)
    
    return jsonify(add_hateoas_links(new_order)), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    """Pattern: Query (Pagination + Filtering + Field Selection)"""
    # 1. Filtering
    status_filter = request.args.get('status')
    filtered_orders = orders
    if status_filter:
        filtered_orders = [o for o in orders if o['status'] == status_filter]
    
    # 2. Pagination (Offset-based)
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    start = (page - 1) * limit
    end = start + limit
    paginated_orders = filtered_orders[start:end]
    
    # Apply HATEOAS cho từng item trong list
    response = [add_hateoas_links(o.copy()) for o in paginated_orders]
    
    return jsonify({
        "data": response,
        "meta": {
            "page": page,
            "limit": limit,
            "total": len(filtered_orders)
        }
    })

@app.route('/orders/<order_id>', methods=['GET'])
def get_order_detail(order_id):
    """Pattern: CRUD (Read) + HATEOAS"""
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return jsonify({"error": "Not found"}), 404
    return jsonify(add_hateoas_links(order.copy()))

@app.route('/orders/<order_id>/pay', methods=['POST'])
def pay_order(order_id):
    """Pattern: CRUD (Update) - Thay đổi trạng thái"""
    order = next((o for o in orders if o['id'] == order_id), None)
    if order and order['status'] == 'pending':
        order['status'] = 'paid'
        
        # Kích hoạt Webhook: Sự kiện quan trọng!
        dispatch_webhooks("order.paid", order)
        
        return jsonify(add_hateoas_links(order))
    return jsonify({"error": "Cannot pay"}), 400

# --- WEBHOOK SUBSCRIPTION (Để Client đăng ký nhận tin) ---

@app.route('/webhooks/subscribe', methods=['POST'])
def subscribe_webhook():
    """Cho phép client đăng ký URL để nhận thông báo"""
    data = request.json
    webhooks.append({
        "target_url": data['target_url'],
        "created_at": time.time()
    })
    return jsonify({"message": "Subscribed successfully"}), 201

# --- MOCK CLIENT (Giả lập phía Client nhận Webhook) ---
@app.route('/client/receiver', methods=['POST'])
def client_webhook_receiver():
    """
    Đây là Endpoint giả lập server của Client (người nhận thông báo).
    Nó sẽ kiểm tra chữ ký HMAC để đảm bảo an toàn.
    """
    received_signature = request.headers.get('X-Hub-Signature-256')
    payload_body = request.get_data(as_text=True)
    
    # Client tự tính toán chữ ký để so khớp
    expected_signature = f"sha256={sign_payload(payload_body, WEBHOOK_SECRET)}"
    
    print("\n[CLIENT APP] --- Received Webhook ---")
    if hmac.compare_digest(received_signature, expected_signature):
        print(f"[CLIENT APP] ✅ Security Check Passed! Valid Signature.")
        print(f"[CLIENT APP] Data: {request.json}")
    else:
        print(f"[CLIENT APP] ❌ DANGER! Invalid Signature. Fake Request?")
        
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    print("Starting API Server...")
    app.run(port=5000, debug=True)