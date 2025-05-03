


from rest_framework.metadata import SimpleMetadata


class CustomMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)
        metadata['metadata'] = view.metadata  # Include custom metadata
        return metadata