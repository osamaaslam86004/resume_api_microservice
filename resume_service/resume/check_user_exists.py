import requests
from django.http import JsonResponse
from requests.exceptions import RequestException


def user_exists(user_id):

    try:
        # Define the URL of the user_service endpoint
        user_service_url = (
            "https://your-user-service-domain.com/api/check-user/"  # Update this!
        )

        # Send a POST request with JSON payload
        response = requests.post(user_service_url, json={"user_id": user_id}, timeout=5)

        # Check if the user exists based on user_service response
        if response.status_code == 200:
            return {
                "exists": True,
                "error_message": {},
                "status_code": 200,
            }
        else:
            return {
                "exists": False,
                "error_message": {},
                "status_code": {response.status_code},
            }

    except RequestException as e:
        # Catch network issues like timeout, connection error, etc.
        return {
            "exists": False,
            "error_message": {"error": str(e)},
            "status_code": 503,  # Service unavailable
        }
