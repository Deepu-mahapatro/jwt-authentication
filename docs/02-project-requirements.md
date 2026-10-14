# Project Purpose, Requirements and Features

## 1. Project Overview

**Project Name:** JWT Authentication System

**Project Type:** Backend Authentication API

**Backend Framework:** Django

**API Framework:** Django REST Framework (DRF)

**Authentication Library:** Simple JWT

**Database:** MySQL

**Programming Language:** Python

### Project Description

The JWT Authentication System is a backend project that implements token-based authentication for REST APIs using Django REST Framework and JSON Web Tokens.

The system allows users to register and log in, access protected APIs using Access Tokens, refresh expired Access Tokens using Refresh Tokens, and log out by revoking the Access Token and blacklisting the Refresh Token.

The project also implements a custom JWT authentication class that checks whether an Access Token has been revoked by looking up its unique `jti` identifier in a MySQL database table.

The main objective is to understand and implement the complete JWT authentication lifecycle rather than simply generating tokens during login.

---

## 2. Problem Statement

Applications with protected APIs must verify the identity of users before allowing access to private resources.

A basic login implementation alone is insufficient because the application must also handle:

- Authentication of user credentials.
- Secure issuance of authentication tokens.
- Protection of private API endpoints.
- Token expiration and renewal.
- Logout and token invalidation.
- Rejection of invalid, expired, or revoked tokens.

JWT provides a token format for carrying verifiable claims, but the application must implement the necessary authentication, authorization, and token lifecycle rules.

Therefore, this project implements a Django-based JWT authentication workflow that addresses these requirements.

---

## 3. Project Objectives

The main objectives are:

1. Implement user registration and login APIs.
2. Authenticate user credentials using Django's authentication system.
3. Generate Access Tokens and Refresh Tokens using Simple JWT.
4. Protect private APIs using Django REST Framework authentication and permissions.
5. Implement an API for refreshing Access Tokens.
6. Implement Refresh Token blacklisting during logout.
7. Implement immediate Access Token revocation using the token's `jti`.
8. Store user and revocation-related information in MySQL.
9. Test successful and unsuccessful authentication scenarios using Postman.
10. Understand the complete request flow between the client, Django backend, JWT validation logic, and MySQL.

---

## 4. Technology Stack and Purpose

| Technology | Purpose in Our Project |
|---|---|
| Python | Main programming language |
| Django | Backend framework and application structure |
| Django REST Framework | REST APIs, serializers, responses, authentication integration, and permissions |
| Simple JWT | Access Token and Refresh Token creation, validation, refresh, and blacklist support |
| MySQL | Stores user information and our custom Access Token revocation records |
| Django ORM | Interacts with database models |
| Postman | Sends API requests and tests authentication scenarios |
| `python-dotenv` | Loads local environment variables from `.env` |
| `mysqlclient` | Provides the MySQL database driver used by Django |

### Why Django REST Framework?

DRF provides tools for building APIs, validating incoming data, generating HTTP responses, and protecting endpoints through authentication and permission classes.

### Why Simple JWT?

Simple JWT provides the underlying token implementation, including token creation, validation, refreshing, and Refresh Token blacklist functionality.

We extend its authentication behavior with our own revocation check.

### Why MySQL?

MySQL provides persistent storage for Django's user records and the custom revocation records required by our implementation.

### Why Postman?

Postman lets us test the entire authentication workflow independently of a frontend application.

---

## 5. Functional Requirements

Functional requirements describe what the system must do.

### FR-01: User Registration

**Endpoint:** `POST /api/auth/register/`

The system must accept the required registration information, validate it, and create a user account.

The password must be stored using Django's password-hashing mechanism rather than as plaintext.

### FR-02: User Login

**Endpoint:** `POST /api/auth/login/`

The system must validate the submitted username and password.

If the credentials are valid, it must issue an Access Token and a Refresh Token.

Invalid credentials must not result in successful authentication.

### FR-03: Protected Profile API

**Endpoint:** `GET /api/auth/profile/`

The system must require authentication before returning profile information.

A valid, accepted Access Token allows the request to proceed. Missing, invalid, expired, or revoked credentials must not grant access.

### FR-04: Access Token Refresh

