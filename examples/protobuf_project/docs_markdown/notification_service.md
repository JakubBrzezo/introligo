# Notification Service

The Notification Service demonstrates all four gRPC streaming patterns. It sends notifications across multiple channels and includes real-time bidirectional chat functionality.

## Streaming Patterns

This service showcases every gRPC streaming pattern:

1. **Unary RPC** - `SendNotification()` - Simple request-response
2. **Server Streaming** - `WatchNotifications()` - Real-time notification feed
3. **Client Streaming** - `BatchSend()` - Bulk notification upload
4. **Bidirectional Streaming** - `Chat()` - Real-time chat messaging

## Delivery Channels

Notifications can be sent through multiple channels simultaneously:

- **Push Notifications** - Mobile and web push
- **Email** - SMTP delivery
- **SMS** - Text message alerts
- **In-App** - Application notification bell
- **Webhook** - HTTP callbacks to external services

## Priority System

Notifications have four priority levels:
- **Low** - Can be batched or delayed
- **Normal** - Standard delivery (default)
- **High** - Immediate delivery
- **Urgent** - Bypasses do-not-disturb settings
