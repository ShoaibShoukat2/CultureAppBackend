# 🎯 Complete API Endpoints List

## Base URL
```
http://localhost:8000/api/
```

---

## 🔐 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | User login | No |
| POST | `/api/auth/logout/` | User logout | Yes |
| POST | `/api/auth/token/` | Get auth token | No |
| GET | `/api/auth/profile/` | Get current user profile | Yes |
| PUT/PATCH | `/api/auth/profile/` | Update user profile | Yes |

---

## 👨‍🎨 Artist Profile Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/artist-profiles/` | List all artists | No |
| GET | `/api/artist-profiles/{id}/` | Get artist details | No |
| POST | `/api/artist-profiles/` | Create artist profile | Yes (Artist) |
| PUT/PATCH | `/api/artist-profiles/{id}/` | Update artist profile | Yes (Owner) |
| DELETE | `/api/artist-profiles/{id}/` | Delete artist profile | Yes (Owner) |
| GET | `/api/artist-profiles/{id}/reviews/` | Get artist reviews | No |
| GET | `/api/artist-profiles/{id}/artworks/` | Get artist artworks | No |

**Query Parameters:**
- `?experience_level=beginner|intermediate|expert`
- `?is_available=true|false`
- `?min_hourly_rate=50`
- `?max_hourly_rate=200`
- `?search=keyword`
- `?ordering=rating|-rating`
- `?page=1&page_size=20`

---

## 🛍️ Buyer Profile Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/buyer-profiles/` | List all buyers | No |
| GET | `/api/buyer-profiles/{id}/` | Get buyer details | No |
| POST | `/api/buyer-profiles/` | Create buyer profile | Yes (Buyer) |
| PUT/PATCH | `/api/buyer-profiles/{id}/` | Update buyer profile | Yes (Owner) |
| DELETE | `/api/buyer-profiles/{id}/` | Delete buyer profile | Yes (Owner) |

---

## 📂 Category Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/categories/` | List all categories | No |
| GET | `/api/categories/{id}/` | Get category details | No |

---

## 🎨 Artwork Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/artworks/` | List all artworks | No |
| GET | `/api/artworks/{id}/` | Get artwork details | No |
| POST | `/api/artworks/` | Create artwork | Yes (Artist) |
| PUT/PATCH | `/api/artworks/{id}/` | Update artwork | Yes (Owner) |
| DELETE | `/api/artworks/{id}/` | Delete artwork | Yes (Owner) |
| POST | `/api/artworks/{id}/like/` | Like artwork | Yes |
| GET | `/api/artworks/featured/` | Get featured artworks | No |

**Query Parameters:**
- `?category=1`
- `?artwork_type=digital|physical|mixed`
- `?min_price=100`
- `?max_price=1000`
- `?is_featured=true`
- `?search=landscape`
- `?ordering=price|-price|created_at|views_count|likes_count`
- `?page=1&page_size=20`

---

## 💼 Job/Project Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/jobs/` | List all jobs | No |
| GET | `/api/jobs/{id}/` | Get job details | No |
| POST | `/api/jobs/` | Create job | Yes (Buyer) |
| PUT/PATCH | `/api/jobs/{id}/` | Update job | Yes (Owner) |
| DELETE | `/api/jobs/{id}/` | Delete job | Yes (Owner) |
| GET | `/api/jobs/{id}/bids/` | Get job bids | Yes |
| POST | `/api/jobs/{id}/hire/` | Hire artist | Yes (Buyer) |
| POST | `/api/jobs/{id}/complete/` | Complete job | Yes (Buyer) |

**Query Parameters:**
- `?status=open|in_progress|completed|cancelled`
- `?category=1`
- `?experience_level=entry|intermediate|expert`
- `?min_budget=200`
- `?max_budget=1000`
- `?search=logo design`
- `?ordering=budget_min|deadline|created_at`
- `?page=1&page_size=20`

---

## 💰 Bid Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/bids/` | List my bids | Yes |
| GET | `/api/bids/{id}/` | Get bid details | Yes |
| POST | `/api/bids/` | Create bid | Yes (Artist) |
| PUT/PATCH | `/api/bids/{id}/` | Update bid | Yes (Owner) |
| DELETE | `/api/bids/{id}/` | Delete bid | Yes (Owner) |

**Query Parameters:**
- `?status=pending|accepted|rejected`
- `?ordering=bid_amount|delivery_time|created_at`
- `?page=1&page_size=20`

---

## 🛠️ Equipment Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/equipment/` | List all equipment | No |
| GET | `/api/equipment/{id}/` | Get equipment details | No |
| POST | `/api/equipment/` | Create equipment | Yes (Admin) |
| PUT/PATCH | `/api/equipment/{id}/` | Update equipment | Yes (Admin) |
| DELETE | `/api/equipment/{id}/` | Delete equipment | Yes (Admin) |
| GET | `/api/equipment/in-stock/` | Get in-stock equipment | No |

**Query Parameters:**
- `?equipment_type=frame|paint|brush|canvas|other`
- `?min_price=10`
- `?max_price=500`
- `?in_stock=true`
- `?search=brush`
- `?ordering=price|stock_quantity`
- `?page=1&page_size=20`

---

## 📦 Order Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/orders/` | List my orders | Yes |
| GET | `/api/orders/{id}/` | Get order details | Yes |
| POST | `/api/orders/` | Create order | Yes |
| PUT/PATCH | `/api/orders/{id}/` | Update order | Yes (Owner) |
| POST | `/api/orders/{id}/confirm/` | Confirm order | Yes (Owner) |
| POST | `/api/orders/{id}/cancel/` | Cancel order | Yes (Owner) |

