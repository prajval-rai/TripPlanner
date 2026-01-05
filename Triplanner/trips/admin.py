from django.contrib import admin
from .models import Trips,ItineraryActivity,InvitedPeople

# Register your models here.
admin.site.register(Trips)
admin.site.register(ItineraryActivity)
admin.site.register(InvitedPeople)