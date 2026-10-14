# Import Simple JWT's existing authentication class
from rest_framework_simplejwt.authentication import JWTAuthentication

# Import DRF's exception for rejecting authentication
from rest_framework.exceptions import AuthenticationFailed

# Import our model that stores revoked Access Token IDs
from .models import RevokedAccessToken


# Extend the existing JWT authentication process
class CustomJWTAuthentication(JWTAuthentication):

    # Django calls this after validating the token's signature and expiry
    def get_user(self, validated_token):

        # Extract the unique token ID (jti) from the validated JWT
        jti = validated_token.get("jti")

        # Check whether this token ID exists in our MySQL table
        is_revoked = RevokedAccessToken.objects.filter(
            jti=jti
        ).exists()

        # If the token has been revoked, reject the request
        if is_revoked:
            raise AuthenticationFailed(
                "This access token has been revoked.",
                code="token_revoked",
            )

        # Otherwise, continue with Simple JWT's normal user validation
        return super().get_user(validated_token)