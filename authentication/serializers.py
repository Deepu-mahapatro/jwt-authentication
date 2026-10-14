# Import Django's built-in User model.
# It represents the user accounts stored in our database.
from django.contrib.auth.models import User

# Import DRF's serializer tools.
from rest_framework import serializers


# Define a serializer specifically for user registration.
class RegisterSerializer(serializers.ModelSerializer):

    # Accept the password as input, but never include it
    # in the serializer's output.
    # For this example, require at least 8 characters.
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    # Configure which model and fields this serializer uses.
    class Meta:
        model = User
        fields = ["username", "email", "password"]

    # This method runs when serializer.save() creates a user.
    def create(self, validated_data):

        # create_user() hashes the password automatically
        # before saving the user to the configured database.
        return User.objects.create_user(**validated_data)
    
# Validates the data submitted to our login API.
class LoginSerializer(serializers.Serializer):

    # The username identifies the account.
    username = serializers.CharField()

    # The password is accepted as input but never
    # included in serialized output.
    # Preserve spaces because they may be part of a password.
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False
    )
