import json
import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    JsonResponse,
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.vary import vary_on_headers
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from formtools.wizard.views import SessionWizardView
from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from custom_restframework_simplejwt.authentication import JWTStatelessUserAuthentication
from resume.forms import (
    EducationfoForm,
    JobAccomplishmentfoForm,
    JobfoForm,
    OverviewForm,
    PersonalInfoForm,
    ProgrammingAreaForm,
    ProjectsForm,
    PublicationForm,
    SkillAndSkillLevelForm,
)
from resume.models import PersonalInfo
from resume.resume_pagination import LargeResultsSetPagination
from resume.serializers import (
    PersonalInfo_Serializer,
    PersonalInfo_Serializer_Get_Request,
)
from resume.validate_schema import ValidateJson
from resume_service.custom_user_rated_throtle_class import CustomUserRateThrottle

logger = logging.getLogger(__name__)


def condition_callable(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("0") or {}
    condition_value = cleaned_data.get("condition")
    return condition_value == "True"


class PersonalInfoWizard(SessionWizardView):
    form_list = [
        PersonalInfoForm,
        PublicationForm,
        OverviewForm,
        EducationfoForm,
        JobfoForm,
        JobAccomplishmentfoForm,
        SkillAndSkillLevelForm,
        ProgrammingAreaForm,
        ProjectsForm,
    ]
    template_name = "wizard_view.html"
    condition_dict = {"1": condition_callable}

    def done(self, form_list, **kwargs):
        condition = form_list[0].cleaned_data["condition"]
        personal_info_form = form_list[0]
        PersonalInfo = personal_info_form.save(commit=False)

        user_id = self.request.GET.get("user_id")
        if not user_id:
            return JsonResponse({"error": "User ID is missing"}, status=400)

        from resume.check_user_exists import user_exists

        user_exists_response = user_exists(user_id)
        if user_exists_response["exists"]:
            pass

        elif user_exists_response["status_code"] == 404:
            return JsonResponse({"error": "User Not Found"}, status=404)

        elif user_exists_response["status_code"] == 503:
            return JsonResponse({"error": "Service Unavailable"}, status=503)

        else:
            return JsonResponse({"error": "Unknown Error"}, status=500)

        if condition == "False":
            over_view = form_list[1]
            education_data = form_list[2]
            job_data = form_list[3]
            job_accomplishment_data = form_list[4]
            skill_and_skill_level_data = form_list[5]
            programming_area_data = form_list[6]
            projects_data = form_list[7]

            overview = over_view.save(commit=False)
            education = education_data.save(commit=False)
            job = job_data.save(commit=False)
            accomplishment = job_accomplishment_data.save(commit=False)
            skill = skill_and_skill_level_data.save(commit=False)
            programming_area = programming_area_data.save(commit=False)
            projects = projects_data.save(commit=False)

            PersonalInfo.user_id = user_id
            PersonalInfo.save()

            overview.personal_info = PersonalInfo
            overview.save()
            education.personal_info = PersonalInfo
            education.save()
            job.personal_info_job = PersonalInfo
            job.save()
            accomplishment.job = job
            accomplishment.save()
            skill.personal_info = PersonalInfo
            skill.save()
            programming_area.personal_info = PersonalInfo
            programming_area.save()
            projects.personal_info = PersonalInfo
            projects.save()

            messages.success(self.request, "CV created successfully!")
            if settings.DEBUG:
                return HttpResponsePermanentRedirect("http://localhost:8000/")
            else:
                return HttpResponsePermanentRedirect(
                    "https://osama11111.pythonanywhere.com/"
                )

        else:
            del personal_info_form.cleaned_data["condition"]
            PersonalInfo = personal_info_form.save(commit=False)

            publication_data = form_list[1]
            over_view = form_list[2]
            education_data = form_list[3]
            job_data = form_list[4]
            job_accomplishment_data = form_list[5]
            skill_and_skill_level_data = form_list[6]
            programming_area_data = form_list[7]
            projects_data = form_list[8]

            publication = publication_data.save(commit=False)
            overview = over_view.save(commit=False)
            education = education_data.save(commit=False)
            job = job_data.save(commit=False)
            accomplishment = job_accomplishment_data.save(commit=False)
            skill = skill_and_skill_level_data.save(commit=False)
            programming_area = programming_area_data.save(commit=False)
            projects = projects_data.save(commit=False)

            PersonalInfo.user_id = user_id
            PersonalInfo.save()

            publication.personal_info = PersonalInfo
            publication.save()
            overview.personal_info = PersonalInfo
            overview.save()
            education.personal_info = PersonalInfo
            education.save()
            job.personal_info_job = PersonalInfo
            job.save()
            accomplishment.job = job
            accomplishment.save()
            skill.personal_info = PersonalInfo
            skill.save()
            programming_area.personal_info = PersonalInfo
            programming_area.save()
            projects.personal_info = PersonalInfo
            projects.save()

            messages.success(self.request, "CV created successfully!")
            if settings.DEBUG:
                return HttpResponsePermanentRedirect("http://localhost:8000/")
            else:
                return HttpResponsePermanentRedirect(
                    "https://osama11111.pythonanywhere.com/"
                )


@method_decorator(cache_control(private=True), name="dispatch")
@method_decorator(cache_page(60 * 60 * 2), name="dispatch")
@method_decorator(vary_on_headers("User-Agent"), name="dispatch")
class PersonalInfo_List_CreateView(viewsets.ModelViewSet, ValidateJson):
    queryset = PersonalInfo.objects.order_by("-id")
    lookup_field = "id"
    serializer_class = PersonalInfo_Serializer
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    authentication_classes = [JWTStatelessUserAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomUserRateThrottle]
    pagination_classes = LargeResultsSetPagination
    http_method_names = ["post", "delete", "get", "put", "patch", "options"]
    allowed_methods = ["POST", "GET", "OPTIONS", "PUT", "PATCH", "DELETE"]

    def add_throttle_headers(self, request, response):
        response["X-RateLimit-Limit"] = request.rate_limit["X-RateLimit-Limit"]
        response["X-RateLimit-Remaining"] = request.rate_limit["X-RateLimit-Remaining"]

    # @extend_schema(
    #     description="End-Point For Creating Resume",
    #     request=PersonalInfo_Serializer,
    #     responses={"201": PersonalInfo_Serializer_Get_Request},
    #     methods=["POST"],
    # )
    def create(self, request, *args, **kwargs):

        # Validate request data
        try:
            self.validate_json(request.data)
        except Exception as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        response = super().create(request, *args, **kwargs)
        self.add_throttle_headers(request, response)
        return response

    def perform_update(self, serializer):
        # this is not django request, instead a django rest framework request: both are different
        # print(f"self.request : {self.request}")

        # Doing commit = False for serializer to get model instance
        # ==> model_instance = form.save(commit=False)
        instance = serializer.instance
        user_id = None
        id = None

        if instance.user_id:
            user_id = instance.user_id.id
        else:
            personal_info_instance = PersonalInfo.objects.filter(id=instance.id).first()
            if personal_info_instance:
                user_id = personal_info_instance.user_id.id

        if instance:
            id = instance.id

        # print(f"user_id : {user_id} and id in self.perfom update------------: {id}")

        try:
            with transaction.atomic():
                try:
                    response = super().perform_update(serializer)
                except Exception as e:
                    raise Exception({"detail super()": str(e)})

                if user_id:
                    transaction.on_commit(
                        lambda: self.send_notification(
                            event="cv_updated",
                            status_="UPDATED",
                            exception=None,
                            user_id=user_id,
                            id=id,
                            request=self.request,
                        )
                    )
                else:
                    transaction.on_commit(
                        lambda: self.send_notification(
                            event="cv_updated",
                            status_="UPDATED",
                            id=id,
                            exception=None,
                            user_id=None,
                            request=self.request,
                        )
                    )
        except Exception as e:
            self.send_notification(
                event="cv_update_fail",
                exception=str(e),
                status_="FAILED",
                user_id=user_id if user_id else None,
                id=id,
                request=self.request,
            )
            raise Exception(e)

    def destroy(self, request, *args, **kwargs):
        personal_info_id = kwargs["id"]
        personal_info = PersonalInfo.objects.filter(id=personal_info_id)

        print(
            f"personal_info_id_delete---- : {personal_info}: request.user.id--- : {request.user.id}"
        )

        data = {
            "id": personal_info_id,
            "user_id": request.user.id,
            "event": "cv_deleted",
            "status": "DELETED",
            "exception": "None",
        }

        if personal_info:

            try:
                with transaction.atomic():
                    self.perform_destroy(personal_info[0])
                    print("perform deleted is perfomed")

                    response = Response({"data": data}, status=status.HTTP_200_OK)

            except Exception as e:
                data["status"] = "FAILED"
                data["exception"] = str(e)
                response = Response(
                    {"data": data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            response = Response(
                {"detail": "Personal Info does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.add_throttle_headers(request, response)
        return response

    @extend_schema(
        responses={"200": PersonalInfo_Serializer_Get_Request},
        methods=["GET"],
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID of the user to whom the Resume belongs.",
            ),
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID of the Resume record.",
            ),
        ],
        description="Return a single Resume if both 'user_id' and 'id' are provided, and if only 'id' is provided. Return a list of all Resumes for user if only 'user_id' is provided",
    )
    def get_personal_info_for_user(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        personal_info_id = request.query_params.get("personal_info_id")

        logger.debug(
            f"Received user_id: {user_id}, personal_info_id: {personal_info_id}"
        )

        # check if "user_id" and "personal_info_id" are not none
        if (
            "user_id" not in request.query_params
            and user_id is not None
            and "personal_info_id" not in request.query_params
            and personal_info_id is not None
        ):
            response = Response(
                {
                    "detail": "query parameters : 'user_id' or 'personal_info_id' is required"
                }
            )
            self.add_throttle_headers(request, response)
            return response

        filter_kwargs = {}
        try:
            # Retrieve a particular instance only
            if personal_info_id and user_id:
                queryset = self.get_queryset().filter(
                    id=personal_info_id, user_id=user_id
                )
                filter_kwargs = {"user_id": user_id, "id": personal_info_id}
            else:
                # return list of personalinfo instances for user
                queryset = self.get_queryset().filter(user_id=user_id)
                filter_kwargs = {
                    "user_id": user_id,
                }
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)

        except Exception as e:
            response = JsonResponse({"detail": str(e)})

        self.add_throttle_headers(request, response)
        return response

    @extend_schema(
        request=PersonalInfo_Serializer,
        responses={"200": PersonalInfo_Serializer_Get_Request},
        methods=["PATCH", "PUT"],
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID of the user to whom the Resume belongs.",
                required=True,
            ),
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID of the Resume record.",
                required=True,
            ),
            OpenApiParameter(
                name="partial",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Update the Resume if 'partial' is not provided otherwise perfom 'Partial Update'. 'partial' is case in-sensitive",
                required=False,
            ),
        ],
        description="Update or partially update a Resume.",
    )
    def patch_personal_info_for_user(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        id = request.query_params.get("id")

        # print(f"user id------ : {user_id} : id-----: {id}")

        # check for user id is not none and id is not empty
        if user_id is not None and id is not None:
            # Check if partial is available as **kwargs
            if "partial" in kwargs:
                partial = True if kwargs.pop("partial").lower() == "true" else False

            elif "partial" in request.query_params:
                # Check if partial is available as query parameter
                partial = (
                    True
                    if request.query_params.get("partial").lower() == "true"
                    else False
                )
            else:
                response = Response(
                    {"error": " 'partial' is not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                self.add_throttle_headers(request, response)
                return response
        else:
            response = Response(
                {"error": "'user_id' and 'id' is not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            self.add_throttle_headers(request, response)
            return response

        # print(f"partial-------------- : {partial}")
        instance = PersonalInfo.objects.filter(user_id__id=user_id, id=id).first()
        # print(f"instance-------: {instance}")

        if not instance:
            response = Response(
                {"error": "Personal Info does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            self.add_throttle_headers(request, response)
            return response

        if user_id not in request.data:
            request.data["user_id"] = user_id
        # want to pass/access variables / keys / query parameters from ModelSets method to/within
        # crete(), update() method of Serializer class, then pass these in context dictionary

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={"user_id": user_id, "id": id},
        )

        serializer.is_valid(raise_exception=True)
        # print(f"serializer_data.validated_data : {serializer.validated_data}")

        try:
            self.perform_update(serializer)
            response = Response(
                data={
                    "id": int(id),
                    "user_id": int(user_id),
                    "event": "cv_updated",
                    "status": "UPDATED",
                    "exception": "None",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            response = Response(
                {"exception in self.perfom_update()----------------": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        self.add_throttle_headers(request, response)
        return response

    def send_notification(self, event, **kwargs):
        request = kwargs.get("request", None)

        if settings.DEBUG:
            WEBHOOK_URL = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"
        else:
            WEBHOOK_URL = "https://osama11111.pythonanywhere.com/cv-webhook/"

        # Convert header values to strings
        headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(request.rate_limit["X-RateLimit-Limit"]),
            "X-RateLimit-Remaining": str(request.rate_limit["X-RateLimit-Remaining"]),
        }

        if event in ["cv_updated", "cv_update_fail"]:
            user_id = kwargs.get("user_id", None)
            id = kwargs.get("id")

            data = {
                "id": id,
                "user_id": user_id,
                "event": event,
                "status": kwargs.get("status_", "UNKNOWN"),
                "exception": kwargs.get("exception", "None"),
            }

            data = json.dumps(data)

        try:
            response = requests.post(WEBHOOK_URL, headers=headers, data=data)
            response.raise_for_status()

        except requests.RequestException as e:
            print(f"Failed to send webhook: {str(e)}")
            pass

    def list(self, request, *args, **kwargs):
        response = Response(
            {"detail": 'Method "GET" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        response["Content-Type"] = "application/json"
        return response

    def update(self, request, *args, **kwargs):
        response = Response(
            {"detail": 'Method "PUT" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        response["Content-Type"] = "application/json"
        return response

    def partial_update(self, request, *args, **kwargs):
        response = Response(
            {"detail": 'Method "PATCH" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        response["Content-Type"] = "application/json"
        return response

    def get_object(self):
        request = self.request

        if request.method == "OPTIONS":
            return
        else:
            return super().get_object()

    def options(self, request, *args, **kwargs):

        if self.metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = self.metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK)
