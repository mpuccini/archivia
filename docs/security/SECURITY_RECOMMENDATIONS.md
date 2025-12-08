# Security Recommendations for Archivia

## Implemented Fixes ✅

### Critical Issues (FIXED)
1. **Removed hardcoded credentials** - All credentials now required via environment variables
2. **Fixed CORS configuration** - Removed wildcard `*` from allowed origins
3. **Added file magic number validation** - Validates actual file content, not just extensions
4. **Fixed temporary file cleanup** - Ensures cleanup even on errors
5. **Added XXE protection** - Using defusedxml and sanitizing all XML text nodes

### High Priority Issues (FIXED)
6. **Fixed exception handling** - Specific exceptions, no error detail exposure to users
7. **Added input validation** - Comprehensive Pydantic field validators with constraints
8. **Replaced print() with logging** - Proper structured logging throughout

## Pending Implementations ⚠️

### HttpOnly Cookie Authentication
**Status**: Requires frontend changes

**Current State**:
- JWT tokens returned in response body
- Frontend stores tokens in localStorage (vulnerable to XSS)

**Required Changes**:

**Backend** (`backend/app/routes/auth.py`):
```python
from fastapi import Response

@router.post("/login")
async def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    # ... authentication logic ...

    # Set HttpOnly cookie instead of returning token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access
        secure=True,  # Only send over HTTPS
        samesite="lax",  # CSRF protection
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {"message": "Login successful"}

# Update get_current_user to read from cookie instead of header:
async def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # ... verify token ...
```

**Frontend** (`frontend/src/stores/auth.js`):
```javascript
// Remove localStorage usage entirely
// Rely on automatic cookie sending by browser
async login(credentials) {
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        credentials: 'include',  // Important: send cookies
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(credentials)
    })
    // Token is now in HttpOnly cookie, not in response
}

// All API calls must include credentials: 'include'
```

**Benefits**:
- Immune to XSS attacks (JavaScript cannot access HttpOnly cookies)
- Automatic CSRF protection with SameSite attribute
- More secure token storage

**Drawbacks to Consider**:
- Requires HTTPS in production (secure flag)
- Need CSRF token for state-changing operations if using SameSite=None
- More complex mobile app integration

## Additional Recommendations

### 1. Rate Limiting
Add rate limiting to prevent brute force attacks:
```python
# Install: pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(...):
    ...
```

### 2. Password Requirements
Enforce strong passwords in `UserCreate` schema:
```python
@field_validator('password')
def validate_password(cls, v):
    if len(v) < 12:
        raise ValueError('Password must be at least 12 characters')
    if not re.search(r'[A-Z]', v):
        raise ValueError('Password must contain uppercase letter')
    if not re.search(r'[a-z]', v):
        raise ValueError('Password must contain lowercase letter')
    if not re.search(r'[0-9]', v):
        raise ValueError('Password must contain digit')
    return v
```

### 3. Security Headers
Add security headers to main.py:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### 4. Database Connection Pooling
Configure SQLAlchemy connection pooling for better performance:
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Maximum number of connections
    max_overflow=0,  # No additional connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600  # Recycle connections after 1 hour
)
```

### 5. Logging Configuration
Add structured logging with security event tracking:
```python
# Create app/utils/security_logger.py
import logging

security_logger = logging.getLogger('security')

def log_authentication_failure(username: str, ip: str, reason: str):
    security_logger.warning(
        "Authentication failure",
        extra={
            "username": username,
            "ip_address": ip,
            "reason": reason,
            "event_type": "auth_failure"
        }
    )

def log_authorization_failure(user_id: int, resource: str, action: str):
    security_logger.warning(
        "Authorization failure",
        extra={
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "event_type": "authz_failure"
        }
    )
```

## Environment Variables Required

Create a `.env` file with these variables before running:

```bash
# Required - No defaults
DATABASE_URL=postgresql://username:password@localhost:5432/archivia
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
MINIO_ACCESS_KEY=<your-minio-access-key>
MINIO_SECRET_KEY=<your-minio-secret-key>

# Optional - Have defaults
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
MINIO_ENDPOINT=localhost:9000
MINIO_BUCKET_NAME=archivia-files
MINIO_SECURE=false
```

## Monitoring & Alerting

Consider implementing:
- Failed login attempt monitoring
- Unusual file upload patterns
- Large file download tracking
- API rate limit violations
- Database query performance monitoring
