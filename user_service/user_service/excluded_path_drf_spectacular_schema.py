# View To Exclude Certain Paths from Documentation of API
def custom_preprocessing_hook(endpoints, **kwargs):
    # Define the paths and methods you want to exclude
    exclude_paths = [
        "/resume/api/get-personal-info-data/",  # For GET
        "/resume/api/get-personal-info-data/{id}/",  # For GET, PUT, PATCH
    ]
    exclude_methods = ["GET", "PUT", "PATCH"]

    # Filter out the endpoints matching the paths and methods
    filtered_endpoints = []
    for path, path_regex, method, callback in endpoints:
        if path in exclude_paths and method in exclude_methods:
            continue
        filtered_endpoints.append((path, path_regex, method, callback))

    return filtered_endpoints
