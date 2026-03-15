# SETUP GUIDE - Cài Đặt & Chạy Hệ Thống

## 📋 Yêu Cầu (Prerequisites)

- **Docker** & **Docker Compose** (đã cài sẵn)
- **PowerShell** (Windows) hoặc **Bash** (Linux/Mac)
- **Git** (để clone/pull code)

---

## ⚡ Cách 1: Chạy Demo Nhanh (2 phút)

### Bước 1: Mở PowerShell

```powershell
cd "d:\2026\Project\Social Post System"
```

### Bước 2: Chạy Demo Script

```powershell
.\RUN_DEMO.ps1
```

**Kết quả:**
```
[✓] HEALTH CHECK - API Status: ok
[✓] REGISTER USERS - alice, bob, charlie
[✓] LOGIN & GET JWT TOKENS - 3 tokens generated
[✓] CREATE POSTS - 3 posts created in MongoDB
[✓] GET POSTS - retrieved from Redis cache
[✓] CREATE LIKES - Redis Pub/Sub event triggered
[✓] RATE LIMITING - 100 requests/hour per IP
[✓] REDIS KEYS - rate_limit:x.x.x.x visible
[✓] MONGODB DATA - verified collections
DEMO COMPLETE - SYSTEM READY!
```

---

## ⚙️ Cách 2: Setup & Chạy Manual

### Bước 1: Khởi động containers

```powershell
cd "d:\2026\Project\Social Post System"
docker-compose up --build
```

**Output:**
```
[+] Running 4/4
 ✔ Container social_post_api              Started
 ✔ Container social_post_mongo            Started
 ✔ Container social_post_redis            Started
 ✔ Container social_post_mongo_express    Started
```

### Bước 2: Kiểm tra health check

```powershell
curl http://localhost:8000/health
```

**Response:**
```json
{"status": "ok"}
```

### Bước 3: Đăng ký user đầu tiên

```powershell
$body = @{
    username="alice"
    email="alice@example.com"
    password="Alice123!@secure"
    full_name="Alice Johnson"
} | ConvertTo-Json

curl -X POST http://localhost:8000/users/register `
  -H "Content-Type: application/json" `
  -d $body
```

**Response (201):**
```json
{
  "_id": "60d5ec49c1234567890abcde",
  "username": "alice",
  "email": "alice@example.com",
  "full_name": "Alice Johnson",
  "created_at": "2026-03-15T10:30:00Z"
}
```

### Bước 4: Đăng nhập & lấy token

```powershell
curl -X POST "http://localhost:8000/users/login?username=alice&password=Alice123!@secure"
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Bước 5: Tạo post (cần token)

```powershell
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
$headers = @{"Authorization"="Bearer $token"}
$body = @{
    content="Hello World!"
    author_id="60d5ec49c1234567890abcde"
} | ConvertTo-Json

curl -X POST http://localhost:8000/posts `
  -H $headers `
  -H "Content-Type: application/json" `
  -d $body
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

## 🔍 Kiểm Tra Hệ Thống

### MongoDB Express (xem dữ liệu)

```
URL: http://localhost:8081
Login: admin / pass
```

**Xem trong browser:**
1. Mở http://localhost:8081
2. Đăng nhập: admin / pass
3. Chọn database `social_post_db`
4. Xem collections: users, posts, comments, likes, follows, audit_logs

### Redis CLI (xem cache & keys)

```powershell
# Mở Redis CLI
docker exec -it social_post_redis redis-cli

# Xem tất cả keys
> KEYS *

# Xem chi tiết key
> GET rate_limit:172.18.0.1
> TTL rate_limit:172.18.0.1

# Thoát
> EXIT
```

### Swagger UI (test API)

```
URL: http://localhost:8000/docs
```

**Cách sử dụng:**
1. Mở http://localhost:8000/docs
2. Click nút 🔒 **Authorize**
3. Dán JWT token vào: `Bearer <token>`
4. Click **Authorize**
5. Thử các endpoints bằng **Try it out**

---

## 🛑 Dừng Hệ Thống

```powershell
docker-compose stop
```

