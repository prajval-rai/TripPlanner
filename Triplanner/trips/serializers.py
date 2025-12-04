from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Trips, TripTags, TripTagMapping, InvitedPeople, ItineraryActivity


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
        ]


# ===========================
# SIMPLE TRIP SERIALIZER
# ===========================
class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trips
        fields = "__all__"
