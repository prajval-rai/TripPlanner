# notifications/views.py
import firebase_admin
from firebase_admin import credentials, messaging
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Initialize Firebase Admin
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

@api_view(['POST'])
def send_notification(request):
    data = request.data
    token = data.get('token')
    title = data.get('title', 'Notification')
    message = data.get('message', 'You have a new message')

    if not token:
        return Response({"error": "FCM token is required"}, status=400)

    # Create FCM message
    msg = messaging.Message(
        notification=messaging.Notification(title=title, body=message),
        token=token
    )

    # Send message
    response = messaging.send(msg)
    return Response({"result": response})
