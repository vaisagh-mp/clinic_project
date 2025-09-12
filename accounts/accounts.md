````markdown
# 📌 Project Documentation – Multi-Role Clinic System

## 🧑‍💻 Accounts Module

The **Accounts module** manages user authentication, authorization, and role-based access for the system. It uses **JWT (JSON Web Tokens)** for secure login, token refresh, and logout.

### Models

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("CLINIC", "Clinic"),
        ("DOCTOR", "Doctor"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
````

  - **ADMIN**: Super Admin / System Admin
  - **CLINIC**: Clinic Owner/Staff
  - **DOCTOR**: Doctor User

-----

### APIs

#### 1\. 🔑 Login API

  - **Endpoint**: `POST /api/accounts/login/`
  - **Description**: Authenticates a user and returns access & refresh tokens with a role-based redirect.

**Request Payload**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**

```json
{
  "access": "short_access_token_here",
  "refresh": "long_refresh_token_here",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@admin.com",
    "first_name": "",
    "last_name": "",
    "role": "ADMIN"
  },
  "redirect_to": "admin_panel:dashboard"
}
```

-----

#### 2\. 🔄 Refresh Token API

  - **Endpoint**: `POST /api/accounts/refresh/`
  - **Description**: Generates a new access token using a valid refresh token.

**Request Payload**

```json
{
  "refresh": "long_refresh_token_here"
}
```

**Response**

```json
{
  "access": "new_access_token_here"
}
```

-----

#### 3\. 🚪 Logout API

  - **Endpoint**: `POST /api/accounts/logout/`
  - **Description**: Blacklists the refresh token and logs the user out.

**Request Payload**

```json
{
  "refresh": "long_refresh_token_here"
}
```

**Response**

```json
{
  "message": "Logged out successfully."
}
```

-----

#### 4\. 👤 Current User (Profile) API

  - **Endpoint**: `GET /api/accounts/me/`
  - **Description**: Returns the details of the currently logged-in user.
  - **Authentication**: `Bearer` Access Token

**Headers**

```
Authorization: Bearer <access_token>
```

**Response**

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@admin.com",
  "first_name": "",
  "last_name": "",
  "role": "ADMIN"
}
```

-----

### Flow Summary

  - A user logs in, and the backend returns `access`, `refresh`, `user` data, and a `redirect_to` URL.
  - The frontend stores these tokens securely.
  - All protected API calls require an `Authorization` header with the `Bearer <access_token>`.
  - If the access token expires, the frontend calls the `/refresh/` endpoint to get a new one.
  - On logout, the frontend calls the `/logout/` endpoint and clears the stored tokens.

<!-- end list -->

