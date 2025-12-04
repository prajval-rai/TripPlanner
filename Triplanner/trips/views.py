from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Trips, TripTags, InvitedPeople, ItineraryActivity
from .serializers import (
    TripSerializer,
    TripDetailSerializer,
    ItineraryActivitySerializer,
)


@api_view(["GET", "POST"])
def trip_list_create(request):
    if request.method == "GET":
        print("--------------------------",request.user.id)
        trips = Trips.objects.filter(created_by=request.user.id).order_by("created_at")
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        data = request.data
        print(request.user.id)
        data['created_by'] = request.user.id
        serializer = TripSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("8888888888888888888888888888888",serializer.errors)
        return Response(serializer.errors, status=400)



@api_view(["GET", "PUT", "DELETE"])
def trip_detail(request, pk):
    trip = get_object_or_404(Trips, pk=pk)

    if request.method == "GET":
        return Response(TripSerializer(trip).data)

    if request.method == "PUT":
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
