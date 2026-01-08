from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count, Case, When, Value, CharField, Q
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny,IsAuthenticated

from .models import Trips, TripTags, InvitedPeople, ItineraryActivity
from .serializers import (
    TripSerializer,
    TripDetailSerializer,
    ItineraryActivitySerializer,
    InvitedPeopleSerializer,
    TripReminderSerializer,
    InvitedTripListSerializer
)


@api_view(["GET", "POST"])
def trip_list_create(request):
    if request.method == "GET":
        trips = (
            Trips.objects
            .filter(created_by=request.user)
            .annotate(invited_count=Count('invitedpeople'))
            .order_by("created_at")
        )

        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        data = request.data
        print("******************************************",data)
        data['created_by'] = request.user.id
        serializer = TripSerializer(data=data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)



@api_view(["GET", "PUT", "DELETE"])
def trip_detail(request, pk):
    trip = get_object_or_404(Trips, pk=pk)

    if request.method == "GET":
        return Response(TripSerializer(trip).data)

    if request.method == "PUT":
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^",request.data)
        serializer = TripSerializer(trip, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        trip.delete()
        return Response({"msg": "Deleted"}, status=204)


@api_view(["GET", "POST"])
def itinerary_list_create(request):
    if request.method == "GET":
        items = ItineraryActivity.objects.all().order_by("id")
        serializer = ItineraryActivitySerializer(items, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = ItineraryActivitySerializer(data=request.data)
        print("-----------------------",request.data)
        trip_id = request.data.get('trip')
        trip_obj = Trips.objects.get(id=trip_id)
        if not trip_obj.photo:
            trip_obj.photo = request.data['photo']
            trip_obj.save()
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        print("LLLLLLLLLLLLLLLL",serializer.errors)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "DELETE"])
def itinerary_detail(request, pk):
    item = get_object_or_404(ItineraryActivity, pk=pk)

    if request.method == "GET":
        return Response(ItineraryActivitySerializer(item).data)

    if request.method == "PUT":
        serializer = ItineraryActivitySerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        item.delete()
        return Response({"msg": "Deleted"}, status=204)


@api_view(["GET"])
def trip_full_detail(request, trip_id):
    trip = get_object_or_404(Trips, id=trip_id)
    serializer = TripDetailSerializer(trip)
    return Response(serializer.data)


@api_view(["POST"])
def invite_people_with_reminder(request):
    """
    API to invite people to a trip and set reminders.
    
    Expected payload:
    {
        "trip_id": 1,
        "invitees": [
            {
                "id": 5,                  # Optional, existing record ID
                "user_id": 2,
                "reminder_msg": "Don't forget!",
                "reminder_time": "2025-12-31T10:00:00Z"
            },
            {
                "id": None,               # New invite
                "user_id": 3
            }
        ],
        "default_reminder": {
            "message": "Trip is coming!",
            "dateTime": "2025-12-30T12:00:00Z"
        }
    }
    """
    data = request.data
    trip_id = data.get("trip_id")
    invitees = data.get("invitees", [])
    default_reminder = data.get("default_reminder", None)

    if not trip_id:
        return Response({"error": "trip_id is required"}, status=400)
    
    try:
        trip = Trips.objects.get(id=trip_id)
    except Trips.DoesNotExist:
        return Response({"error": "Trip not found"}, status=404)
    
    invited_list = []

    for person in invitees:
        record_id = person.get("id")  # existing record ID, can be None
        user_id = person.get("user_id")
        reminder_msg = person.get("reminder_msg", "")
        reminder_time = person.get("reminder_time", None)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            continue  # skip invalid users

        if record_id:  # update existing
            try:
                invited = InvitedPeople.objects.get(id=record_id, trip=trip)
                invited.reminder_msg = reminder_msg
                invited.reminder_time = reminder_time if reminder_time else timezone.now()
                invited.save()
            except InvitedPeople.DoesNotExist:
                # fallback: create new if record not found
                invited = InvitedPeople.objects.create(
                    trip=trip,
                    user=user,
                    reminder_msg=reminder_msg,
                    reminder_time=reminder_time if reminder_time else timezone.now()
                )
        else:  # create new
            invited = InvitedPeople.objects.create(
                trip=trip,
                user=user,
                reminder_msg=reminder_msg,
                reminder_time=reminder_time if reminder_time else timezone.now()
            )
        
        invited_list.append(invited)

    return Response({
        "invited": InvitedPeopleSerializer(invited_list, many=True).data,
    }, status=status.HTTP_201_CREATED)



@api_view(["GET"])
def get_invited_people(request, trip_id):
    """
    Get all invited people with reminder info for a trip
    """

    try:
        trip = Trips.objects.get(id=trip_id)
    except Trips.DoesNotExist:
        return Response(
            {"error": "Trip not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    invited_people = (
        InvitedPeople.objects
        .filter(trip=trip)
        .select_related("user")
    )

    invitees = []
    for invite in invited_people:
        invitees.append({
            "id":invite.id,
            "user_id": invite.user.id,
            "name": f"{invite.user.first_name} {invite.user.last_name}".strip(),
            "reminder_msg": invite.reminder_msg,
            "reminder_time": invite.reminder_time,
            "status": invite.status
        })

    return Response({
        "trip_id": trip.id,
        "invitees": invitees
    }, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invited_trip_list(request):
    """
    Get all trips where logged-in user is invited
    """
    invited_qs = (
        InvitedPeople.objects
        .select_related("trip", "trip__created_by")
        .filter(user=request.user,status="invited")
        .order_by("-id")
    )

    serializer = InvitedTripListSerializer(invited_qs, many=True)

    return Response({
        "count": invited_qs.count(),
        "results": serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_invite(request, invite_id):
    try:
        print("222222222222222222222222",invite_id)
        invite = InvitedPeople.objects.get(id=invite_id)
        invite.status = 'accepted'
        invite.save()
        return Response({"message": "Trip invitation accepted."}, status=status.HTTP_200_OK)
    except InvitedPeople.DoesNotExist:
        return Response({"error": "Invite not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_invite(request, invite_id):
    try:
        print("======================",invite_id)
        invite = InvitedPeople.objects.get(id=invite_id, user=request.user)
        invite.status = 'declined'
        invite.save()
        return Response({"message": "Trip invitation rejected."}, status=status.HTTP_200_OK)
    except InvitedPeople.DoesNotExist:
        return Response({"error": "Invite not founddddddddddd."}, status=status.HTTP_404_NOT_FOUND)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_trips_list(request):
    user = request.user

    # Get trips where user is invited and accepted
    accepted_trip_ids = InvitedPeople.objects.filter(
        user=user,
        status='accepted'
    ).values_list('trip_id', flat=True)

    # Get all trips either created by user or accepted
    trips = Trips.objects.filter(
        Q(created_by=user) | Q(id__in=accepted_trip_ids)
    ).annotate(
        invited_count=Count('invitedpeople'),
        status=Case(
            When(created_by=user, then=Value('created')),
            When(id__in=accepted_trip_ids, then=Value('accepted')),
            default=Value('unknown'),
            output_field=CharField()
        )
    ).order_by('-created_at')

    serializer = TripSerializer(trips, many=True)
    return Response(serializer.data)