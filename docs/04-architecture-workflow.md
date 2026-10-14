# JWT Architecture, API Documentation and End-to-End Workflow

## 1. System Architecture

Our JWT Authentication project follows this architecture:

**Client / Postman ↔ Django REST Framework ↔ MySQL**

### Components and Responsibilities

| Component | Responsibility |
|---|---|
| Client / Postman | Sends API requests, submits credentials, and presents tokens |
| Django URL routing | Directs requests to the correct endpoint |
| Serializers | Validate registration and login data |
| Views | Execute registration, login, profile, refresh, and logout logic |
| Simple JWT | Creates and validates JWTs, refreshes tokens, and supports Refresh Token blacklisting |
| Custom JWT authentication | Checks whether an Access Token has been revoked |
| MySQL | Stores user records and Access Token revocation records |
| DRF permissions | Protect endpoints that require authentication |

### Architecture Flow

```text
Client / Postman
       |
       | HTTP Request
       v
config/urls.py
       |
       v
authentication/urls.py
       |
       v
Views and Serializers
       |
       v
JWT Authentication and Permissions
       |
       +------> Simple JWT validation
       |
       +------> MySQL revocation check
       |
       v
API Response
       |
       v
Client / Postman
```

The exact processing steps depend on the endpoint. For example, registration does not require an existing Access Token, while the protected profile endpoint requires authentication.

---

## 2. API Overview

Our project implements five API endpoints.

| No. | Method | Endpoint | Purpose |
|---|---|---|---|
| 1 | POST | `/api/auth/register/` | Register a new user |
| 2 | POST | `/api/auth/login/` | Authenticate credentials and issue tokens |
| 3 | GET | `/api/auth/profile/` | Access the authenticated user's profile |
| 4 | POST | `/api/auth/token/refresh/` | Obtain a new Access Token |
| 5 | POST | `/api/auth/logout/` | Revoke the Access Token and blacklist the Refresh Token |

The examples below describe the intended request formats and typical successful responses. Replace example values with your own test data when using Postman.

---

## 3. API 1 — User Registration

### Endpoint

`POST /api/auth/register/`

### Purpose

Creates a new user account in the application.

### Request Body

```json
{
  "username": "deepu",
  "email": "deepu@example.com",
  "password": "ExamplePassword123"
}
```

These are illustrative values. Use a unique username and an appropriate test password.

### Internal Workflow

1. The client submits registration information.
2. Django routes the request to the registration view.
3. `RegisterSerializer` validates the submitted fields.
4. The serializer's `create()` method calls Django's `create_user()`.
5. Django hashes the password before saving the user.
6. The API returns a response.

### Expected Result

A successful registration normally returns HTTP `201 Created` if configured that way in the view.

Invalid input may return HTTP `400 Bad Request`.

### Important Point

Registration creates the account; it does not automatically mean that the user has been issued JWTs. In our implementation, token issuance happens through the login endpoint.

---

## 4. API 2 — User Login

### Endpoint

`POST /api/auth/login/`

### Purpose

Verifies the user's credentials and issues an Access Token and Refresh Token.

### Request Body

```json
{
  "username": "deepu",
  "password": "ExamplePassword123"
}
```

### Internal Workflow

1. The client submits the username and password.
2. `LoginSerializer` validates the input.
3. Django's `authenticate()` checks the credentials.
4. If authentication fails, the API returns an error.
5. If authentication succeeds, Simple JWT generates the tokens.
6. The API returns the token information to the client.

### Token Generation

Our implementation uses:

```python
refresh = RefreshToken.for_user(user)
access_token = refresh.access_token
```

The Refresh Token is created first, and its `access_token` property generates the corresponding Access Token.

### Expected Result

A successful response contains the Access Token and Refresh Token, along with the response fields defined by our view.

The client must protect both tokens because they are credentials.

### Important Point

The login endpoint authenticates the user's credentials. Subsequent protected requests use the Access Token rather than repeatedly sending the password.

---

## 5. API 3 — Protected Profile

### Endpoint

`GET /api/auth/profile/`

### Purpose

Returns profile information for the authenticated user.

### Request Header

```http
Authorization: Bearer <ACCESS_TOKEN>
```

### Internal Workflow

1. The client sends a GET request with the Access Token.
2. Django REST Framework invokes the configured authentication class.
3. Simple JWT validates the token, including its signature and expiry.
4. Our custom authentication class checks the token's `jti` against `RevokedAccessToken`.
5. If the token is revoked, authentication fails.
6. Otherwise, normal user lookup and permission checks continue.
7. The view returns the authenticated user's profile.

### Successful Response Example

```json
{
  "message": "Profile retrieved successfully.",
  "user": {
    "id": 7,
    "username": "deepu",
    "email": "deepu@example.com"
  }
}
```

The user ID and profile information are illustrative.

### Expected Outcomes

| Condition | Typical result |
|---|---|
| Valid, accepted Access Token | `200 OK` |
| Missing or invalid credentials | Authentication failure |
| Expired Access Token | Authentication failure |
| Revoked Access Token | `401 Unauthorized` from our custom authentication flow |

### Important Point

The profile endpoint uses `IsAuthenticated`. A client cannot access the protected profile merely by knowing the endpoint URL.

---

## 6. API 4 — Refresh Access Token

### Endpoint

`POST /api/auth/token/refresh/`

### Purpose

Obtains a new Access Token using a valid Refresh Token.

### Request Body

```json
{
  "refresh": "<REFRESH_TOKEN>"
}
```

### Internal Workflow

