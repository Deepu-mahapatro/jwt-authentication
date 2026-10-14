#  JWT Fundamentals and End-to-End Concepts

## 1. Purpose of This Document

The purpose of this document is to understand JSON Web Token (JWT) authentication from fundamentals to the complete authentication workflow.

After studying this document, I should be able to:

- Explain what JWT is and why it is used.
- Understand authentication and authorization.
- Explain JWT structure, claims, signatures, and expiration.
- Understand the difference between Access Tokens and Refresh Tokens.
- Explain how Django validates JWTs.
- Understand token refresh, logout, blacklisting, and revocation.
- Trace the complete flow between the client, Django backend, and MySQL database.
- Explain the JWT authentication workflow confidently in technical interviews.

---

## 2. What Is Authentication?

### Definition

Authentication is the process of verifying the identity of a user or client.

It answers the question:

**Who are you?**

### Example

Suppose a user wants to log in to an application.

1. The user submits a username and password.
2. The backend checks whether the credentials are valid.
3. If valid, the backend authenticates the user.
4. The backend issues authentication credentials, such as JWTs, according to the configured authentication flow.

### In Our Project

We implemented a login API using Django and Django REST Framework.

The backend authenticates the submitted credentials against Django's user system and issues an Access Token and a Refresh Token when authentication succeeds.

---

## 3. What Is Authorization?

### Definition

Authorization determines what an authenticated user is allowed to access or perform.

It answers the question:

**What are you allowed to do?**

### Example

Consider an application with two types of users:

- A normal user can view their own profile.
- An administrator can manage users.

Authentication establishes the user's identity. Authorization determines which operations that user may perform.

### Authentication vs Authorization

| Authentication | Authorization |
|---|---|
| Verifies identity | Checks access permissions |
| Answers "Who are you?" | Answers "What can you do?" |
| Uses credentials or tokens | Uses permissions, roles, ownership, or policies |
| Happens before access is granted | Determines whether a requested action is permitted |

### In Our Project

Our profile API uses `IsAuthenticated` to require an authenticated user.

This is an authentication requirement. It does not automatically implement a complete role-based authorization system.

---

## 4. What Is JWT?

### Definition

JWT stands for **JSON Web Token**.

It is a compact token format that allows information to be represented as JSON claims and protected by a cryptographic mechanism, such as a digital signature or a message authentication code.

JWTs are commonly used to carry authentication-related information between a client and a server.

### Why Do We Use JWT?

JWT authentication can help an application:

- Authenticate API requests without storing a traditional server-side login session for every request.
- Verify the integrity of a token.
- Carry claims such as a user identifier and token expiration.
- Protect APIs by requiring a valid token.
- Separate short-lived API access from longer-lived token renewal.

### Important Clarification

JWT is a token format, not a complete authentication system by itself.

An application still needs to decide:

- How users are authenticated.
- How tokens are issued and validated.
- How permissions are enforced.
- How tokens expire and refresh.
- How logout and revocation are handled.

---

## 5. How a JWT Is Structured

A typical signed JWT contains three parts separated by periods:

`HEADER.PAYLOAD.SIGNATURE`

### 5.1 Header

The header contains metadata about the token, such as the signing algorithm and token type.

Example:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

- `alg` identifies the algorithm.
- `typ` identifies the token format.

Our project uses the `HS256` signing algorithm.

### 5.2 Payload

The payload contains claims, which are statements about the token or its subject.

Example:

```json
{
  "user_id": 7,
  "token_type": "access",
  "jti": "example-token-id",
  "iat": 1790000000,
  "exp": 1790000300
}
```

This is an illustrative example, not a copy of an actual token from our project.

| Claim | Meaning |
|---|---|
| `user_id` | Identifies the user associated with the token |
| `token_type` | Indicates the token type, such as access or refresh |
| `jti` | Unique identifier for the token |
| `iat` | Time at which the token was issued |
| `exp` | Time at which the token expires |

The exact claims can vary depending on the token configuration and library.

### 5.3 Signature

The signature protects the integrity of a signed JWT.

With HS256, the signature is generated using a shared secret and a keyed-hash message authentication code.

Conceptually:

```text
Signature = HMAC-SHA256(
    encoded_header + "." + encoded_payload,
    signing_secret
)
```

If the signed content is modified, signature verification should fail.

### Important Security Rule

A signed JWT is not automatically encrypted.

Its header and payload are normally Base64URL-encoded, not hidden. Anyone who obtains a typical signed JWT can decode those sections.

