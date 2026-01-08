import os
import requests
from dotenv import load_dotenv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from config import GOOGLE_API_KEY

@api_view(["GET"])
@permission_classes([AllowAny])   # change to IsAuthenticated later if needed
def google_place_search(request):
    cat = request.GET.get("cat", None)
    location = request.GET.get("location", None)

    if not cat and not location:
        return Response({"error": "Query parameter is required"}, status=400)

    

    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={cat}+in+{location}&key={GOOGLE_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        return Response({
            "status": data.get("status"),
            "results": data.get("results", [])
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
