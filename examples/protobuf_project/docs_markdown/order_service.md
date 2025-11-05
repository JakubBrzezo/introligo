# Order Service

The Order Service orchestrates the complete order lifecycle from creation through delivery. It demonstrates cross-service integration by referencing both User and Product services.

## Order States

Orders progress through a well-defined state machine:

**Pending** → **Confirmed** → **Processing** → **Shipped** → **Delivered**

Terminal states: **Cancelled**, **Refunded**, **Failed**

## Key Capabilities

- **Order Creation** - Validates product availability and calculates totals
- **Address Management** - Separate shipping and billing addresses
- **State Machine** - Enforces valid state transitions
- **Real-Time Tracking** - Server-streaming RPC for live order updates
- **Carrier Integration** - Tracking numbers and delivery estimates
- **Cancellation & Refunds** - Order cancellation with automatic refund initiation