**Xóa containers & volumes:**
```powershell
docker-compose down -v
```

---

## 🐛 Troubleshooting

### ❌ Port 8000/27017/6379 đã được sử dụng

```powershell
# Tìm process sử dụng port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### ❌ Docker không chạy

```powershell
# Khởi động Docker Desktop
& 'C:\Program Files\Docker\Docker\Docker Desktop.exe'

# Chờ đợi
Start-Sleep -Seconds 15

# Thử lại
docker-compose up
```

### ❌ MongoDB authentication failed

```powershell
# Kiểm tra docker-compose.yml
# Phải có:
# MONGO_INITDB_ROOT_USERNAME: admin
# MONGO_INITDB_ROOT_PASSWORD: password
# MONGODB_URL: mongodb://admin:password@mongo:27017
```

### ❌ API trả về 401 Unauthorized

```powershell
# Token hết hạn? Lấy token mới
curl -X POST "http://localhost:8000/users/login?username=alice&password=Alice123!@secure"

# Copy token mới vào Authorization header
```

---

## 📊 Endpoint Danh Sách

**39 endpoints tổng cộng:**

### Users (6)
- `POST /users/register` - Đăng ký
- `POST /users/login` - Đăng nhập
- `GET /users` - Danh sách
- `GET /users/{id}` - Chi tiết
- `PUT /users/{id}` - Cập nhật
- `DELETE /users/{id}` - Xóa

### Posts (8)
- `POST /posts` - Tạo
- `GET /posts` - Danh sách
- `GET /posts/{id}` - Chi tiết
- `PUT /posts/{id}` - Cập nhật
- `DELETE /posts/{id}` - Xóa
- `GET /posts/{id}/comments` - Bình luận
- `GET /posts/{id}/likes` - Lượt thích
- `GET /posts/author/{author_id}` - Theo tác giả

### Comments (6)
- `POST /comments` - Tạo
- `GET /comments` - Danh sách
- `GET /comments/{id}` - Chi tiết
- `PUT /comments/{id}` - Cập nhật
- `DELETE /comments/{id}` - Xóa
- `GET /comments/post/{post_id}` - Theo post

### Likes (5)
- `POST /likes` - Thích
- `GET /likes` - Danh sách
- `GET /likes/{id}` - Chi tiết
- `DELETE /likes/{id}` - Bỏ thích
- `GET /likes/post/{post_id}` - Lượt thích post

### Follows (6)
- `POST /follows` - Theo dõi
- `GET /follows` - Danh sách
- `GET /follows/{id}` - Chi tiết
- `DELETE /follows/{id}` - Bỏ theo dõi
- `GET /follows/user/{user_id}/followers` - Followers
- `GET /follows/user/{user_id}/following` - Following

### Audit Logs (6)
- `GET /audit-logs` - Danh sách
- `GET /audit-logs/{id}` - Chi tiết
- `GET /audit-logs/user/{user_id}` - Theo user
- `GET /audit-logs/resource/{resource_id}` - Theo resource
- `GET /audit-logs/action/{action}` - Theo action
- `DELETE /audit-logs/{id}` - Xóa

### Health (1)
- `GET /health` - API status

### ReDoc (1)
- `GET /redoc` - Alternative API docs

**Xem đầy đủ:** [API_REFERENCE.md](API_REFERENCE.md)

---

## ✅ Xác Minh Setup Thành Công

Chạy những check sau:

```powershell
# 1. API health
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# 2. MongoDB connection
curl http://localhost:8000/users
# Expected: {"data": [...]}

# 3. Rate limiting headers
curl http://localhost:8000/health -i | findstr x-ratelimit
# Expected: x-ratelimit-limit: 100, x-ratelimit-remaining: 99+

# 4. Redis cache
docker exec social_post_redis redis-cli DBSIZE
# Expected: (integer) 1+ (rate_limit key)
```

**Nếu tất cả pass ✅ → System ready!**

---

## 📞 Liên Hệ Support

Nếu gặp vấn đề:
1. Kiểm tra logs: `docker-compose logs api`
2. Xem troubleshooting section ở trên
3. Restart containers: `docker-compose restart`
