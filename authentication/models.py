# Import Django's models module to define database tables
from django.db import models


# Create a model to store revoked Access Tokens
class RevokedAccessToken(models.Model):

    # Store the unique ID (jti) of the revoked Access Token
    # unique=True prevents duplicate jti records in the database
    jti = models.CharField(
        max_length=255,
        unique=True
    )

    # Store when the Access Token expires
    # We will use this later to clean up expired revocation records
    expires_at = models.DateTimeField()

    # Automatically store the date and time when this record is created
    # This represents when the token was revoked in our application
    revoked_at = models.DateTimeField(
        auto_now_add=True
    )

    # Display the token's jti when this model object is printed
    def __str__(self):
        return self.jti