1. The client submits the Refresh Token.
2. Simple JWT validates the token.
3. The blacklist mechanism checks whether it has been blacklisted.
4. If the Refresh Token is accepted, Simple JWT issues a new Access Token.
5. The response returns the new token.

### Successful Response Example

```json
{
  "access": "<NEW_ACCESS_TOKEN>"
}
```

The exact response fields depend on the configured Simple JWT behavior.

### Expected Outcomes

- A valid Refresh Token can obtain a new Access Token.
- An expired, malformed, or blacklisted Refresh Token is rejected.
- Refreshing a token does not itself revoke an already-issued Access Token.

### Important Point

Our current configuration sets `ROTATE_REFRESH_TOKENS` to `False`. Therefore, a successful refresh does not automatically issue a replacement Refresh Token.

---

## 7. API 5 — Logout and Token Revocation

### Endpoint

`POST /api/auth/logout/`

### Purpose

Makes the current Access Token unacceptable to our protected APIs and prevents reuse of the submitted Refresh Token.

### Request Body

Our implementation requires both tokens:

```json
{
  "access": "<ACCESS_TOKEN>",
  "refresh": "<REFRESH_TOKEN>"
}
```

### Internal Workflow

1. The client submits both tokens.
2. The logout view validates the Access Token.
3. It extracts the Access Token's `jti` and expiry time.
4. It parses and blacklists the Refresh Token.
5. It stores the Access Token's `jti` in `RevokedAccessToken`.
6. The API returns a success response if the operations complete.

### Expected Successful Response

```json
{
  "message": "Logout successful. Tokens revoked."
}
```

Our implementation returns HTTP `200 OK` on success.

### What Happens After Logout?

- The old Access Token is rejected by our custom authentication class because its `jti` is in the revocation table.
- The old Refresh Token is rejected by Simple JWT's blacklist mechanism when used for refresh.

### Important Implementation Consideration

Our current view catches broad exceptions and performs the blacklist and database operations separately. Production hardening should use more specific exception handling and ensure that partial failures are handled consistently.

---

## 8. Complete End-to-End Authentication Lifecycle

### Phase 1 — Registration

```text
Client
  |
  | POST /api/auth/register/
  v
Django Registration View
  |
  v
RegisterSerializer
  |
  v
Django User Creation
  |
  v
MySQL User Record
```

The user account is created, and Django stores the password hash rather than the plaintext password.

### Phase 2 — Login

```text
Client
  |
  | POST /api/auth/login/
  v
LoginSerializer
  |
  v
Django authenticate()
  |
  v
Simple JWT
  |
  +----> Access Token
  |
  +----> Refresh Token
  |
  v
Client Receives Tokens
```

### Phase 3 — Protected API Request

```text
Client
  |
  | GET /api/auth/profile/
  | Authorization: Bearer <ACCESS_TOKEN>
  v
Simple JWT Validation
  |
  v
Custom jti Revocation Check
  |
  +----> Revoked: Reject
  |
  +----> Not Revoked: Continue
                    |
                    v
              User Lookup
                    |
                    v
             IsAuthenticated
                    |
                    v
             Profile Response
```

### Phase 4 — Token Refresh

```text
Client
  |
  | POST /api/auth/token/refresh/
  | Refresh Token
  v
Simple JWT Validation
  |
  v
Blacklist Check
  |
  +----> Invalid / Blacklisted: Reject
  |
  +----> Accepted: Issue New Access Token
```

### Phase 5 — Logout

```text
Client
  |
  | POST /api/auth/logout/
  | Access Token + Refresh Token
  v
Logout View
  |
  +----> Store Access Token jti
  |
  +----> Blacklist Refresh Token
  |
  v
Logout Success Response
  |
  v
Subsequent Use of Old Tokens Is Rejected
```

---

## 9. Database Verification

After logout, we verified that the Access Token revocation record was stored in MySQL.

Our database is `jwt_auth_db`, and the custom table is `authentication_revokedaccesstoken`.

Example query:

```sql
USE jwt_auth_db;

SELECT
    id,
    jti,
    expires_at,
    revoked_at
FROM authentication_revokedaccesstoken;
```

The returned `jti` should correspond to the Access Token revoked during the logout test.

We also tested that the old Access Token was rejected by the profile API and that the old Refresh Token could not be used successfully for refresh.

Simple JWT's blacklist records are maintained separately from our custom Access Token revocation table.

---

## 10. End-to-End Testing Checklist

Use Postman to verify the following scenarios.

| Test | Expected behavior |
|---|---|
| Register with valid information | User is created |
| Log in with valid credentials | Access and Refresh Tokens are returned |
| Log in with invalid credentials | Authentication fails |
| Access profile with valid Access Token | Profile is returned |
| Access profile without a token | Request is rejected |
| Access profile with an expired token | Request is rejected |
| Refresh using a valid Refresh Token | New Access Token is returned |
| Refresh using a blacklisted Refresh Token | Request is rejected |
| Log out with both tokens | Revocation and blacklisting are recorded |
| Access profile using the revoked Access Token | Request is rejected |
| Query the revocation table | Corresponding `jti` record is present |

### Final Architecture Summary

Our project implements five connected APIs that cover registration, login, protected access, token renewal, and logout.

The main security distinction is that **Refresh Token blacklisting and Access Token revocation are separate mechanisms**. Simple JWT handles Refresh Token blacklist support, while our custom authentication class checks the Access Token's `jti` against MySQL.

This completes the documented architecture and API workflow for our JWT Authentication project.
