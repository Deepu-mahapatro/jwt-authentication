# JWT Security Best Practices, Rules and Mistakes to Avoid

## 1. Purpose

This document explains the security rules to follow when building JWT authentication systems.

The objective is to understand not only how to implement authentication, but also how to avoid common mistakes that can expose user accounts, authentication tokens, databases, and application secrets.

Each rule explains:

- What to do or avoid.
- Why the rule matters.
- The correct approach.
- How it applies to our Django JWT Authentication project.

---

## 2. Password Security

### Rule 1: Never Store Plaintext Passwords

**Wrong approach:**

```python
User.objects.create(
    username=username,
    password=password
)
```

Assigning a raw password directly to Django's `password` field does not hash it.

**Correct approach:**

```python
User.objects.create_user(
    username=username,
    password=password
)
```

Django's `create_user()` hashes the password using its configured password-hashing system.

**In our project:** We use `create_user()` inside `RegisterSerializer`.

### Rule 2: Never Store Passwords in JWT Payloads

**Wrong approach:**

```json
{
  "username": "deepu",
  "password": "MyPassword123"
}
```

**Why is it dangerous?**

A typical signed JWT is encoded, not encrypted. Anyone who obtains the token can decode its payload and read its contents.

**Correct approach:** Keep passwords out of JWTs. Include only the claims required by the application.

### Rule 3: Never Return Passwords in API Responses

Passwords must not appear in registration responses, login responses, logs, or error messages.

In our project, the serializer declares the password as `write_only=True`, preventing it from being included in serialized output.

---

## 3. JWT Token Security

### Rule 4: Never Put Secrets in JWT Payloads

Do not include:

- Passwords.
- Database credentials.
- JWT signing keys.
- API keys.
- Sensitive personal information that the client or anyone obtaining the token must not see.

The payload of a typical signed JWT is readable. A signature protects integrity; it does not provide confidentiality.

### Rule 5: Always Validate the Token

A backend must not trust a token merely because it looks like a JWT.

Validation should include the applicable checks for:

- Signature.
- Expiration.
- Expected token type.
- Relevant claims and intended use.
- Associated user and applicable permissions.
- Revocation status, when the application implements revocation.

**In our project:** Simple JWT handles standard token validation, while our custom authentication class checks the Access Token's `jti` against the revocation table.

### Rule 6: Protect Access Tokens and Refresh Tokens

Both tokens are sensitive credentials.

If an attacker obtains a usable token, they may be able to act as the associated user.

Use secure transport, avoid exposing tokens in logs, and choose appropriate token lifetimes and storage mechanisms.

### Rule 7: Use Appropriate Token Lifetimes

Access Tokens should generally have a limited lifetime appropriate to the application's risk and usability requirements.

Refresh Tokens need their own expiration and protection policies.

**In our project:** Simple JWT settings control the Access Token and Refresh Token lifetimes. The exact values must be checked in `config/settings.py`.

Short-lived tokens reduce exposure time, but they do not replace revocation, secure storage, or other protections.

---

## 4. Signing Key and Environment Security

### Rule 8: Never Expose the JWT Signing Key

Our project uses HS256, which relies on a shared secret for signing and verification.

If an attacker obtains that secret, they may be able to forge valid tokens.

**Correct approach:**

- Store the secret in an environment variable or appropriate secret manager.
- Never hardcode the production secret in source code.
- Use strong, unpredictable secrets.
- Restrict access to secrets.
- Rotate compromised secrets and plan key rotation appropriately.

### Rule 9: Never Commit `.env` to GitHub

Our `.env` file may contain:

- MySQL credentials.
- `JWT_SIGNING_KEY`.
- Email credentials or other private configuration.

Our `.gitignore` includes:

```gitignore
.env
.env.*
!.env.example
```

This helps prevent accidental commits of environment files.

**Important:** `.gitignore` does not remove a secret that has already been committed. If a secret is exposed, revoke or rotate it and remove it from repository history as appropriate.

### Rule 10: Use Different Secrets for Development and Production

A development signing key must not be reused as a production secret.

Production credentials should be managed separately and must never be shared through source control.

---

## 5. Token Storage and Transmission

### Rule 11: Use HTTPS in Production

HTTPS protects tokens and other request data while they travel between the client and server.

Without secure transport, an attacker on an insecure network may be able to intercept credentials.

### Rule 12: Do Not Send Tokens in URLs

Avoid putting tokens in query parameters or URL paths.

URLs may be recorded in browser history, server logs, analytics, and intermediary systems.

For our protected profile endpoint, the expected format is:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

### Rule 13: Choose Browser Token Storage Carefully

Browser storage decisions involve different risks.

- `localStorage` is accessible to JavaScript and therefore vulnerable to token theft if an XSS vulnerability exists.
- Cookies configured with `HttpOnly`, `Secure`, and an appropriate `SameSite` policy can reduce some risks.
- Cookie-based authentication must account for CSRF protection where applicable.

Neither storage option is automatically secure in every architecture. The choice depends on the client, threat model, and backend design.

Our current project uses the Bearer Authorization header; it does not implement a dedicated browser cookie-based token architecture.

---

## 6. Database and Application Security

### Rule 14: Use Django ORM or Parameterized SQL

Avoid constructing SQL queries by directly concatenating untrusted user input.

Unsafe SQL construction can lead to SQL injection.

**Correct approach:** Prefer Django ORM queries or parameterized SQL.

Our revocation check uses the Django ORM:

