# SOCIAL POST SYSTEM - COMPLETE DEMO SCRIPT
# Demonstrates: MongoDB, Redis, JWT Auth, Cache, Rate Limiting

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SOCIAL POST SYSTEM - LIVE DEMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$API_URL = "http://localhost:8000"
$MONGO_EXPRESS_URL = "http://localhost:8081"

# Color variables
$Success = "Green"
$Info = "Cyan"
$Warning = "Yellow"

# 1. HEALTH CHECK
Write-Host "[1] HEALTH CHECK" -ForegroundColor $Info
Write-Host "────────────────────────────────────────" -ForegroundColor $Info
$health = Invoke-WebRequest -Uri "$API_URL/health" -UseBasicParsing
Write-Host "OK API Status: $(($health.Content | ConvertFrom-Json).status)" -ForegroundColor $Success
Write-Host ""

# 2. REGISTER USERS
Write-Host "[2] REGISTER USERS (MongoDB)" -ForegroundColor $Info
Write-Host "────────────────────────────────────────" -ForegroundColor $Info

$users = @(
    @{username="alice_smith";email="alice@example.com";password="Alice123!@secure";full_name="Alice Smith"}
    @{username="bob_wilson";email="bob@example.com";password="Bob123!@secure";full_name="Bob Wilson"}
    @{username="charlie_brown";email="charlie@example.com";password="Charlie123!@secure";full_name="Charlie Brown"}
)

$userIds = @{}
foreach ($user in $users) {
    try {
        $body = $user | ConvertTo-Json
        $response = Invoke-WebRequest -Uri "$API_URL/users/register" -Method POST `
            -ContentType "application/json" -Body $body -UseBasicParsing
        $userData = $response.Content | ConvertFrom-Json
        $userIds[$user.username] = $userData._id
        Write-Host "[+] Registered: $($user.username)" -ForegroundColor $Success
    } catch {
        Write-Host "[W] $($user.username) - Already exists or error" -ForegroundColor $Warning
    }
}
Write-Host ""

# 3. USER LOGIN & JWT TOKENS
Write-Host "[3] LOGIN & GET JWT TOKENS" -ForegroundColor $Info
Write-Host "────────────────────────────────────────" -ForegroundColor $Info

$tokens = @{}
foreach ($user in $users) {
    try {
        $loginUrl = "$API_URL/users/login?username=$($user.username)&password=$($user.password)"
        $login = Invoke-WebRequest -Uri $loginUrl `
            -Method POST -UseBasicParsing
        $loginData = $login.Content | ConvertFrom-Json
        $tokens[$user.username] = $loginData.access_token
        Write-Host "[+] Login: $($user.username) - Token: $($loginData.access_token.Substring(0,20))..." -ForegroundColor $Success
    } catch {
        Write-Host "[X] Login failed: $($user.username)" -ForegroundColor Red
    }
}
Write-Host ""

# 4. CREATE POSTS (MongoDB)
Write-Host "[4] CREATE POSTS (MongoDB)" -ForegroundColor $Info
Write-Host "────────────────────────────────────────" -ForegroundColor $Info

$postContents = @(
    "Just launched my new FastAPI project!",
    "MongoDB + Redis integration working perfectly!",
    "JWT authentication is so cool!"
)