Never put passwords, signing secrets, or sensitive personal information in a JWT payload.

---

## 6. What Is a Signing Key?

A signing key is a secret used to create and verify signed JWTs when using a symmetric algorithm such as HS256.

### Why Is It Needed?

The backend needs to determine whether a token was generated by a trusted issuer and whether its signed content has been modified.

### In Our Project

We configured:

```python
SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.environ["JWT_SIGNING_KEY"],
}
```

The signing key is read from an environment variable.

The real secret belongs in `.env` during local development and must not be committed to GitHub.

### Remember

If an attacker obtains the signing secret, they may be able to forge tokens. Protecting and rotating secrets is therefore an important security responsibility.

---

## 7. What Is an Access Token?

### Definition

An Access Token is a token presented by the client when requesting access to a protected API.

### Purpose

It allows the backend to authenticate API requests without asking the user to submit their password on every request.

### Example

The client sends:

```http
GET /api/auth/profile/
Authorization: Bearer <ACCESS_TOKEN>
```

The backend validates the token and, if authentication succeeds, allows the request to continue.

### In Our Project

We created an Access Token from the Refresh Token issued during login:

```python
refresh = RefreshToken.for_user(user)
access_token = refresh.access_token
```

The Access Token is used to access our protected profile endpoint.

### Important Point

An Access Token is not a password, but it is a sensitive credential. Anyone who obtains a usable token may be able to act as its associated user until it expires or is otherwise rejected.

---

## 8. What Is a Refresh Token?

### Definition

A Refresh Token is a credential used to obtain a new Access Token when the existing Access Token expires, provided the Refresh Token remains valid and is accepted by the backend.

### Why Do We Need It?

Without a Refresh Token, the application might need to ask the user to log in again whenever a short-lived Access Token expires.

Refresh Tokens support renewal without repeatedly collecting the user's password.

### In Our Project

We issue both tokens during login.

The refresh endpoint is:

`POST /api/auth/token/refresh/`

The client submits the Refresh Token, and Simple JWT validates it before issuing a new Access Token.

### Access Token vs Refresh Token

| Access Token | Refresh Token |
|---|---|
| Used to access protected APIs | Used to obtain a new Access Token |
| Usually has a shorter lifetime | Usually has a longer lifetime |
| Sent with protected API requests | Sent to the refresh endpoint |
| Can be rejected through our custom revocation check | Can be blacklisted using Simple JWT's blacklist support |

Refresh Tokens must be protected carefully because an attacker who steals a valid Refresh Token may be able to obtain new Access Tokens.

---

## 9. What Is the Bearer Token Scheme?

The Bearer scheme is a standard way to present a token in an HTTP Authorization header.

Example:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

The word `Bearer` tells the server how the client is presenting its credential.

The token itself follows the scheme name.

### In Our Project

We configured:

```python
"AUTH_HEADER_TYPES": ("Bearer",)
```

The client sends the Access Token in the Authorization header when calling the protected profile API.

### Security Rule

Never send tokens through URL query parameters when an Authorization header or another appropriate secure mechanism can be used. URLs may be recorded in browser history, access logs, or other systems.

---

## 10. What Is Token Validation?

Token validation is the process of checking whether a presented token should be accepted.

For a typical signed JWT access request, the backend must validate the signature and relevant claims, including expiration. It must also identify the associated user and enforce the application's authentication and authorization rules.

### Common Validation Checks

1. Is the token correctly formed?
2. Is its signature valid?
3. Has the token expired?
4. Is the token intended for the operation being performed?
5. Has the token been revoked or blacklisted where applicable?
6. Does the associated user exist and remain eligible for authentication?
7. Is the user allowed to perform the requested operation?

The exact checks depend on the library, configuration, and application.

### In Our Project

Simple JWT handles normal JWT validation.

Our custom authentication class adds another check: it looks up the token's `jti` in the `RevokedAccessToken` database table.

If the identifier is present in that table, our custom class rejects the request.

---

## 11. What Is a JWT Claim?

A claim is a piece of information carried in the JWT payload.

Claims can describe the token's subject, issue time, expiry time, intended audience, issuer, or other application-specific information.

### Common Claims

| Claim | Meaning |
|---|---|
| `sub` | Subject of the token |
| `iss` | Issuer of the token |
| `aud` | Intended audience |
| `iat` | Issued-at time |
| `exp` | Expiration time |
| `nbf` | Token must not be accepted before this time |
| `jti` | Unique token identifier |

