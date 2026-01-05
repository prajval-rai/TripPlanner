from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Trips, TripTags, TripTagMapping, InvitedPeople, ItineraryActivity,TripReminder


# ===========================
# USER SERIALIZER
# ===========================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username"]


# ===========================
# TAG SERIALIZERS
# ===========================
class TripTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripTags
        fields = ["id", "name"]


class TripTagMappingSerializer(serializers.ModelSerializer):
    tag = TripTagSerializer()

    class Meta:
        model = TripTagMapping
        fields = ["tag"]


# ===========================
# INVITED PEOPLE
# ===========================
class InvitedPeopleSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = InvitedPeople
        fields = [
            "id",
            "user",
            "reminder_msg",
            "reminder_time",
            "status",
        ]


# ===========================
# ITINERARY
# ===========================
class ItineraryActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryActivity
        fields = [
            "trip",
            "id",
            "date",
            "title",
            "desc",
            "location",
            "lon",
            "lat",
            "start_time",
            "end_time",
            "reminder",
            "reminder_time",
            "photo"
        ]


# ===========================
# TRIP DETAIL (FULL JOINED DATA)
# ===========================
class TripDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()

    # 🌟 Important: use source to access reverse relations
    tags = TripTagSerializer(many=True)
    invited_people = InvitedPeopleSerializer(
        many=True,
        source="invitedpeople_set"
    )
    itinerary = ItineraryActivitySerializer(
        many=True,
        source="itineraryactivity_set"
    )

    class Meta:
        model = Trips
        fields = [
            "id",
            "created_by",
            "title",
            "description",
            "start_date",
            "end_date",
            "location",
            "created_at",
            "tags",
            "invited_people",
            "itinerary",
            "photo"
        ]


# ===========================
# SIMPLE TRIP SERIALIZER
# ===========================
class TripSerializer(serializers.ModelSerializer):
    invited_count = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    class Meta:
        model = Trips
        fields = "__all__"

class TripReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripReminder
        fields = "__all__"

class InvitedPeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitedPeople
        fields = "__all__"

class InvitedTripListSerializer(serializers.ModelSerializer):
    trip_id = serializers.IntegerField(source="trip.id")
    title = serializers.CharField(source="trip.title")
    location = serializers.CharField(source="trip.location")
    start_date = serializers.DateField(source="trip.start_date")
    end_date = serializers.DateField(source="trip.end_date")
    photo = serializers.CharField(source="trip.photo")

    created_by = serializers.SerializerMethodField()

    class Meta:
        model = InvitedPeople
        fields = [
            "id",            # invited record id
            "trip_id",
            "title",
            "location",
            "start_date",
            "end_date",
            "photo",
            "created_by",
            "status",
        ]

    def get_created_by(self, obj):
        user = obj.trip.created_by
        return {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}".strip()
                    or user.username
        }



class InvitedPeopleDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = InvitedPeople
        fields = ["id", "user", "user_name", "user_email", "reminder_msg", "reminder_time", "status"]

class TripReminderDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    class Meta:
        model = TripReminder
        fields = ["id", "user", "user_name", "dateTime", "message", "status"]