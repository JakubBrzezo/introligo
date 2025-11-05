# Integration Examples

These examples show how multiple services work together to build complete e-commerce workflows.

## Complete Order Flow (Python)

This example demonstrates the full order creation workflow from user creation through payment processing:

```python
import grpc
from user.v1 import user_pb2, user_pb2_grpc
from product.v1 import product_pb2, product_pb2_grpc
from order.v1 import order_pb2, order_pb2_grpc
from payment.v1 import payment_pb2, payment_pb2_grpc
from notification.v1 import notification_pb2, notification_pb2_grpc

# Setup channels
channel = grpc.insecure_channel('localhost:50051')
user_stub = user_pb2_grpc.UserServiceStub(channel)
product_stub = product_pb2_grpc.ProductServiceStub(channel)
order_stub = order_pb2_grpc.OrderServiceStub(channel)
payment_stub = payment_pb2_grpc.PaymentServiceStub(channel)
notification_stub = notification_pb2_grpc.NotificationServiceStub(channel)

# 1. Create a user
user_resp = user_stub.CreateUser(user_pb2.CreateUserRequest(
    email="customer@example.com",
    name="Jane Customer"
))
user_id = user_resp.user.id

# 2. List products
products = product_stub.ListProducts(product_pb2.ListProductsRequest(
    status=product_pb2.PRODUCT_STATUS_ACTIVE,
    page_size=10
))

# 3. Create an order
order_resp = order_stub.CreateOrder(order_pb2.CreateOrderRequest(
    user_id=user_id,
    items=[
        order_pb2.CreateOrderItem(
            product_id=products.products[0].id,
            quantity=2
        )
    ],
    shipping_address=order_pb2.ShippingAddress(
        full_name="Jane Customer",
        address_line1="123 Main St",
        city="San Francisco",
        state="CA",
        postal_code="94102",
        country="US",
        phone="+15551234567"
    )
))
order_id = order_resp.order.id

# 4. Process payment
payment_resp = payment_stub.CreatePayment(payment_pb2.CreatePaymentRequest(
    order_id=order_id,
    user_id=user_id,
    amount=order_resp.order.total,
    currency="USD",
    method=payment_pb2.PaymentMethod(
        card=payment_pb2.CreditCard(
            token="tok_visa_test",
            last4="4242",
            brand=payment_pb2.CARD_BRAND_VISA
        )
    )
))

# 5. Send notification
notification_stub.SendNotification(notification_pb2.SendNotificationRequest(
    user_id=user_id,
    type=notification_pb2.NOTIFICATION_TYPE_ORDER,
    title="Order Confirmed!",
    message=f"Your order #{order_id[:8]} has been confirmed.",
    channels=[
        notification_pb2.NOTIFICATION_CHANNEL_EMAIL,
        notification_pb2.NOTIFICATION_CHANNEL_PUSH
    ]
))

print(f"Order created: {order_id}")
print(f"Payment processed: {payment_resp.payment.id}")
```

## Real-Time Order Tracking (Go)

This example uses server-side streaming to receive real-time order status updates:

```go
package main

import (
    "context"
    "io"
    "log"
    "google.golang.org/grpc"
    orderpb "example.com/order/v1"
)

func main() {
    conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
    defer conn.Close()

    client := orderpb.NewOrderServiceClient(conn)

    // Watch order updates
    stream, err := client.WatchOrder(context.Background(),
        &orderpb.WatchOrderRequest{
            Id: "order-id-here",
        })
    if err != nil {
        log.Fatalf("WatchOrder failed: %v", err)
    }

    // Receive real-time updates
    for {
        update, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            log.Fatalf("Error: %v", err)
        }
        log.Printf("Status: %s", update.ChangeDescription)
        log.Printf("New state: %v", update.Order.Status)
    }
}
```

## Real-Time Notifications (Node.js)

This example demonstrates server-side streaming for live notification feed:

```javascript
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const packageDef = protoLoader.loadSync('protos/notification.proto');
const notificationProto = grpc.loadPackageDefinition(packageDef).notification.v1;

const client = new notificationProto.NotificationService(
    'localhost:50051',
    grpc.credentials.createInsecure()
);

// Watch notifications
const stream = client.WatchNotifications({
    user_id: 'user-id-here',
    types: ['NOTIFICATION_TYPE_ORDER', 'NOTIFICATION_TYPE_PAYMENT'],
    min_priority: 'NOTIFICATION_PRIORITY_NORMAL'
});

stream.on('data', (notification) => {
    console.log('Notification:', notification.title);
    console.log('Message:', notification.message);
});

stream.on('error', (err) => {
    console.error('Error:', err);
});
```
