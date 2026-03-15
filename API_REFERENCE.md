# API REFERENCE - Danh Sách 39 Endpoints

## 📡 Base URL

```
http://localhost:8000
```

## 🔐 Authentication

Tất cả endpoints (trừ `/health`, `/users/register`, `/users/login`) yêu cầu JWT token:

```
Authorization: Bearer <token>
```

**Lấy token:**
```bash
POST /users/login?username=<user>&password=<pass>
```

---

## 👤 USERS - 6 Endpoints

### 1. Đăng Ký User
```
POST /users/register
Content-Type: application/json
```

**Request:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "John123!@secure",
  "full_name": "John Doe"
}
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

---

### 2. Đăng Nhập
```
POST /users/login?username=john&password=John123!@secure
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token expires in: 30 minutes**

---

### 3. Danh Sách Users (Pagination)
```
GET /users?page=1&page_size=10
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (default: 1)
- `page_size` (default: 10, max: 100)

**Response (200):**
```json
{
  "data": [
    {
      "_id": "60d5ec49c1234567890abcde",
      "username": "john",
      "email": "john@example.com",
      "full_name": "John Doe",
      "created_at": "2026-03-15T10:30:00Z"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 5,
  "total_pages": 1
}
```

---

### 4. Chi Tiết User
```
GET /users/{user_id}
Authorization: Bearer <token>
```

**Path Parameters:**
- `user_id` - MongoDB ObjectId

**Response (200):**
```json
{
  "_id": "60d5ec49c1234567890abcde",
  "username": "john",
  "email": "john@example.com",
  "full_name": "John Doe",
  "followers_count": 5,
  "following_count": 3,
  "created_at": "2026-03-15T10:30:00Z"
}
```

---

### 5. Cập Nhật User
```
PUT /users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "full_name": "John Smith",
  "email": "john.smith@example.com"
}
```

**Response (200):** Updated user object

---

### 6. Xóa User
```
DELETE /users/{user_id}
Authorization: Bearer <token>
```

**Response (204):** No content

---

## 📝 POSTS - 8 Endpoints

### 1. Tạo Post
```
POST /posts
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "content": "Hello World!",
  "author_id": "60d5ec49c1234567890abcde"
}
```

**Response (201):**
```json
{
  "_id": "60d5ec49c1234567890def012",
  "author_id": "60d5ec49c1234567890abcde",
  "content": "Hello World!",
  "created_at": "2026-03-15T10:35:00Z",
  "updated_at": "2026-03-15T10:35:00Z",
  "likes_count": 0,
  "comments_count": 0
}
```

---

### 2. Danh Sách Posts (Pagination + Cache)
```
GET /posts?page=1&page_size=10
```

**Query Parameters:**
- `page` (default: 1)
- `page_size` (default: 10, max: 100)

**Cache:** 60 seconds TTL in Redis

**Response (200):**
```json
{
  "data": [
    {
      "_id": "60d5ec49c1234567890def012",
      "author_id": "60d5ec49c1234567890abcde",
      "content": "Hello World!",
      "created_at": "2026-03-15T10:35:00Z",
      "likes_count": 5,
      "comments_count": 2
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 25,
  "total_pages": 3
}
```

---

### 3. Chi Tiết Post
```
GET /posts/{post_id}
```

**Response (200):** Post object with author details

---

### 4. Cập Nhật Post
```
PUT /posts/{post_id}
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "content": "Updated content!"
}
```

**Response (200):** Updated post object

---

### 5. Xóa Post
```
DELETE /posts/{post_id}
Authorization: Bearer <token>
```

**Response (204):** No content

---

### 6. Lấy Comments của Post
```
GET /posts/{post_id}/comments?page=1&page_size=10
```

**Response (200):** Paginated comments

---

### 7. Lấy Likes của Post
```
GET /posts/{post_id}/likes?page=1&page_size=10
```

**Response (200):** Paginated likes

