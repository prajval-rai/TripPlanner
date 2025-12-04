from django.urls import path
from .views import (
    trip_list_create,
    trip_detail,
    itinerary_list_create,
    itinerary_detail,
    trip_full_detail,
)

urlpatterns = [
    path("trips_list/", trip_list_create),
    path("detail/<int:pk>/", trip_detail),

    path("itinerary/", itinerary_list_create),
    path("itinerary/<int:pk>/", itinerary_detail),

    # FINAL COMBINED TRIP DETAIL
    path("trip-detail/<int:trip_id>/", trip_full_detail),
]