Some are registered JWT claim names, while others, such as `user_id` and `token_type`, are commonly used library or application claims.

A claim's presence does not mean every application automatically validates it. Validation must be configured and implemented as appropriate.

---

## 12. What Is Token Expiration?

A JWT can contain an `exp` claim representing its expiration time.

After that time, a properly validating backend rejects the token.

### Example

Suppose an Access Token is issued at 10:00 AM and expires at 10:05 AM.

- At 10:02 AM, it may be accepted if all other checks pass.
- After 10:05 AM, it should be rejected as expired.

This example illustrates a five-minute lifetime, not a guarantee about the current value in our settings.

### Why Use Short-Lived Access Tokens?

Short-lived tokens reduce the period during which a stolen token can be used without needing revocation or other intervention.

However, expiration alone does not immediately invalidate a token when a user logs out.

That is why our project adds an explicit Access Token revocation mechanism.

---

## 13. What Is the Difference Between JWT Authentication and Session Authentication?

### Session Authentication

In a traditional session-based approach:

1. The user logs in.
2. The server creates a session.
3. The client receives a session identifier, commonly through a cookie.
4. The server uses session storage to look up the session on subsequent requests.

### JWT Authentication

In a typical JWT-based approach:

1. The user logs in.
2. The server issues a signed token.
3. The client presents the token with subsequent requests.
4. The server validates the token and applies its authentication rules.

### Comparison

| Session authentication | JWT authentication |
|---|---|
| Commonly relies on server-side session state | Can validate signed tokens without a traditional session lookup |
| Session data is maintained by the server | Claims are carried in the token |
| Session invalidation can be managed centrally | Immediate revocation may require additional state or another design |
| Commonly uses session cookies | Often uses an Authorization header for APIs |

JWT authentication is not automatically stateless in every implementation. Our project performs a MySQL lookup for Access Token revocation, so that additional check introduces server-side state.

---

## 14. What Is Token Blacklisting?

Token blacklisting means marking a token as unusable even if it has not yet reached its natural expiration time.

### In Our Project

We enabled Simple JWT's blacklist application for Refresh Tokens.

During logout, we call:

```python
refresh_token.blacklist()
```

The blacklist mechanism prevents the blacklisted Refresh Token from being used successfully for a new token refresh.

This mechanism is separate from our custom Access Token revocation table.

---

## 15. What Is Access Token Revocation?

Access Token revocation is the process of making an otherwise unexpired Access Token unacceptable before its normal expiration time.

### The Problem

A signed JWT does not automatically become invalid merely because the user logs out.

If the backend only checks its signature and expiry, an unexpired token may continue to work.

### Our Solution

We implemented a custom revocation mechanism using the JWT's `jti`.

The process is:

1. Extract the Access Token's `jti` during logout.
2. Store that identifier in the `RevokedAccessToken` table.
3. During protected API authentication, extract the incoming token's `jti`.
4. Query the database for that identifier.
5. Reject the request if the identifier has been revoked.

### Result

In our tested flow:

- The profile API succeeds before logout with a valid Access Token.
- Logout records the Access Token's `jti` and blacklists the Refresh Token.
- The old Access Token is rejected by the profile API.
- The old Refresh Token is rejected when used for refresh.

This is an important project feature because it demonstrates that token expiry and immediate token revocation solve different problems.

---

## 16. What Is the `jti` Claim?

The `jti` claim identifies a particular JWT.

Two tokens belonging to the same user can have different `jti` values.

### Why Do We Use It?

Our revocation system needs to identify the exact Access Token being revoked.

If we stored only the username, we could accidentally reject all tokens belonging to that user rather than just the specific token.

By storing the `jti`, our implementation can target an individual token.

### Example

```text
Access Token A
    jti = token-A

Access Token B
    jti = token-B
```

If `token-A` is revoked, the revocation record for `token-A` does not automatically revoke `token-B`.

This assumes both tokens are otherwise valid and no additional account-level restrictions apply.

---

## 17. Complete JWT Authentication Workflow in Our Project

Our main architecture is:

**Client / Postman ↔ Django REST Framework ↔ MySQL**

The client handles the tokens, Django validates and processes requests, and MySQL stores user records and revocation-related data.

### Step 1 — Registration

Endpoint:

`POST /api/auth/register/`

The client submits registration information.

Django validates the input through `RegisterSerializer` and creates the user using Django's `create_user()` method.

