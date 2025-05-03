# Let's move on to this point / section: Schema Validation Middleware:
# Implement middleware or decorators to automatically validate incoming requests 
# against defined schemas. You can use custom middleware or existing libraries like 
# django-json-schema-validator.

# middleware.py

import jsonschema
from django.http import JsonResponse

class SchemaValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define JSON schemas for each API endpoint
        schemas = {
            '/api/endpoint1/': {
                'type': 'object',
                'properties': {
                    'key1': {'type': 'string'},
                    'key2': {'type': 'number'}
                },
                'required': ['key1', 'key2']
            },
            '/api/endpoint2/': {
                'type': 'object',
                'properties': {
                    'key3': {'type': 'string'}
                },
                'required': ['key3']
            }
        }

        # Get the schema corresponding to the requested endpoint
        schema = schemas.get(request.path)

        # If a schema exists for the endpoint, validate the request payload
        if schema:
            try:
                jsonschema.validate(request.data, schema)
            except jsonschema.ValidationError as e:
                # Return a JSON response with validation error details
                return JsonResponse({'error': str(e)}, status=400)

        return self.get_response(request)


# Configure Middleware:
# In your Django settings, add the custom middleware to the MIDDLEWARE list to ensure that
# it's executed for incoming requests.
    

# settings.py

# MIDDLEWARE = [
#     # Other middleware classes...
#     'yourapp.middleware.SchemaValidationMiddleware',
# ]


# With this middleware in place, any incoming requests to your API endpoints will 
# be automatically validated against the defined JSON schemas. If a request payload fails
# validation, the middleware will return a JSON response with details of the validation error,
#  indicating what went wrong with the request. This helps ensure that only valid requests 
#  are processed by your API views, improving the reliability 
# and robustness of your API.