# System Overview

The e-commerce platform is built with a microservices architecture where five independent services work together to provide a complete online shopping experience.

## Architecture

```
User Service ──┐
               │
Product Service├──→ Order Service ──→ Payment Service
               │
               └──→ Notification Service
```

Each service:
- Is independently deployable
- Communicates via gRPC
- Has its own data model
- Uses Protocol Buffers for type-safe APIs

## Services

- **User Service** - Manages user accounts, authentication, and authorization
- **Product Service** - Handles product catalog, inventory, and categories
- **Order Service** - Orchestrates the order lifecycle from creation to delivery
- **Payment Service** - Processes payments through multiple payment providers
- **Notification Service** - Sends notifications via email, SMS, push, and webhooks