---

### 8. Posts của User
```
GET /posts/author/{author_id}?page=1&page_size=10
```

**Response (200):** Paginated posts of author

---

## 💬 COMMENTS - 6 Endpoints

### 1. Tạo Comment
```
POST /comments
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "content": "Great post!",
  "post_id": "60d5ec49c1234567890def012",
  "author_id": "60d5ec49c1234567890abcde"
}
```

**Response (201):** Comment object

---

### 2. Danh Sách Comments
```
GET /comments?page=1&page_size=10
```

**Response (200):** Paginated comments

---

### 3. Chi Tiết Comment
```
GET /comments/{comment_id}
```

**Response (200):** Comment object

---

### 4. Cập Nhật Comment
```
PUT /comments/{comment_id}
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "content": "Updated comment!"
}
```

**Response (200):** Updated comment

---

### 5. Xóa Comment
```
DELETE /comments/{comment_id}
Authorization: Bearer <token>
```

**Response (204):** No content

---

### 6. Comments của Post
```
GET /comments/post/{post_id}?page=1&page_size=20
```

**Response (200):** Paginated comments for post

---

## ❤️ LIKES - 5 Endpoints

### 1. Thích Post
```
POST /likes
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "post_id": "60d5ec49c1234567890def012",
  "liker_id": "60d5ec49c1234567890abcde"
}
```

**Response (201):** Like object
**Triggers:** Redis Pub/Sub event `like.created`

---

### 2. Danh Sách Likes
```
GET /likes?page=1&page_size=10
```

**Response (200):** Paginated likes

---

### 3. Chi Tiết Like
```
GET /likes/{like_id}
```

**Response (200):** Like object

---

### 4. Bỏ Thích
```
DELETE /likes/{like_id}
Authorization: Bearer <token>
```

**Response (204):** No content

---

### 5. Likes của Post
```
GET /likes/post/{post_id}?page=1&page_size=50
```

**Response (200):** Paginated likes for post

---

## 👥 FOLLOWS - 6 Endpoints

### 1. Theo Dõi User
```
POST /follows
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "follower_id": "60d5ec49c1234567890abcde",
  "following_id": "60d5ec49c1234567890def012"
}
```

**Response (201):** Follow object
**Triggers:** Redis Pub/Sub event `user.followed`

---

### 2. Danh Sách Follows
```
GET /follows?page=1&page_size=10
```

**Response (200):** Paginated follows

---

### 3. Chi Tiết Follow
```
GET /follows/{follow_id}
```

**Response (200):** Follow object

---

### 4. Bỏ Theo Dõi
```
DELETE /follows/{follow_id}
Authorization: Bearer <token>
```

**Response (204):** No content

---

### 5. Followers của User
```
GET /follows/user/{user_id}/followers?page=1&page_size=20
```

**Response (200):** Paginated followers

---

### 6. Following của User
```
GET /follows/user/{user_id}/following?page=1&page_size=20
```

**Response (200):** Paginated following list

---

## 📋 AUDIT LOGS - 6 Endpoints

### 1. Danh Sách Audit Logs
```
GET /audit-logs?page=1&page_size=50
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "data": [
    {
      "_id": "60d5ec49c1234567890xyz123",
      "user_id": "60d5ec49c1234567890abcde",
      "action": "post_created",
      "resource_type": "post",
      "resource_id": "60d5ec49c1234567890def012",
      "timestamp": "2026-03-15T10:35:00Z"
    }
  ],
  "page": 1,
  "page_size": 50,
  "total": 150,
  "total_pages": 3
}
```

**Actions:** `user_created`, `user_updated`, `user_deleted`, `post_created`, `post_updated`, `post_deleted`, `comment_created`, `like_created`, `follow_created`

---

### 2. Chi Tiết Audit Log
```
GET /audit-logs/{log_id}
Authorization: Bearer <token>
```

**Response (200):** Audit log object

