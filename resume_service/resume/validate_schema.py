import jsonschema

# import logging
from rest_framework import serializers
from resume.serializers import PersonalInfo_Serializer


# logger = logging.getLogger(__name__)


class GenerateJsonSchema:
    def generate_json_schema(self):
        serializer = PersonalInfo_Serializer()
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