Django hashes the password before storing it.

### Step 2 — Login

Endpoint:

`POST /api/auth/login/`

The client submits a username and password.

Django authenticates the credentials and issues an Access Token and a Refresh Token when authentication succeeds.

### Step 3 — Access a Protected API

Endpoint:

`GET /api/auth/profile/`

The client sends the Access Token in the Authorization header.

Django validates the token and checks whether its `jti` has been revoked.

If authentication succeeds, the API returns the authenticated user's profile information.

### Step 4 — Refresh the Access Token

Endpoint:

`POST /api/auth/token/refresh/`

When the Access Token expires, the client submits the Refresh Token to the refresh endpoint.

Simple JWT validates the Refresh Token and issues a new Access Token if the request is accepted.

### Step 5 — Logout

Endpoint:

`POST /api/auth/logout/`

Our logout endpoint requires both the Access Token and the Refresh Token.

It records the Access Token's `jti` in the revocation table and blacklists the Refresh Token.

Subsequent protected API requests using the revoked Access Token fail the custom revocation check.

---

## 18. What Happens in Different Failure Scenarios?

| Scenario | Expected outcome |
|---|---|
| Valid, unexpired Access Token | Request may proceed if all other checks pass |
| Expired Access Token | Authentication fails |
| Invalid signature | Authentication fails |
| Revoked Access Token | Our custom authentication class rejects it |
| Blacklisted Refresh Token | Refresh request fails |
| Missing Access Token on a protected endpoint | Authentication is not established; the protected request is rejected |
| Valid authentication but insufficient permissions | The operation is denied by the applicable permission rules |

An HTTP `401 Unauthorized` response commonly indicates missing or invalid authentication. An HTTP `403 Forbidden` response commonly indicates that the request is understood but access is denied by permission rules, although exact behavior depends on the configured authentication and framework handling.

---

## 19. Security Rules to Remember

1. Never store plaintext passwords in the database.
2. Never include passwords or signing secrets in JWT payloads.
3. Remember that signed JWT payloads are normally readable, not encrypted.
4. Protect JWT signing keys and never commit real secrets to GitHub.
5. Use HTTPS in production.
6. Keep Access Tokens short-lived when appropriate for the application's threat model.
7. Protect Refresh Tokens and revoke or rotate them according to the application's design.
8. Validate signatures, expiry, token type, and relevant claims.
9. Do not confuse authentication with authorization.
10. Understand that JWT logout does not automatically invalidate every issued token.
11. Test invalid, expired, blacklisted, and revoked tokens.
12. Avoid logging passwords, signing keys, or full authentication tokens.

Detailed security rules and implementation guidance belong in Document 05: `05-jwt-security-best-practices.md`.

---

## 20. Key Terms for Quick Revision

| Term | Simple meaning |
|---|---|
| JWT | Standard format for carrying claims in a token |
| Authentication | Verifying identity |
| Authorization | Determining allowed actions |
| Access Token | Credential used to access protected APIs |
| Refresh Token | Credential used to obtain a new Access Token |
| Header | Contains token metadata |
| Payload | Contains claims |
| Signature | Protects token integrity and authenticity |
| Claim | A statement carried in the token |
| `exp` | Token expiration time |
| `iat` | Token issue time |
| `jti` | Unique token identifier |
| Bearer | HTTP scheme used to present the token |
| Blacklisting | Marking a token as unusable |
| Revocation | Invalidating a token before natural expiry |
| Signing key | Secret used for signing and verifying tokens with HS256 |

---

## 21. Final Mental Model

Remember this flow:

**User credentials → Django authentication → JWT issuance → Client stores and presents tokens → Django validates the Access Token → Protected API response**

When a token needs renewal:

**Refresh Token → Refresh endpoint → Validation → New Access Token**

When the user logs out in our project:

**Logout request → Access Token `jti` stored as revoked → Refresh Token blacklisted → Subsequent use of the old tokens rejected**

The key idea is that a JWT provides a verifiable token, but the application is still responsible for deciding whether the token should be accepted and what the authenticated user is allowed to do.

---

## 22. Final Takeaway

JWT authentication is not just about generating a token during login. It involves validating tokens on protected requests, managing expiration and renewal, protecting credentials, enforcing authorization, and handling logout and revocation correctly.

Our Django project implements these concepts through Django REST Framework, Simple JWT, MySQL, a custom authentication class, and an Access Token revocation table.

This document establishes the conceptual foundation for the remaining project documents.