```python
RevokedAccessToken.objects.filter(
    jti=jti
).exists()
```

### Rule 15: Store Only the Data You Need

Avoid storing full authentication tokens when a token identifier is sufficient for the application's revocation design.

**In our project:** The `RevokedAccessToken` model stores the `jti`, expiry time, and revocation time rather than the entire Access Token.

### Rule 16: Restrict Database Access

- Use database accounts with only the permissions they need.
- Do not expose database credentials in source code.
- Protect database backups.
- Restrict access to production database servers.
- Use appropriate network and access controls.

### Rule 17: Handle Errors Safely

Authentication failures should not expose passwords, signing keys, full tokens, SQL statements, or unnecessary internal details.

Our logout view currently catches broad exceptions. A production-ready version should use more specific exception handling and carefully handle failures across the Refresh Token blacklist operation and Access Token revocation record creation.

---

## 7. Authentication, Authorization and API Protection

### Rule 18: Protect Every Private Endpoint

An endpoint is not protected merely because the application uses JWTs elsewhere.

Every private API must apply the appropriate authentication and permission checks.

**In our project:** The profile endpoint uses DRF's `IsAuthenticated` permission.

### Rule 19: Authentication Does Not Replace Authorization

A valid token identifies an authenticated user; it does not automatically grant permission to perform every operation.

For example, an authenticated normal user should not automatically receive administrative privileges.

Authorization must enforce the required roles, permissions, resource ownership, or policies.

Our current project does not yet implement a dedicated role-based access control system.

### Rule 20: Rate-Limit Sensitive Endpoints

Login and other sensitive authentication operations should have appropriate rate limits to reduce brute-force and abuse risks.

Production deployments should also consider monitoring, abuse detection, and account-protection policies.

Advanced authentication rate limiting is not currently a dedicated feature of our project.

---

## 8. Logout, Blacklisting and Revocation

### Rule 21: Understand That JWT Logout Is Not Automatic

A signed Access Token can remain valid after logout until its expiration time if the backend does not perform additional revocation checks.

Blacklisting a Refresh Token alone does not automatically invalidate already-issued Access Tokens.

### Rule 22: Revoke Tokens According to the Application's Requirements

Possible approaches include:

- Short-lived Access Tokens.
- Refresh Token blacklisting.
- Access Token revocation lists.
- Token version or session-based checks, depending on the design.

**In our project:** We use two separate mechanisms.

| Mechanism | Purpose |
|---|---|
| Simple JWT Refresh Token blacklist | Prevents reuse of blacklisted Refresh Tokens |
| `RevokedAccessToken` table | Allows our custom authentication class to reject specific revoked Access Tokens |

### Rule 23: Clean Up Expired Revocation Records

A revocation record is no longer needed for token rejection after the associated token has expired, assuming the application has no other reason to retain it.

Expired records should be cleaned up according to an appropriate retention policy.

Our current implementation records `expires_at`, but a dedicated automated cleanup job has not yet been implemented.

### Rule 24: Handle Logout Failures Consistently

Logout involves blacklisting a Refresh Token and recording Access Token revocation.

If one operation succeeds and the other fails, the system may be left in a partially completed state.

Production hardening should use carefully designed exception handling, appropriate transaction boundaries where applicable, and safe retry behavior.

---

## 9. Production Security Checklist

Before deploying a JWT authentication system, verify the following.

### Secrets and Passwords

- [ ] Passwords are hashed using Django's password-hashing system.
- [ ] Passwords and signing keys never appear in JWT payloads.
- [ ] `.env` is excluded from source control.
- [ ] Production secrets are strong and securely managed.
- [ ] Secrets are rotated if compromised.

### Tokens

- [ ] Token signatures and expiration are validated.
- [ ] The expected token type is checked.
- [ ] Access Tokens have appropriate lifetimes.
- [ ] Refresh Tokens are protected and their lifecycle is managed.
- [ ] Revocation and blacklist behavior is tested.
- [ ] Tokens are not exposed in URLs or logs.

### Django and Database

- [ ] HTTPS is enabled in production.
- [ ] `DEBUG` is disabled in production.
- [ ] Database permissions are restricted.
- [ ] Private APIs have appropriate authentication and authorization.
- [ ] Sensitive endpoints have appropriate rate limiting.
- [ ] Errors do not expose internal details.
- [ ] Dependencies are maintained and updated.
- [ ] Monitoring and security logging are configured appropriately.

### Project-Specific Follow-Up

- [ ] Improve logout exception handling.
- [ ] Ensure logout operations handle partial failures consistently.
- [ ] Implement cleanup for expired revocation records.
- [ ] Add automated tests for invalid, expired, and revoked tokens.
- [ ] Evaluate the performance impact of the database revocation check.

---

## 10. Final Takeaways

The most important JWT security rules are:

1. Never store plaintext passwords in the database.
2. Never put passwords or signing secrets in JWT payloads.
3. Remember that a signed JWT is normally readable, not encrypted.
4. Protect signing keys and environment variables.
5. Validate tokens instead of trusting their appearance.
6. Use HTTPS and protect tokens in transit and at rest.
7. Keep authentication separate from authorization.
8. Understand the difference between Refresh Token blacklisting and Access Token revocation.
9. Handle errors and database operations consistently.
10. Review security requirements before production deployment.

**Final takeaway:** Implementing JWT authentication correctly means more than issuing tokens. A secure backend must validate credentials and tokens, protect secrets, enforce permissions, manage token expiration and revocation, and handle failure scenarios safely.