**Endpoint:** `POST /api/auth/token/refresh/`

The system must accept a Refresh Token and issue a new Access Token when the Refresh Token passes validation and is eligible for use.

Blacklisted or otherwise invalid Refresh Tokens must be rejected.

### FR-05: Logout and Refresh Token Blacklisting

**Endpoint:** `POST /api/auth/logout/`

The system must accept both the Access Token and Refresh Token.

It must record the Access Token's `jti` as revoked and blacklist the Refresh Token.

### FR-06: Access Token Revocation

The system must check whether an Access Token's `jti` exists in the `RevokedAccessToken` table during custom JWT authentication.

If the token has been revoked, the protected API request must be rejected even when the token has not yet expired.

### FR-07: Error Handling

The system must return appropriate HTTP status codes for successful requests, invalid input, and authentication failures.

---

## 6. Non-Functional Requirements

Non-functional requirements describe how the system should behave and the qualities it should maintain.

### NFR-01: Security

- Passwords must not be stored in plaintext.
- The JWT signing secret must be kept outside source control.
- Protected endpoints must validate authentication.
- Tokens must not be exposed unnecessarily in logs or responses.

### NFR-02: Maintainability

Authentication logic should be organized into separate modules, including serializers, views, models, URL routing, and the custom authentication class.

### NFR-03: Reliability

Invalid, expired, and revoked tokens must not grant access to protected resources.

### NFR-04: Testability

The API should be testable using Postman and database queries.

### NFR-05: Configuration Management

Environment-specific settings, including database credentials and the JWT signing secret, should be supplied through environment variables.

### NFR-06: Performance Considerations

The custom Access Token revocation check performs a database lookup during authentication. This provides immediate revocation but adds database work to protected requests.

A production deployment should evaluate the performance and scaling implications of this approach.

---

## 7. Main Features Implemented

### Feature 1: User Registration

- Accepts registration details.
- Validates incoming data using `RegisterSerializer`.
- Creates users using Django's `create_user()`.
- Uses Django's password-hashing mechanism.

### Feature 2: User Login

- Validates input using `LoginSerializer`.
- Authenticates credentials using Django.
- Generates Access and Refresh Tokens using Simple JWT.

### Feature 3: Protected Profile

- Uses DRF's `IsAuthenticated` permission.
- Obtains the authenticated user from `request.user`.
- Returns profile information after authentication succeeds.

### Feature 4: Access Token Refresh

- Uses Simple JWT's token refresh functionality.
- Validates the Refresh Token.
- Returns a new Access Token when accepted.

### Feature 5: Refresh Token Blacklisting

- Uses Simple JWT's blacklist support.
- Prevents a blacklisted Refresh Token from being reused successfully.

### Feature 6: Immediate Access Token Revocation

- Extracts the Access Token's `jti` during logout.
- Stores the identifier in `RevokedAccessToken`.
- Checks the identifier in our custom authentication class.
- Rejects subsequent requests using that revoked token.

---

## 8. API Inventory

| HTTP Method | Endpoint | Responsibility |
|---|---|---|
| POST | `/api/auth/register/` | Create a user account |
| POST | `/api/auth/login/` | Authenticate credentials and issue tokens |
| GET | `/api/auth/profile/` | Return protected profile information |
| POST | `/api/auth/token/refresh/` | Obtain a new Access Token |
| POST | `/api/auth/logout/` | Revoke the Access Token and blacklist the Refresh Token |

The registration, login, and logout endpoints have their own validation and error-handling behavior. The profile endpoint requires authentication, and the refresh endpoint uses Simple JWT's token validation.

---

## 9. Project Architecture

The main architecture is:

**Client / Postman ↔ Django REST Framework ↔ MySQL**

### Client

The client submits credentials, receives tokens, and sends the Access Token when requesting protected resources.

### Django REST Framework

Django processes incoming requests, validates input, performs authentication, checks permissions, and generates responses.

### Simple JWT

Simple JWT handles token creation and standard token validation, refreshing, and blacklist support.

### Custom JWT Authentication

Our custom authentication class checks the Access Token's `jti` against the revocation table before continuing the normal user lookup.

### MySQL

