from django.urls import path
from .views import (
    trip_list_create,
    trip_detail,
    itinerary_list_create,
    itinerary_detail,
    trip_full_detail,
    invite_people_with_reminder,
    get_invited_people,
    invited_trip_list,
    accept_invite,
    reject_invite,
    user_trips_list
)

urlpatterns = [
    path("trips_list/", trip_list_create),
    path("user_trips_list/", user_trips_list),
    path("detail/<int:pk>/", trip_detail),

    path("itinerary/", itinerary_list_create),
    path("itinerary/<int:pk>/", itinerary_detail),

    # FINAL COMBINED TRIP DETAIL
    path("trip-detail/<int:trip_id>/", trip_full_detail),

    path("invite_people_with_reminder/",invite_people_with_reminder),
    path("<int:trip_id>/invited/",get_invited_people),
    path("invited_list/",invited_trip_list),

    #Accept Reject Invite
    path('accept/<int:invite_id>/',accept_invite, name='accept-invite'),
    path('reject/<int:invite_id>/',reject_invite, name='reject-invite'),
]
