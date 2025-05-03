from django.urls import include, path
from rest_framework.routers import DefaultRouter
from resume import views
from resume.views import PersonalInfo_List_CreateView, PersonalInfoWizard

router = DefaultRouter()
router.register(
    r"get-personal-info-data",
    PersonalInfo_List_CreateView,
    basename="get-personal-info-data",
)
urlpatterns = [
    path(
        "get-personal-info-data-for-user/",
        PersonalInfo_List_CreateView.as_view({"get": "get_personal_info_for_user"}),
        name="get_personal_info_for_user",
    ),
    path(
        "patch-put-personal-info-data-for-user/",
        PersonalInfo_List_CreateView.as_view(
            {
                "put": "patch_personal_info_for_user",
                "patch": "patch_personal_info_for_user",
            }
        ),
        name="patch_put_personal_info_for_user",
    ),
    path(
        "",
        PersonalInfoWizard.as_view(),
        name="personal-info-wizard",
    ),
] + [path("api/", include(router.urls))]
