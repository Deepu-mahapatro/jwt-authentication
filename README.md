# 🔐 JWT Authentication System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/DRF-REST_Framework-A30000?style=for-the-badge&logo=django&logoColor=white" alt="Django REST Framework">
  <img src="https://img.shields.io/badge/JWT-Authentication-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT">
  <img src="https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/Postman-API_Testing-FF6C37?style=for-the-badge&logo=postman&logoColor=white" alt="Postman">
  <img src="https://img.shields.io/badge/Git-GitHub-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git">
</p>

<p align="center">
  <b>A practical authentication project implementing JWT-based authentication, protected REST APIs, token refresh, and token revocation using Django REST Framework and MySQL.</b>
</p>

---

## 📌 About the Project

This project demonstrates how **JSON Web Token (JWT) authentication** works in a Django REST Framework backend.

Users can register, log in, receive access and refresh tokens, access protected endpoints, refresh access tokens, and log out through a token revocation workflow.

The project focuses on understanding the complete authentication lifecycle, from credential verification to token validation and logout.

---

# 🎯 Project Objectives

- Understand JWT structure and the complete authentication workflow.
- Implement user registration and login.
- Generate and validate access and refresh tokens.
- Protect REST APIs using JWT authentication.
- Understand access-token expiration and refresh-token usage.
- Implement access-token revocation and refresh-token blacklisting.
- Integrate Django authentication with MySQL.
- Test authentication workflows using Postman.

---

# 🏗️ Architecture

```text
                CLIENT / POSTMAN
                       |
                       | Register / Login
                       | API Requests + JWT
                       v
               DJANGO REST FRAMEWORK
                       |
                JWT Authentication
                       |
              +--------+--------+
              |                 |
              v                 v
          User Model       Token Validation
              |                 |
              v                 v
             MySQL       Revocation Check
              |                 |
              +--------+--------+
                       |
                       v
                PROTECTED APIs
                       |
                       v
                    RESPONSE
```

### Core Principle

> **The client presents tokens, Django verifies them, and MySQL stores persistent user data and access-token revocation records.**

JWTs are signed tokens, not encrypted containers. Sensitive information should not be placed in their payloads.

---

# 🔄 JWT Authentication Workflow

```text
User Registration
        |
        v
User Login
        |
        v
Credential Verification
        |
        v
Access Token + Refresh Token
        |
        v
Protected API Request
        |
        v
JWT Verification
        |
        v
Authorized Response
        |
        v
Access Token Expires
        |
        v
Refresh Access Token
        |
        v
Logout
        |
        v
Revoke Access Token
+ Blacklist Refresh Token
```

---

# 🚀 Features Implemented

| Feature | Purpose |
|---|---|
| User Registration | Create a user account |
| User Login | Verify credentials and issue JWTs |
| Access Token | Authenticate protected API requests |
| Refresh Token | Obtain a new access token |
| Protected Profile API | Restrict access to authenticated users |
| Access Token Revocation | Reject revoked access tokens |
| Refresh Token Blacklisting | Reject blacklisted refresh tokens |
| Environment Configuration | Keep secrets and credentials outside source code |

---

# 🌐 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/auth/register/` | Register a user |
| `POST` | `/api/auth/login/` | Authenticate and receive tokens |
| `GET` | `/api/auth/profile/` | Retrieve the authenticated user's profile |
| `POST` | `/api/auth/token/refresh/` | Obtain a new access token |
| `POST` | `/api/auth/logout/` | Revoke tokens and log out |

### Example: Login Response

```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

Use the access token in protected requests:

```http
Authorization: Bearer <access_token>
```

---

# 🛡️ Security Highlights

- Django's password-hashing system handles user passwords.
- Environment variables are used for sensitive configuration.
- Protected endpoints require valid access tokens.
- Expired and revoked access tokens are rejected.
- Refresh-token blacklisting prevents reuse of blacklisted refresh tokens.
- Access-token revocation is checked against the database.
- Production deployments should use HTTPS, secure token storage, appropriate token lifetimes, and restricted database credentials.

---

# 🛠️ Tech Stack

### Backend
- Python
- Django
- Django REST Framework

### Authentication
- JSON Web Tokens (JWT)
- `djangorestframework-simplejwt`

### Database
- MySQL

### API Testing
- Postman

### Development Tools
- Git
- GitHub
- VS Code

---

# ⚙️ Setup

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd jwt-authentication
```

## 2. Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file in the project root, next to `manage.py`.

Add your MySQL credentials and JWT signing secret using the **exact variable names expected by `config/settings.py`**.

Example:

```env
DB_NAME=jwt_auth_db
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
JWT_SIGNING_KEY=your_secure_secret
```

Do not commit `.env` or real credentials to GitHub.

## 5. Apply Migrations

```bash
python manage.py migrate
```

## 6. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

# 📚 Documentation

| Document | Description |
|---|---|
| `docs/01-jwt-fundamentals.md` | JWT fundamentals and authentication concepts |
| `docs/02-project-requirements.md` | Project requirements and scope |
| `docs/03-implementation-guide.md` | Implementation and code structure |
| `docs/04-architecture-workflow.md` | Architecture and request flows |
| `docs/05-jwt-security-best-practices.md` | Security practices and checklist |

---

# 🧪 Testing

Authentication endpoints were tested using Postman.

Testing covered:

- User registration and login
- Valid and invalid credentials
- Access to protected APIs
- Missing, invalid, and expired access tokens
- Access-token refresh
- Logout and access-token revocation
- Refresh-token blacklisting

---

# 🎓 Learning Outcomes

- JWT structure and signature verification
- Stateless authentication
- Access tokens vs. refresh tokens
- Django REST Framework authentication and permissions
- Token expiration, revocation, and blacklisting
- MySQL integration with Django
- REST API testing and debugging
- Authentication security fundamentals

---

# ⭐ Key Takeaway

> **This project demonstrates the complete JWT authentication lifecycle—from user registration and token generation to protected API access, token refresh, and logout with token revocation.**