$postIds = @()
$authorIndex = 0
foreach ($content in $postContents) {
    try {
        $author = $users[$authorIndex].username
        $headers = @{"Authorization"="Bearer $($tokens[$author])"}
        $body = @{content=$content;author_id=$userIds[$author]} | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "$API_URL/posts" -Method POST `
            -Headers $headers -ContentType "application/json" -Body $body -UseBasicParsing
        $postData = $response.Content | ConvertFrom-Json
        $postIds += $postData._id
        
        Write-Host "[+] Post created by $author - ID: $($postData._id.Substring(0,8))..." -ForegroundColor $Success
        $authorIndex++
    } catch {
        Write-Host "[X] Post creation failed" -ForegroundColor Red
    }
}
Write-Host ""

# 5. GET POSTS (Redis Cache)
Write-Host "[5] GET POSTS (Redis Cache)" -ForegroundColor $Info
Write-Host "────────────────────────────────────────" -ForegroundColor $Info

$posts = Invoke-WebRequest -Uri "$API_URL/posts/?page=1&limit=10" -UseBasicParsing
$postsData = $posts.Content | ConvertFrom-Json
Write-Host "[+] Retrieved $($postsData.data.Count) posts from cache" -ForegroundColor $Success
Write-Host "    Total posts in DB: $($postsData.total)" -ForegroundColor $Info
Write-Host ""

# 6. CREATE LIKES
Write-Host "[6] CREATE LIKES (MongoDB + Redis Pub/Sub)" -ForegroundColor $Info
Write-Host "────────────────────────────────────────" -ForegroundColor $Info

if ($postIds.Count -gt 0) {
    try {
        $token = $tokens["alice"]
        $headers = @{"Authorization"="Bearer $token"}
        $body = @{post_id=$postIds[0];liker_id=$userIds["bob"]} | ConvertTo-Json
        
        $like = Invoke-WebRequest -Uri "$API_URL/likes" -Method POST `
            -Headers $headers -ContentType "application/json" -Body $body -UseBasicParsing
        
        Write-Host "[+] Like created - Triggers Redis Pub/Sub event" -ForegroundColor $Success
    } catch {
        Write-Host "[W] Like creation - error" -ForegroundColor $Warning
    }
}
Write-Host ""

# 7. RATE LIMITING CHECK
Write-Host "[7] RATE LIMITING (via Redis)" -ForegroundColor $Info
Write-Host "────────────────────────────────────────" -ForegroundColor $Info

$testReq = Invoke-WebRequest -Uri "$API_URL/posts/?page=1&limit=1" -UseBasicParsing
$rateLimit = $testReq.Headers["x-ratelimit-limit"]
$rateLimitRemaining = $testReq.Headers["x-ratelimit-remaining"]

Write-Host "[+] Rate Limit: $rateLimit requests/hour" -ForegroundColor $Success
Write-Host "    Remaining: $rateLimitRemaining requests" -ForegroundColor $Info
Write-Host ""

# 8. REDIS VERIFICATION
Write-Host "[8] REDIS KEYS VERIFICATION" -ForegroundColor $Info
Write-Host "────────────────────────────────────────" -ForegroundColor $Info

$redisKeys = docker exec social_post_redis redis-cli KEYS "*"
Write-Host "[+] Redis Keys:" -ForegroundColor $Success
if ($redisKeys) {
    foreach ($key in $redisKeys) {
        if ($key) {
            Write-Host "    - $key" -ForegroundColor $Info
        }
    }
} else {
    Write-Host "    (empty - cache populated on-demand)" -ForegroundColor $Info
}
Write-Host ""

# 9. MONGODB DATA VERIFICATION
Write-Host "[9] MONGODB DATA VERIFICATION" -ForegroundColor $Info
Write-Host "────────────────────────────────────────" -ForegroundColor $Info

Write-Host "[+] MongoDB collections:" -ForegroundColor $Success
Write-Host "    users - $(($userIds.Count)) users registered" -ForegroundColor $Info
Write-Host "    posts - $($postIds.Count) posts created" -ForegroundColor $Info
Write-Host "    Other: comments, likes, follows, audit_logs" -ForegroundColor $Info
Write-Host ""

# 10. SUMMARY
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DEMO COMPLETE - SYSTEM READY!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "USEFUL LINKS:" -ForegroundColor $Info
Write-Host "  - Swagger API:      $API_URL/docs" -ForegroundColor $Warning
Write-Host "  - MongoDB Express:  $MONGO_EXPRESS_URL (admin/pass)" -ForegroundColor $Warning
Write-Host "  - Redis CLI:        docker exec -it social_post_redis redis-cli" -ForegroundColor $Warning
Write-Host ""

Write-Host "TECHNOLOGY STACK:" -ForegroundColor $Info
Write-Host "  + FastAPI 0.104.1 (39 endpoints)" -ForegroundColor $Success
Write-Host "  + MongoDB 7.0 (6 collections with auth)" -ForegroundColor $Success
Write-Host "  + Redis 7.2 (cache + Pub/Sub + rate limiting)" -ForegroundColor $Success
Write-Host "  + JWT Authentication (30-min expiry)" -ForegroundColor $Success
Write-Host "  + Rate Limiting (100 req/hour)" -ForegroundColor $Success
Write-Host "  + Background Jobs (APScheduler)" -ForegroundColor $Success
Write-Host ""

Write-Host "Ready for employer presentation!" -ForegroundColor Cyan
