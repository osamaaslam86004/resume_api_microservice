import jsonschema

# import logging
from rest_framework import serializers
from api_auth.serializers import UserSerializer


# logger = logging.getLogger(__name__)


class GenerateJsonSchema:
    def generate_json_schema(self):
        serializer = UserSerializer()
        schema = serializer.get_initial()
        schema["type"] = "object"  # Ensuring the top-level schema type is set
        print(f"schema in generate json schema: {schema}")
        return schema
        # return jsonschema.Draft4Validator.check_schema(schema)


class ValidateJson(GenerateJsonSchema):

    def validate_json(self, data):
        try:
            jsonschema.validate(data, self.generate_json_schema())
        except jsonschema.SchemaError as e:
            raise serializers.ValidationError(detail={"Schema Error": str(e)})
        except jsonschema.ValidationError as e:
            raise serializers.ValidationError(detail={"Validation Error": str(e)})


user_create_request_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "username": {"type": "string"},
        "password": {"type": "string"},
        "is_active": {"type": "boolean"},
        "is_staff": {"type": "boolean"},
        # "locality": {"type": ["string", "null"]},
        # "facebook": {"type": ["string", "null"], "format": "uri"},
        # "start_date": {"type": ["string", "null"], "format": "date"},
        # "end_date": {"type": ["string", "null"], "format": "date"}
    },
    # "required": ["email", "username", "password", "locality", "facebook", "is_active", "is_staff"]
    "required": ["email", "username", "password", "is_active", "is_staff"],
}

user_create_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "username": {"type": "string"},
        "is_active": {"type": "boolean"},
        "is_staff": {"type": "boolean"},
        # "locality": {"type": ["string", "null"]},
        # "facebook": {"type": ["string", "null"], "format": "uri"},
        # "start_date": {"type": ["string", "null"], "format": "date"},
        # "end_date": {"type": ["string", "null"], "format": "date"}
    },
    # "required": ["id", "email", "username", "is_active", "is_staff", "locality", "facebook"]
    "required": ["id", "email", "username", "is_active", "is_staff"],
}
