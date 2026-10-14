# Import DRF's response and HTTP status utilities.
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated


# Import token classes for validating and revoking JWTs
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

# Import the model that stores revoked Access Tokens
from .models import RevokedAccessToken

# Convert the JWT expiry timestamp into a Python datetime
from datetime import datetime, timezone as dt_timezone

# Import our registration serializer.
from .serializers import RegisterSerializer

#Import our login serializer 
from .serializers import LoginSerializer

from rest_framework.exceptions import AuthenticationFailed


# Allow this endpoint to receive only HTTP POST requests.
@api_view(["POST"])
def register_user(request):

    # Pass the incoming JSON data to the serializer.
    serializer = RegisterSerializer(data=request.data)

    # Validate the submitted username, email and password.
    if serializer.is_valid():

        # Create the user.
        # Our serializer's create() method calls create_user(),
        # which hashes the password before saving it.
        user = serializer.save()

        # Return a success response without exposing the password.
        return Response(
            {
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    # If validation fails, return the validation errors.
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )

# Handle login requests sent using HTTP POST.
@api_view(["POST"])
def login_user(request):

    # Validate the structure of the submitted login data.
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        # Return validation errors if fields are missing or invalid.
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Read the validated username and password.
    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    # Django checks the submitted password against the stored hash.
    user = authenticate(
        request=request,
        username=username,
        password=password,
    )
    # If authentication fails, reject the login.
    if user is None:
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    
    # Step 1: Create a Refresh Token for the authenticated user.
    refresh = RefreshToken.for_user(user)

    # Step 2: Generate an Access Token from the Refresh Token.
    access_token = refresh.access_token
    
    # DEBUG: Display the Access Token's Payload in the terminal.
    print("ACCESS TOKEN PAYLOAD:", access_token.payload)

    # DEBUG: Display the Refresh Token's Payload in the terminal.
    print("REFRESH TOKEN PAYLOAD:", refresh.payload)

    # Step 3: Return both tokens to the client.
    return Response(
        {
            "message": "Login successful.",
            "username": user.username,

            # Convert token objects into strings for the JSON response.
            "access": str(access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_200_OK,
    )
    
# Allow only HTTP GET requests.
@api_view(["GET"])

# Require the request to have an authenticated user.
@permission_classes([IsAuthenticated])
def profile_user(request):

    # JWTAuthentication identifies the user from the validated token.
    user = request.user

    # Return basic information about the authenticated user.
    return Response(
        {
            "message": "Profile retrieved successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        },
        status=status.HTTP_200_OK,
    )
    

# Allow logout requests only through HTTP POST.
@api_view(["POST"])
def logout_user(request):

    # Receive both tokens from the client
    access_token_string = request.data.get("access")
    refresh_token_string = request.data.get("refresh")

    # Both tokens are required for this logout implementation
    if not access_token_string or not refresh_token_string:
        return Response(
            {
                "error": "Both access and refresh tokens are required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Step 1: Validate the Access Token
        # This checks its signature and expiration
        access_token = AccessToken(access_token_string)

        # Extract the unique ID of this Access Token
        jti = access_token["jti"]

        # Convert its Unix expiry timestamp to a datetime
        expires_at = datetime.fromtimestamp(
            access_token["exp"],
            tz=dt_timezone.utc,
        )

        # Step 2: Validate the Refresh Token
        refresh_token = RefreshToken(refresh_token_string)

        # Step 3: Blacklist the Refresh Token
        refresh_token.blacklist()

        # Step 4: Store the Access Token's jti in MySQL
        # get_or_create prevents duplicate records for the same jti
        RevokedAccessToken.objects.get_or_create(
            jti=jti,
            defaults={
                "expires_at": expires_at,
            },
        )

    except Exception:
        # Return an error if either token is invalid or unusable
        return Response(
            {"error": "Logout failed. Check your tokens and try again."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Step 5: Confirm that logout completed
    return Response(
        {"message": "Logout successful. Tokens revoked."},
        status=status.HTTP_200_OK,
    )