MySQL stores user records and the custom Access Token revocation records. Simple JWT's blacklist application also maintains its own token-related database records.

---

## 10. Why Did We Implement Custom Access Token Revocation?

### The Problem

An Access Token can remain valid after logout if it has not expired and the backend only checks its signature and expiry.

Blacklisting a Refresh Token does not automatically invalidate an already-issued Access Token.

### Our Approach

We introduced a custom model:

`RevokedAccessToken`

It stores:

- `jti`: unique token identifier.
- `expires_at`: the token's natural expiry time.
- `revoked_at`: the time the revocation record was created.

During logout, the Access Token's `jti` is recorded. During authentication, the custom class checks whether that identifier exists in the table.

### Result

The application can reject the specific revoked Access Token immediately, rather than waiting for natural expiration.

### Trade-Off

This approach adds a database lookup during protected API authentication. Expired revocation records should also be cleaned up periodically, and production error handling should ensure logout operations remain consistent if one step fails.

---

## 11. Database Responsibilities

Our MySQL database is named `jwt_auth_db`.

The main database responsibilities are:

| Data | Purpose |
|---|---|
| Django user records | Store user account information and password hashes |
| `authentication_revokedaccesstoken` | Store Access Token revocation identifiers and timestamps |
| Simple JWT blacklist tables | Track blacklisted Refresh Tokens and associated token records |

The exact database schema is determined by the Django and Simple JWT migrations.

The project does not store plaintext passwords or the full Access Token in the custom revocation table.

---

## 12. Scope of the Current Implementation

### Implemented

- User registration.
- Username and password login.
- Access Token and Refresh Token issuance.
- Protected profile API.
- Access Token refresh.
- Refresh Token blacklisting.
- Custom Access Token revocation using `jti`.
- MySQL integration.
- Postman testing of the authentication lifecycle.

### Not Yet Implemented as Dedicated Features

- Role-based access control with separate user roles and permissions.
- Email verification or OTP-based login.
- Password reset and account recovery.
- Social login.
- Automated cleanup of expired revocation records.
- Automated CI/CD deployment.
- Production monitoring and advanced authentication rate limiting.

These features may be added later, but they should not be described as completed features of the current project.

---

## 13. Known Design Considerations

The current implementation is a practical learning project and a foundation for further production hardening.

Important considerations include:

1. The logout view uses broad exception handling that should be refined into specific validation and token exceptions.
2. The Refresh Token blacklist operation and Access Token revocation record creation should be handled consistently if one operation fails.
3. The revocation table needs a cleanup strategy for expired records.
4. Authentication and authorization are separate; more advanced permission rules would be required for role-based access.
5. Production deployment requires HTTPS, secure secret management, appropriate logging, rate limiting, and database access controls.

These are improvement areas, not reasons to disregard the working features already implemented.

---

## 14. Acceptance Criteria

The implementation satisfies its core objectives when the following behaviors are verified:

- A valid registration request creates a user account.
- A valid login request returns Access and Refresh Tokens.
- Invalid login credentials do not authenticate the user.
- A valid Access Token permits access to the protected profile API.
- An expired Access Token is rejected.
- A valid Refresh Token can obtain a new Access Token.
- A blacklisted Refresh Token cannot be used successfully for refresh.
- Logout records the Access Token's `jti` and blacklists the Refresh Token.
- The revoked Access Token is rejected on subsequent protected API requests.
- MySQL contains the corresponding revocation record.

These behaviors were tested during implementation using Postman and database verification.

---

## 15. Final Summary

The JWT Authentication System demonstrates the complete token-based authentication lifecycle using Django REST Framework, Simple JWT, and MySQL.

Its core features include user registration, login, protected API access, Access Token renewal, Refresh Token blacklisting, and custom Access Token revocation.

The key implementation decision is the use of a `jti`-based revocation table and a custom authentication class. This allows the backend to reject a revoked Access Token before its natural expiry.

The project provides a practical foundation for understanding authentication, token lifecycle management, database-backed revocation, and the security considerations involved in building backend APIs.

**Key takeaway:** The project does not merely generate JWTs; it implements and tests the major stages of the authentication lifecycle, including protected requests, refresh, logout, and immediate Access Token revocation.