---

### 3. Audit Logs của User
```
GET /audit-logs/user/{user_id}?page=1&page_size=50
Authorization: Bearer <token>
```

**Response (200):** Paginated audit logs for user

---

### 4. Audit Logs của Resource
```
GET /audit-logs/resource/{resource_id}?page=1&page_size=50
Authorization: Bearer <token>
```

**Response (200):** Paginated audit logs for resource

---

### 5. Audit Logs By Action
```
GET /audit-logs/action/{action}?page=1&page_size=50
Authorization: Bearer <token>
```

**Valid actions:** user_created, post_created, comment_created, like_created, etc.

**Response (200):** Paginated logs for action

---

### 6. Xóa Audit Log
```
DELETE /audit-logs/{log_id}
Authorization: Bearer <token>
```

**Response (204):** No content

---

## ❤️ HEALTH CHECK - 1 Endpoint

### 1. API Status
```
GET /health
```

**Response (200):**
```json
{
  "status": "ok"
}
```

**No authentication required**

---

## 📖 DOCUMENTATION - 1 Endpoint

### 1. ReDoc (Alternative API Docs)
```
GET /redoc
```

Opens interactive API documentation via ReDoc

---

## 📊 Rate Limiting

**Limit:** 100 requests per hour per IP

**Headers:**
```
x-ratelimit-limit: 100
x-ratelimit-remaining: 85
x-ratelimit-reset: 1773560537
```

**Implementation:** Redis token bucket algorithm

---

## ⏱️ Response Codes

| Code | Meaning |
|------|---------|
| **200** | OK - Request successful |
| **201** | Created - Resource created |
| **204** | No Content - Delete successful |
| **400** | Bad Request - Invalid input |
| **401** | Unauthorized - Missing/invalid token |
| **403** | Forbidden - No permission |
| **404** | Not Found - Resource not found |
| **429** | Too Many Requests - Rate limit exceeded |
| **500** | Internal Server Error |

---

## 🔄 Redis Pub/Sub Events

Events triggered automatically:

| Event | When | Payload |
|-------|------|---------|
| `post.created` | Post created | `{post_id, author_id}` |
| `post.updated` | Post updated | `{post_id, updated_at}` |
| `post.deleted` | Post deleted | `{post_id}` |
| `comment.created` | Comment added | `{comment_id, post_id, author_id}` |
| `like.created` | User likes post | `{like_id, post_id, liker_id}` |
| `user.followed` | User followed | `{follower_id, following_id}` |

---

## 🔒 Authentication Example (curl)

```bash
# 1. Register
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"John123!@secure","full_name":"John Doe"}'

# 2. Login & get token
curl -X POST "http://localhost:8000/users/login?username=john&password=John123!@secure"

# 3. Use token in request
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X GET http://localhost:8000/posts \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📚 MongoDB Collections

Data persisted in MongoDB (6 collections):

- `users` - User accounts
- `posts` - Social posts
- `comments` - Post comments
- `likes` - Post likes
- `follows` - User follows
- `audit_logs` - Action logs

---

## ✨ Features

- ✅ JWT authentication (30-min expiry)
- ✅ Password hashing (bcrypt + salt)
- ✅ Rate limiting (100 req/hour)
- ✅ Redis caching (60s TTL)
- ✅ Pub/Sub events
- ✅ Audit logging
- ✅ Pagination
- ✅ CORS enabled
- ✅ Swagger UI
- ✅ ReDoc docs

---

## 🚀 Quick Test

```powershell
# Run auto demo
.\RUN_DEMO.ps1

# Or test manually
curl http://localhost:8000/health
curl -X POST http://localhost:8000/users/register ...
curl -X POST http://localhost:8000/users/login ...
curl -X GET http://localhost:8000/posts -H "Authorization: Bearer ..."
```

---

**Last Updated:** March 15, 2026  
**Status:** Production Ready ✅