**Query Parameters:**
- `?order_type=artwork|equipment`
- `?status=pending|confirmed|shipped|delivered|cancelled`
- `?ordering=created_at|total_amount`
- `?page=1&page_size=20`

---

## 💳 Payment Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/payments/` | List my payments | Yes |
| GET | `/api/payments/{id}/` | Get payment details | Yes |
| POST | `/api/payments/` | Create payment | Yes |
| POST | `/api/payments/{id}/process/` | Process payment | Yes (Payer) |

**Query Parameters:**
- `?payment_method=jazzcash|bank_transfer|cash_on_delivery`
- `?status=pending|completed|failed|refunded`
- `?ordering=created_at|amount`
- `?page=1&page_size=20`

---

## 💬 Message Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/messages/` | List my messages | Yes |
| GET | `/api/messages/{id}/` | Get message details | Yes |
| POST | `/api/messages/` | Send message | Yes |
| PUT/PATCH | `/api/messages/{id}/` | Update message | Yes (Owner) |
| DELETE | `/api/messages/{id}/` | Delete message | Yes (Owner) |
| POST | `/api/messages/{id}/mark-read/` | Mark as read | Yes (Receiver) |
| GET | `/api/messages/conversations/` | Get conversations | Yes |

**Query Parameters:**
- `?is_read=true|false`
- `?job=1`
- `?ordering=created_at`
- `?page=1&page_size=20`

---

## ⭐ Review Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/reviews/` | List reviews | Yes |
| GET | `/api/reviews/{id}/` | Get review details | Yes |
| POST | `/api/reviews/` | Create review | Yes (Buyer) |
| PUT/PATCH | `/api/reviews/{id}/` | Update review | Yes (Owner) |
| DELETE | `/api/reviews/{id}/` | Delete review | Yes (Owner) |

**Query Parameters:**
- `?rating=1|2|3|4|5`
- `?ordering=created_at|rating`
- `?page=1&page_size=20`

---

## 📄 Contract Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/contracts/` | List my contracts | Yes |
| GET | `/api/contracts/{id}/` | Get contract details | Yes |
| POST | `/api/contracts/` | Create contract | Yes |
| PUT/PATCH | `/api/contracts/{id}/` | Update contract | Yes (Buyer) |
| POST | `/api/contracts/{id}/sign/` | Sign contract | Yes (Artist/Buyer) |

**Query Parameters:**
- `?status=draft|pending|active|completed|terminated`
- `?rights_type=display_only|reproduction|commercial|exclusive`
- `?ordering=created_at|amount`
- `?page=1&page_size=20`

---

## 🔔 Notification Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/notifications/` | List my notifications | Yes |
| GET | `/api/notifications/{id}/` | Get notification details | Yes |
| POST | `/api/notifications/{id}/mark-read/` | Mark as read | Yes |
| POST | `/api/notifications/mark-all-read/` | Mark all as read | Yes |
| GET | `/api/notifications/unread-count/` | Get unread count | Yes |

**Query Parameters:**
- `?notification_type=new_bid|bid_accepted|job_completed|payment_received|new_message|contract_signed`
- `?is_read=true|false`
- `?ordering=created_at`
- `?page=1&page_size=20`

---

## 📊 Dashboard & Analytics Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/dashboard/stats/` | Get dashboard stats | Yes |
| GET | `/api/analytics/` | List analytics | Yes (Admin) |
| GET | `/api/analytics/{id}/` | Get specific analytics | Yes (Admin) |
| POST | `/api/analytics/calculate-today/` | Calculate today's stats | Yes (Admin) |

---

## 🔍 Search Endpoint

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/search/?q=keyword` | Global search | No |

Searches across:
- Artworks
- Jobs
- Artists

---

## 📚 API Documentation Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/docs/` | Swagger UI Documentation |
| `/swagger/` | Swagger UI (Alternative) |
| `/redoc/` | ReDoc Documentation |

---

## 🎯 Quick Examples

### Register Artist
```bash
POST http://localhost:8000/api/auth/register/
Content-Type: application/json

{
    "username": "artist_john",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "user_type": "artist",
    "first_name": "John",
    "last_name": "Doe"
}
```

### Login
```bash
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
    "username": "artist_john",
    "password": "SecurePass123!"
}
```

### Create Artwork
```bash
POST http://localhost:8000/api/artworks/
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json

{
    "title": "Beautiful Sunset",
    "description": "A stunning sunset painting",
    "category_id": 1,
    "artwork_type": "digital",
    "price": "299.99"
}
```

### Search Jobs
```bash
GET http://localhost:8000/api/jobs/?search=logo&min_budget=200&status=open
```

### Create Bid
```bash
POST http://localhost:8000/api/bids/
Authorization: Token YOUR_TOKEN_HERE
Content-Type: application/json

{
    "job_id": 5,
    "bid_amount": "450.00",
    "delivery_time": 7,
    "cover_letter": "I have extensive experience..."
}
```

---

## 📝 Notes

1. **Authentication**: Include `Authorization: Token YOUR_TOKEN` header for authenticated endpoints
2. **Pagination**: Default page size is 20, max is 100
3. **Rate Limiting**: 100 requests/hour for anonymous, 1000/hour for authenticated users
4. **File Uploads**: Use `multipart/form-data` content type
5. **Date Format**: ISO 8601 format (`2025-12-31T23:59:59Z`)

---

## 🔗 Full URL Structure

```
project/
├── manage.py
├── project/
│   ├── settings.py
│   ├── urls.py (Main URLs - includes api/)
│   └── wsgi.py
└── your_app/
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── permissions.py
    ├── filters.py
    └── urls.py (App URLs - all API endpoints)
```