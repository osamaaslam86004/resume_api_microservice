from rest_framework.metadata import SimpleMetadata


class CustomMetadata(SimpleMetadata):

    def determine_metadata(self, request, view):
        if request.method == "OPTIONS":
            metadata = {
                "name": view.get_view_name(),
                "description": view.get_view_description(),
                "renders": [renderer.media_type for renderer in view.renderer_classes],
                "parses": [parser.media_type for parser in view.parser_classes],
            }
            # if hasattr(view, "get_serializer"):
            #     actions = self.determine_actions(request, view)
            #     if actions:
            #         metadata["actions"] = actions
            return metadata
        else:
            return super().determine_metadata(request, view)
