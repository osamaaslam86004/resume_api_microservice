from rest_framework.pagination import PageNumberPagination




class LargeResultsSetPagination(PageNumberPagination):
    page_size = 3  # the number of items you want to show on each page
    page_size_query_param = (
        "page_size"  # let the user decide how many items they want to see on a page
    )
    max_page_size = (
        10000  # maximum limit on how many items a user can request on a single page.
    )
