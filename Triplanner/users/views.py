# users/views.py
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Profile,Follower,FollowRequest  # make sure your Profile model has OneToOneField(User)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from notifications.models import Notifications
from django.db.models import Count,Q
from .serializers import UserSearchSerializer

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
@permission_classes([AllowAny]) 
def login_user(request):
    """
    Authenticate user using email & password and return JWT + User Profile data.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email & Password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(username=user_obj.username, password=password)

    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    try:
        profile = user.profile  # related_name=profile required in model
        login(request,user)
        response_data = {
            "access": str(access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "contact": profile.contact
            }
        }

        profile.access_token = access_token
        profile.refresh_token = str(refresh)
        profile.save()
        return Response(response_data, status=status.HTTP_200_OK)

    except Profile.DoesNotExist:
        return Response({'error': 'User profile missing'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_follow_counts(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    # Count followers and following
    followers_count = Follower.objects.filter(user=user).count()
    following_count = Follower.objects.filter(follow_by=user).count()

    data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'number_of_followers': followers_count,
        'number_of_following': following_count,
    }

    # If requesting own profile
    if request.user.id == user_id:
        pending_requests_count = FollowRequest.objects.filter(request_to=user, status='pending').count()

        notification_counts = (
            Notifications.objects
            .filter(user=request.user, is_read=False)
            .values('notification_type')  # GROUP BY notification_type
            .annotate(count=Count('id'))
        )
        final_notify = {i['notification_type']: i['count'] for i in notification_counts}

        data.update({
            'is_me': True,
            'notification': final_notify,
            'number_of_pending_requests': pending_requests_count,
            'total_notification': len(notification_counts),
        })
    else:
        data['is_me'] = False

        # Check if logged-in user has sent a follow request
        request_pending = FollowRequest.objects.filter(
            request_from=request.user, 
            request_to=user, 
            status='pending'
        ).exists()

        # Check if logged-in user is following the user
        following = Follower.objects.filter(
            user=user,
            follow_by=request.user
        ).exists()

        data['request_pending'] = request_pending
        data['following'] = following

    return Response(data)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_follow_request(request):
    user_to_id = request.data.get("user_to")

    if not user_to_id:
        return Response({"error": "User ID required"}, status=400)

    try:
        user_to = User.objects.get(id=user_to_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if request.user == user_to:
        return Response({"error": "You cannot follow yourself"}, status=400)

    # Create or update follow request
    follow, created = FollowRequest.objects.get_or_create(
        request_from=request.user,
        request_to=user_to
    )

    if not created:
        follow.status = "pending"
        follow.save()

    # 🔥 Create Notification for receiver (user_to)
    Notifications.objects.create(
        user=user_to,
        notification_type="follow_request",
        message=f"{request.user.first_name} {request.user.last_name} sent you a follow request."
    )

    return Response({"message": "Follow request sent successfully"}, status=201 if created else 200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def manage_follow_request(request):
    """
    Manage a follow request using request_from and request_to.
    Request body:
    {
        "request_from": <user_id>,
        "request_to": <user_id>,
        "status": "accepted" / "rejected" / "cancelled"
    }
    """
    request_from_id = request.data.get("request_from")
    request_to_id = request.user.id
    status = request.data.get("status")

    if status == "cancelled":
        request_from_id = request.user.id
        request_to_id = request.data.get("request_from")


    if not status:
        return Response({"error": "Status is required"}, status=400)

    status = status.lower()
    if status not in ["accepted", "rejected", "cancelled"]:
        return Response({"error": "Invalid status"}, status=400)

    try:
        follow_request = FollowRequest.objects.get(
            request_from_id=request_from_id,
            request_to_id=request_to_id
        )
    except FollowRequest.DoesNotExist:
        return Response({"error": "Follow request not found"}, status=404)

    # Permission checks
    if status in ["accepted", "rejected"] and follow_request.request_to != request.user:
        return Response({"error": "You are not allowed to manage this request"}, status=403)
    if status == "cancelled" and follow_request.request_from != request.user:
        return Response({"error": "You can only cancel your own requests"}, status=403)

    # Already handled
    if follow_request.status in ["accepted", "rejected"] and status in ["accepted", "rejected"]:
        return Response({"message": f"Follow request already {follow_request.status}"}, status=200)
    if follow_request.status == "cancelled" and status == "cancelled":
        return Response({"message": "Follow request already cancelled"}, status=200)

    # Update status
    follow_request.status = status
    follow_request.save()

    # Handle side effects
    if status == "accepted":
        Follower.objects.get_or_create(
            user=follow_request.request_to,
            follow_by=follow_request.request_from
        )
        Notifications.objects.create(
            user=follow_request.request_from,
            notification_type="follow_accepted",
            message=f"{request.user.first_name} {request.user.last_name} accepted your follow request."
        )

    elif status == "rejected":
        Notifications.objects.create(
            user=follow_request.request_from,
            notification_type="follow_rejected",
            message=f"{request.user.first_name} {request.user.last_name} rejected your follow request."
        )

    elif status == "cancelled":
        Notifications.objects.create(
            user=follow_request.request_to,
            notification_type="follow_cancelled",
            message=f"{request.user.first_name} {request.user.last_name} cancelled the follow request."
        )

    return Response({"message": f"Follow request has been {status}"}, status=200)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_all_follow_requests(request):
    """
    List all follow requests for the logged-in user (received).
    """

    follow_requests = FollowRequest.objects.filter(request_to=request.user,status="pending").order_by("-requested_at")

    data = []
    for fr in follow_requests:
        data.append({
            "id": fr.id,
            "request_from": fr.request_from.id,
            "request_from_name": f"{fr.request_from.first_name} {fr.request_from.last_name}".strip(),
            "status": fr.status,
            "requested_at": fr.requested_at
        })

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unfollow_user(request):
    """
    Unfollow a user.
    Request body: {"user_id": <id of the user to unfollow>}
    """
    user_id = request.data.get("user_id")
    if not user_id:
        return Response({"error": "user_id is required"}, status=400)

    try:
        user_to_unfollow = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    try:
        # Get the follower record
        follow = Follower.objects.get(user=user_to_unfollow, follow_by=request.user)
        follow.delete()
        return Response({"message": f"You have unfollowed {user_to_unfollow.username}"}, status=200)
    except Follower.DoesNotExist:
        return Response({"error": "You are not following this user"}, status=400)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """
    Search users by first_name, last_name, or username.
    Example: /api/users/search/?q=john
    """
    query = request.GET.get('q', '')

    if not query:
        return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)

    users = User.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(username__icontains=query)
    )

    serializer = UserSearchSerializer(users, many=True)
    return Response({"results": serializer.data}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_read(request):
    try:
        notification_obj = Notifications.objects.filter(user=request.user.id,is_read=False)
        frd_req = FollowRequest.objects.filter(request_to=request.user,status="pending").count()
        notification_obj.update(is_read=True)
        
        return Response({"frd_request":frd_req,"total_notification":notification_obj.count()}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": e.__str__()}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_notify(request):
    try:
        all_notify = Notifications.objects.filter(user=request.user,is_read=False).count()
        return Response({"total_notify":all_notify},status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error":e.__str__()},status=status.HTTP_400_BAD_REQUEST)
        

