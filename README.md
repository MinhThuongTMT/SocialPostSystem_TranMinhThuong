# SOCIAL POST SYSTEM

Một **nền tảng mạng xã hội hoàn chỉnh** được xây dựng với **FastAPI**, **MongoDB**, và **Redis**.

---

## 🎯 Giới Thiệu Nhanh

**Social Post System** cung cấp:
- ✅ API REST hoàn chỉnh với 39 endpoints
- ✅ Xác thực JWT (30 phút expiry)
- ✅ Quản lý người dùng, bài viết, bình luận, lượt thích, theo dõi
- ✅ MongoDB với 6 collections + authentication
- ✅ Redis cache (60s TTL) + Pub/Sub events
- ✅ Rate limiting (100 requests/hour)
- ✅ Audit logs cho mọi hành động

**Tất cả đã triển khai xong và sẵn sàng demo!** 🚀

---

## 📚 Tài Liệu Chính

| File | Mục Đích |
|------|---------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | **Cài đặt & chạy hệ thống** |
| [API_REFERENCE.md](API_REFERENCE.md) | **Danh sách 39 API endpoints** |
| [RUN_DEMO.ps1](RUN_DEMO.ps1) | **Script demo tự động** |

**Chỉ cần đọc 3 file trên!** Không cần mở file khác.

---

## ⚡ Quick Start (30 giây)

```powershell
# 1. Mở folder project
cd "d:\2026\Project\Social Post System"

# 2. Chạy demo tự động
.\RUN_DEMO.ps1

# 3. Mở Swagger UI để test
# http://localhost:8000/docs
```

**Kết quả:**
- ✅ 3 users đăng ký thành công
- ✅ 3 posts tạo được
- ✅ MongoDB: dữ liệu lưu trữ
- ✅ Redis: cache + rate limiting active
- ✅ JWT authentication: working

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────┐
│  FastAPI (8000)     │ ← REST API, Swagger UI
├─────────────────────┤
│ MongoDB (27017)     │ ← 6 collections
│ + Authentication    │   (users, posts, comments, likes, follows, audit_logs)
│                     │
│ Redis (6379)        │ ← Cache (60s TTL)
│ + Pub/Sub Events    │   Rate limiting (100 req/hr)
│ + Rate Limiting     │   Event channels
└─────────────────────┘
```

---

## 💾 MongoDB Collections

| Collection | Dữ Liệu |
|-----------|--------|
| `users` | ID, username, email, password_hash, full_name, created_at |
| `posts` | ID, content, author_id, created_at, likes_count, comments_count |
| `comments` | ID, content, post_id, author_id, created_at |
| `likes` | ID, post_id, user_id, created_at |
| `follows` | ID, follower_id, following_id, created_at |
| `audit_logs` | ID, user_id, action, resource_type, resource_id, timestamp |

---

## 🔒 Bảo Mật

- **JWT Token**: Header `Authorization: Bearer <token>`
- **Rate Limiting**: 100 requests/hour per IP (via Redis)
- **Password**: Bcrypt hash + salt
- **CORS**: Cho phép tất cả origins (development mode)

---

## 📊 Ví Dụ Request/Response

**1. Đăng ký user:**
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "John123!@secure",
    "full_name": "John Doe"
  }'
```

**Response (201):**
```json
{
  "_id": "60d5ec49c1234567890abcde",
  "username": "john",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2026-03-15T10:30:00Z"
}
```

**2. Đăng nhập:**
```bash
curl -X POST "http://localhost:8000/users/login?username=john&password=John123!@secure"
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**3. Tạo bài viết:**
```bash
curl -X POST http://localhost:8000/posts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello World!",
    "author_id": "60d5ec49c1234567890abcde"
  }'
```

---

## 🔍 Kiểm Tra Hệ Thống

**MongoDB Express** (xem dữ liệu):
```
http://localhost:8081
Login: admin / pass
```

**Redis CLI** (xem cache):
```powershell
docker exec -it social_post_redis redis-cli
> KEYS *
> GET <key>
```

**Swagger UI** (test API):
```
http://localhost:8000/docs
```

---

## 📋 Danh Sách Endpoints (39 tổng cộng)

```
👤 Users (6 endpoints)
  POST   /users/register       - Đăng ký user mới
  POST   /users/login          - Đăng nhập
  GET    /users/{id}           - Chi tiết user
  GET    /users                - Danh sách users
  PUT    /users/{id}           - Cập nhật user
  DELETE /users/{id}           - Xóa user

📝 Posts (8 endpoints)
  POST   /posts                - Tạo bài viết
  GET    /posts                - Danh sách posts (pagination)
  GET    /posts/{id}           - Chi tiết post
  PUT    /posts/{id}           - Cập nhật post
  DELETE /posts/{id}           - Xóa post
  ...

💬 Comments, ❤️ Likes, 👥 Follows, 📋 Audit Logs
  ... (mỗi section ~6-8 endpoints)

❤️ Health Check
  GET    /health               - API status
```

**Xem đủ danh sách:** [API_REFERENCE.md](API_REFERENCE.md)

---

## 🎬 Demo Tự Động

```powershell
.\RUN_DEMO.ps1
```

Script sẽ tự động:
1. ✅ Kiểm tra health check
2. ✅ Tạo 3 users
3. ✅ Login & lấy JWT tokens
4. ✅ Tạo 3 posts
5. ✅ Get posts từ cache
6. ✅ Tạo likes
7. ✅ Hiển thị rate limiting
8. ✅ Kiểm tra Redis & MongoDB

---

## ⚙️ Tech Stack

| Thành Phần | Phiên Bản | Mục Đích |
|-----------|----------|---------|
| **FastAPI** | 0.104.1 | Web framework async |
| **Python** | 3.11 | Runtime |
| **MongoDB** | 7.0 | NoSQL database |
| **Redis** | 7.2 | Cache + Pub/Sub |
| **Docker** | Latest | Containerization |
| **Motor** | 3.3.2 | Async MongoDB driver |
| **redis-asyncio** | Latest | Async Redis client |
| **PyJWT** | Latest | JWT tokens |
| **Bcrypt** | Latest | Password hashing |

---

## 📖 Hướng Dẫn Chi Tiết

Để **cài đặt & chạy toàn bộ** từ đầu:
→ **[Xem SETUP_GUIDE.md](SETUP_GUIDE.md)**

Để **xem chi tiết mỗi endpoint**:
→ **[Xem API_REFERENCE.md](API_REFERENCE.md)**

---

## ✅ Các Yêu Cầu Đã Hoàn Thành

- ✅ API REST với 39 endpoints
- ✅ MongoDB + 6 collections + authentication
- ✅ Redis cache + Pub/Sub + rate limiting
- ✅ JWT authentication system
- ✅ Background jobs (APScheduler)
- ✅ Audit logs cho mọi hành động
- ✅ Rate limiting (100 req/hour)
- ✅ Docker deployment
- ✅ Swagger UI + authentication
- ✅ Demo script tự động
- ✅ Đầy đủ documentation

---

## 🚀 Sẵn Sàng Demo!

Hệ thống hoàn toàn sẵn sàng để:
- ✅ Chạy demo trực tiếp
- ✅ Test tất cả endpoints
- ✅ Kiểm tra MongoDB & Redis
- ✅ Trình bày trước employer

**Bắt đầu ngay:** Chạy `.\RUN_DEMO.ps1` ✅
