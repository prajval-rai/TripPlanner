# users/views.py
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Profile  # make sure your Profile model has OneToOneField(User)

@api_view(['POST'])
def register_user(request):
    """
    Register a new user and create a linked profile atomically.
    """
    data = request.data

    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'contact', 'password']
    missing_fields = [f for f in required_fields if f not in data or not data[f]]
    if missing_fields:
        return Response(
            {'error': f'Missing required fields: {", ".join(missing_fields)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            # Create Django user
            user_obj = User.objects.create_user(
                username=data["email"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                password=data["password"]
            )

            # Create linked Profile
            profile_obj = Profile.objects.create(
                user=user_obj,  # OneToOneField to User
                contact=data['contact']
            )

        # Return only safe user info
        response_data = {
            'first_name': user_obj.first_name,
            'last_name': user_obj.last_name,
            'email': user_obj.email,
            'contact': profile_obj.contact
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Catch any DB or integrity errors
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def login_user(request):
    """
    Authenticate user using email & password and return profile data.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Please provide email and password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=email, password=password)  # Django auth

    if user:
        try:
            # Access related profile safely
            profile = user.profile
            response_data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'contact': profile.contact
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            # If profile missing
            return Response(
                {'error': 'Profile does not exist for this user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
