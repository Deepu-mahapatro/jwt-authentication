# JWT Authentication Implementation Guide

## 1. Project Structure and File Responsibilities

Our Django project separates configuration, API logic, validation, and authentication.

| File | Responsibility |
|---|---|
| `config/settings.py` | MySQL, DRF, environment variables, and JWT configuration |
| `config/urls.py` | Root URL routing |
| `authentication/models.py` | Defines the `RevokedAccessToken` model |
| `authentication/serializers.py` | Validates registration and login input |
| `authentication/views.py` | Implements registration, login, profile, refresh, and logout |
| `authentication/urls.py` | Maps API endpoints to views |
| `authentication/authentication.py` | Implements custom JWT authentication and revocation checks |
| `authentication/migrations/` | Stores database schema changes |
| `.env` | Stores local environment variables |
| `requirements.txt` | Records Python dependencies |

## 2. Environment and JWT Configuration

**File:** `config/settings.py`

The project loads environment variables from `.env` and configures Django REST Framework and Simple JWT.

Important configuration includes:

- Database connection to MySQL.
- JWT signing algorithm: `HS256`.
- JWT signing key loaded from an environment variable.
- Access Token and Refresh Token lifetimes.
- Bearer Authorization header configuration.
- Custom JWT authentication class.
- Simple JWT blacklist application.

The exact token lifetimes are controlled by `SIMPLE_JWT` settings.

**Purpose:** Keep application configuration separate from business logic and avoid hardcoding secrets in source code.

## 3. User Registration and Login Serializers

**File:** `authentication/serializers.py`

We implemented two serializers.

### `RegisterSerializer`

- Uses Django's `User` model.
- Accepts `username`, `email`, and `password`.
- Marks the password as write-only.
- Applies a minimum password length of eight characters.
- Uses `create_user()` to create the account and hash the password.

### `LoginSerializer`

- Accepts `username` and `password`.
- Marks the password as write-only.
- Preserves password whitespace during validation.

**Purpose:** Validate incoming API data before the views process it.

## 4. Registration and Login APIs

**File:** `authentication/views.py`

### Registration

`POST /api/auth/register/`

The view validates registration data through `RegisterSerializer` and creates a user when the data is valid.

### Login

`POST /api/auth/login/`

The view validates credentials using `LoginSerializer` and Django's `authenticate()` function.

When authentication succeeds, Simple JWT generates the tokens:

```python
refresh = RefreshToken.for_user(user)
access_token = refresh.access_token
```

The API returns the Access Token and Refresh Token to the client.

**Purpose:** Establish user identity and issue authentication credentials.

## 5. Protected Profile API

**Endpoint:** `GET /api/auth/profile/`

The profile view uses:

```python
@api_view(["GET"])
@permission_classes([IsAuthenticated])
```

The `IsAuthenticated` permission requires an authenticated request.

After authentication succeeds, the view uses `request.user` to obtain the authenticated user and returns the user's ID, username, and email.

**Purpose:** Demonstrate how JWT authentication protects a private API.

## 6. Custom JWT Authentication

**File:** `authentication/authentication.py`

We created `CustomJWTAuthentication` by extending Simple JWT's `JWTAuthentication` class.

The class overrides `get_user()` and checks whether the incoming token's `jti` exists in the `RevokedAccessToken` table.

```python
jti = validated_token.get("jti")

is_revoked = (
    RevokedAccessToken.objects
    .filter(jti=jti)
    .exists()
)

if is_revoked:
    raise AuthenticationFailed(
        "This access token has been revoked.",
        code="token_revoked",
    )
```

If the token is revoked, authentication fails. Otherwise, the parent class continues the normal user lookup.

The class is registered through `REST_FRAMEWORK` in `settings.py`.

**Purpose:** Add immediate Access Token revocation checking to Simple JWT's standard authentication flow.

## 7. Access Token Revocation Model

**File:** `authentication/models.py`

We implemented:

```python
class RevokedAccessToken(models.Model):
    jti = models.CharField(
        max_length=255,
        unique=True
    )
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(
        auto_now_add=True
    )
```

| Field | Purpose |
|---|---|
| `jti` | Identifies the specific revoked token |
| `expires_at` | Records the token's original expiration time |
| `revoked_at` | Records when the revocation entry was created |

We applied the database changes using Django migrations.

**Purpose:** Store revocation information so the custom authentication class can reject a previously revoked Access Token.

## 8. Token Refresh and Logout

### Token Refresh

**Endpoint:** `POST /api/auth/token/refresh/`

Simple JWT validates the submitted Refresh Token and issues a new Access Token when the request is accepted.

### Logout

**Endpoint:** `POST /api/auth/logout/`

Our logout view:

1. Requires both the Access Token and Refresh Token.
2. Parses the Access Token and extracts its `jti` and expiry.
3. Blacklists the Refresh Token.
4. Creates the Access Token revocation record.
5. Returns a success response if the operation completes.

**Purpose:** Prevent reuse of the logged-out Access Token and Refresh Token.

## 9. URL Routing and API Endpoints

The root URL configuration includes the authentication app under `/api/auth/`.

Our five endpoints are:

| Method | Endpoint | View or functionality |
|---|---|---|
| POST | `/api/auth/register/` | User registration |
| POST | `/api/auth/login/` | User login and token issuance |
| GET | `/api/auth/profile/` | Protected profile |
| POST | `/api/auth/token/refresh/` | Simple JWT token refresh |
| POST | `/api/auth/logout/` | Access Token revocation and Refresh Token blacklisting |

The root URLs direct requests to the application, and the application's URLs map each path to the appropriate view or Simple JWT endpoint.

## 10. Implementation Verification and End-to-End Flow

We tested the authentication lifecycle using Postman and verified revocation records in MySQL.

### Verified workflow

1. Register a user.
2. Log in and obtain both tokens.
3. Call the profile API with the Access Token.
4. Refresh the Access Token using the Refresh Token.
5. Log out by submitting both tokens.
6. Call the profile API again with the old Access Token.
7. Confirm that the revoked Access Token is rejected.
8. Try refreshing with the old Refresh Token and confirm that it is rejected.
9. Verify that the Access Token's `jti` was stored in MySQL.

### End-to-end architecture

**Client / Postman → Django URLs → Views and Serializers → JWT Authentication → MySQL**

Simple JWT handles standard token operations, while our custom authentication class checks the revocation table.

### Important Implementation Considerations

- Our custom revocation check adds a database query to authenticated requests.
- Expired revocation records need a cleanup strategy.
- Logout error handling and consistency between blacklisting and database recording can be improved for production.
- Role-based authorization and advanced rate limiting are not currently dedicated features of this implementation.

**Final takeaway:** Our implementation combines Django's user authentication, Simple JWT token management, DRF permissions, and a custom `jti`-based revocation check to support the complete JWT authentication lifecycle.
