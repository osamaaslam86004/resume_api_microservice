from django.core.exceptions import ValidationError
from django.db import transaction
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from resume.models import (
    Education,
    Job,
    JobAccomplishment,
    Overview,
    PersonalInfo,
    ProgrammingArea,
    Projects,
    Publication,
    SkillAndSkillLevel,
)
from resume.schema_classes_for_documentation import schema_personalinfo_serializer


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = ["title", "authors", "journal", "year", "link"]
        read_only = ["id"]


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = "__all__"
        read_only_fields = ["id"]


class ProgrammingAreaSerializer(serializers.ModelSerializer):

    PROGRAMMING_AREA_CHOICES = (
        ("FRONTEND", "Frontend"),
        ("BACKEND", "Backend"),
    )

    FRONTEND_PROGRAMMING_LANGUAGE_CHOICES = [
        ("HTML", "HTML"),
        ("CSS", "CSS"),
        ("JavaScript", "JavaScript"),
        ("TypeScript", "TypeScript"),
        ("React", "React"),
        ("Angular", "Angular"),
        ("Vue.js", "Vue.js"),
    ]

    BACKEND_PROGRAMMING_LANGUAGE_CHOICES = [
        ("JavaScript (Node.js)", "JavaScript (Node.js)"),
        ("Python (Django)", "Python (Django)"),
        ("Python (Flask)", "Python (Flask)"),
        ("Ruby (Ruby on Rails)", "Ruby (Ruby on Rails)"),
        ("Java (Spring)", "Java (Spring)"),
        ("PHP (Laravel)", "PHP (Laravel)"),
        ("C# (ASP.NET)", "C# (ASP.NET)"),
        ("Go (GoLang)", "Go (GoLang)"),
        ("Scala (Play Framework)", "Scala (Play Framework)"),
        ("Elixir (Phoenix)", "Elixir (Phoenix)"),
    ]

    class Meta:
        model = ProgrammingArea
        fields = ["programming_area_name", "programming_language_name"]

    def get_programming_language_area_value(self, area, name):
        if area == "FRONTEND":
            self.frontend_programming_language_name(name)
        else:
            self.backend_programming_language_name(name)

    def backend_programming_language_name(self, name):
        count = 0
        for items in ProgrammingAreaSerializer.BACKEND_PROGRAMMING_LANGUAGE_CHOICES:
            if name == items[0]:
                if (
                    count
                    != len(
                        ProgrammingAreaSerializer.BACKEND_PROGRAMMING_LANGUAGE_CHOICES
                    )
                    + 1
                ):
                    break
                else:
                    raise serializers.ValidationError(
                        "Invalid programming language for BACKEND area"
                    )
            else:
                count = count + 1
                if count == 7:
                    raise serializers.ValidationError(
                        "Invalid programming language for Backend area"
                    )

    def frontend_programming_language_name(self, name):
        count = 0
        for items in ProgrammingAreaSerializer.FRONTEND_PROGRAMMING_LANGUAGE_CHOICES:
            if name == items[0]:
                if (
                    count
                    != len(
                        ProgrammingAreaSerializer.FRONTEND_PROGRAMMING_LANGUAGE_CHOICES
                    )
                    + 1
                ):
                    break
                else:
                    raise serializers.ValidationError(
                        "Invalid programming language for frontend area"
                    )
            else:
                count = count + 1
                if count == 7:
                    raise serializers.ValidationError(
                        "Invalid programming language for frontend area"
                    )


class SkillAndSkillLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillAndSkillLevel
        fields = ["text", "skill_level"]
        read_only_fields = ["id"]


class JobAccomplishmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAccomplishment
        fields = ["job_accomplishment"]


class JobSerializer(serializers.ModelSerializer):
    accomplishment = JobAccomplishmentSerializer()
    job_start_date = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])
    job_end_date = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])

    class Meta:
        model = Job
        fields = [
            "company",
            "companyurl",
            "location",
            "title",
            "description",
            "job_start_date",
            "job_end_date",
            "is_current",
            "is_public",
            "image",
            "accomplishment",
        ]


class EducationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ["name", "location", "degree"]


class EducationListCreateSerializer(serializers.ModelSerializer):

    education_start_date = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])
    education_end_date = serializers.DateField(input_formats=["%d-%m-%Y", "%Y-%m-%d"])

    class Meta:
        model = Education
        fields = [
            "name",
            "location",
            "schoolurl",
            "education_start_date",
            "education_end_date",
            "degree",
            "description",
        ]

    def update(self, instance, validated_data):
        fields_to_update = [
            "name",
            "location",
            "schoolurl",
            "education_start_date",
            "education_end_date",
            "degree",
            "description",
        ]

        for field in fields_to_update:
            setattr(
                instance, field, validated_data.get(field, getattr(instance, field))
            )
            instance.save()

        return instance


class OverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Overview
        fields = ["text"]

    def update(self, instance, validated_data):
        instance.text = validated_data.get("text", instance.text)
        instance.save()
        return instance


@extend_schema_serializer(
    exclude_fields=("id"),
    examples=[
        OpenApiExample(
            name="Example 1",
            summary="short summary",
            description="longer description",
            value=schema_personalinfo_serializer,
            request_only=True,
            response_only=False,
        ),
    ],
)
class PersonalInfo_Serializer(serializers.ModelSerializer):
    overview = OverviewSerializer()
    education = EducationListCreateSerializer(many=True)
    job = JobSerializer()
    skill = SkillAndSkillLevelSerializer(many=True)
    programming_area = ProgrammingAreaSerializer(many=True)
    projects = ProjectsSerializer(many=True)
    publications = PublicationSerializer(many=True)

    class Meta:
        model = PersonalInfo
        fields = [
            "id",
            "user_id",
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "locality",
            "region",
            "title",
            "email",
            "linkedin",
            "facebook",
            "github",
            "site",
            "twittername",
            "overview",
            "education",
            "skill",
            "job",
            "programming_area",
            "projects",
            "publications",
        ]

    def __init__(self, *args, **kwargs):

        # **kwarg contain the json data send by client. No change in the structure/data-type
        # self = {context={request, format, view}, data = **kwargs }
        super(PersonalInfo_Serializer, self).__init__(*args, **kwargs)
        self.instance_of_Programming_area = ProgrammingAreaSerializer()
        # Trigger signal for create method but not for update method of serializer
        self.is_create = False

    def validate_programming_area_model_fields(self, programming_area_data):
        for item in programming_area_data:
            area = item.get("programming_area_name")
            name = item.get("programming_language_name")
            self.instance_of_Programming_area.get_programming_language_area_value(
                area, name
            )

    def create(self, validated_data):
        self.is_create = True

        overview_data = validated_data.pop("overview")
        education_data = validated_data.pop("education")
        job_data = validated_data.pop("job")
        skill_data = validated_data.pop("skill")
        programming_area_data = validated_data.pop("programming_area")
        projects_data = validated_data.pop("projects")
        publication_data = validated_data.pop("publications")

        self.validate_programming_area_model_fields(programming_area_data)
        try:
            with transaction.atomic():
                user_id = self.context.get("user_id")
                if user_id:
                    personal_info = PersonalInfo.objects.create(
                        user_id, **validated_data
                    )
                else:
                    personal_info = PersonalInfo.objects.create(**validated_data)

                Overview.objects.create(personal_info=personal_info, **overview_data)

                for item in education_data:
                    Education.objects.create(personal_info=personal_info, **item)

                job_accomplishment_data = job_data.pop("accomplishment")
                job_created = Job.objects.create(
                    personal_info_job=personal_info, **job_data
                )
                JobAccomplishment.objects.create(
                    job=job_created, **job_accomplishment_data
                )

                for item in skill_data:
                    SkillAndSkillLevel.objects.create(
                        personal_info=personal_info, **item
                    )
                for item in programming_area_data:
                    ProgrammingArea.objects.create(personal_info=personal_info, **item)
                for item in projects_data:
                    Projects.objects.create(personal_info=personal_info, **item)
                for item in publication_data:
                    Publication.objects.create(personal_info=personal_info, **item)
        except Exception as e:
            raise ValidationError(str(e))
        return personal_info

    def update(self, instance, validated_data):
        self.is_create = False

        try:
            # # instance here is the instance of PersonalInfo model
            with transaction.atomic():
                self.update_personal_info(instance, validated_data)
                self.update_overview(instance, validated_data)
                self.update_education(instance, validated_data)
                self.update_job(instance, validated_data)
                self.update_skill_and_skill_level(instance, validated_data)
                self.update_programming_area(instance, validated_data)
                self.update_projects(instance, validated_data)
                self.update_publications(instance, validated_data)
        except Exception as e:
            raise ValidationError({"detail": str(e)})

        return instance

    def update_personal_info(self, instance, validated_data):

        fields_to_update = [
            "user_id",
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "locality",
            "region",
            "title",
            "email",
            "linkedin",
            "facebook",
            "github",
            "site",
            "twittername",
        ]

        try:
            id_user = self.context.get("user_id")

            for field in fields_to_update:
                if "user_id" in validated_data:
                    setattr(
                        instance,
                        field,
                        validated_data.get(field, getattr(instance, field)),
                    )
                else:
                    instance.user_id = id_user
            instance.save()
        except Exception as e:
            raise ValidationError({"detail": str(e)})

    def update_overview(self, instance, validated_data):

        overview_data = validated_data.pop("overview")
        overview_instance = instance.overview
        overview_instance.text = overview_data.get("text", overview_instance.text)
        overview_instance.save()

    def update_education(self, instance, validated_data):
        education_data = validated_data.pop("education")
        education_fields_to_update = [
            "name",
            "location",
            "schoolurl",
            "education_start_date",
            "education_end_date",
            "degree",
            "description",
        ]

        education_instance_list = Education.objects.filter(
            personal_info__id=instance.id
        )
        if not education_instance_list:
            raise serializers.ValidationError(
                f"Education instance with Personal ID {instance.id} does not exist."
            )
        else:
            count = 0
            for item in education_data:
                try:
                    for field, value in item.items():
                        if field not in education_fields_to_update:
                            raise serializers.FieldDoesNotExist(
                                f"The field '{field}' does not exist in the education data."
                            )
                        else:
                            setattr(education_instance_list[count], field, value)
                    education_instance_list[count].save()
                    count = count + 1
                except:
                    Education.objects.create(personal_info=instance, **item)

    def update_job(self, instance, validated_data):
        job_data = validated_data.pop("job")
        # for index, item in enumerate(job_data):
        if "accomplishment" not in job_data:
            raise serializers.ValidationError(
                f" key [ accomplishment ]does not exist in job."
            )

        job_list = [
            "company",
            "companyurl",
            "location",
            "title",
            "description",
            "job_start_date",
            "job_end_date",
            "is_current",
            "is_public",
            "image",
            "accomplishment",
        ]

        job_instance = Job.objects.filter(personal_info_job__id=instance.id)[0]
        if not job_instance:
            raise serializers.ValidationError(
                f"Job instances with Personal ID {instance.id} does not exist."
            )
        else:
            for field, value in job_data.items():
                if field != "accomplishment":
                    if field not in job_list:
                        raise serializers.FieldDoesNotExist(
                            f"The field '{field}' does not exist in the job data."
                        )
                    else:
                        setattr(job_instance, field, value)
            job_instance.save()

            job_accomp_instance = job_instance.accomplishment
            job_accomplishment_data = job_data.pop("accomplishment")
            # for index, item_ in enumerate(job_accomplishment_data):
            job_accomp_instance.job_accomplishment = job_accomplishment_data.get(
                "job_accomplishment", job_accomp_instance.job_accomplishment
            )
            job_accomp_instance.save()

    def update_skill_and_skill_level(self, instance, validated_data):
        if "skill" not in validated_data:
            raise serializers.ValidationError(f" key [ skill ]does not exist in Json.")
        SkillAndSkillLevel_data = validated_data.pop("skill")
        skill_instance_list = SkillAndSkillLevel.objects.filter(
            personal_info__id=instance.id
        )
        # if not skill_instance_list:
        #     raise serializers.ValidationError(
        #         f"skill instances with Personal ID {instance.id} does not exist."
        #     )
        attributes_list = ["text", "skill_level"]

        count = 0
        for item in SkillAndSkillLevel_data:
            try:
                for field, value in item.items():
                    if field not in attributes_list:
                        raise serializers.FieldDoesNotExist(
                            f"The field '{field}' does not exist in the Skill data."
                        )
                    else:
                        setattr(skill_instance_list[count], field, value)
                skill_instance_list[count].save()
                count = count + 1
            except:
                SkillAndSkillLevel.objects.create(personal_info=instance, **item)

    def update_programming_area(self, instance, validated_data):
        if "programming_area" not in validated_data:
            raise serializers.ValidationError(
                f" key [ programming_area ]does not exist in job."
            )
        ProgrammingArea_data = validated_data.pop("programming_area")

        # validates the fields
        self.validate_programming_area_model_fields(ProgrammingArea_data)
        programming_instance_list = ProgrammingArea.objects.filter(
            personal_info__id=instance.id
        )
        # if not programming_instance_list:
        #     raise serializers.ValidationError(
        #         f"Programming instances with Personal ID {instance.id} does not exist."
        #     )

        for index, item in enumerate(ProgrammingArea_data):
            try:
                for field, value in item.items():
                    if field not in [
                        "programming_area_name",
                        "programming_language_name",
                    ]:
                        raise serializers.FieldDoesNotExist(
                            f"The field '{field}' does not exist in the Programming Model data."
                        )
                    else:
                        setattr(programming_instance_list[index], field, value)
                programming_instance_list[index].save()
            except:
                ProgrammingArea.objects.create(personal_info=instance, **item)

    def update_projects(self, instance, validated_data):
        if "projects" not in validated_data:
            raise serializers.ValidationError(
                f" key [ projects ]does not exist in item."
            )
        Project_data = validated_data.pop("projects")
        project_attributes = [
            "project_name",
            "short_description",
            "long_description",
            "link",
        ]

        project_instance_list = Projects.objects.filter(personal_info__id=instance.id)
        # if not project_instance_list:
        #     raise serializers.ValidationError(
        #         f"Project instances with Personal ID {instance.id} does not exist."
        #     )
        for index, item in enumerate(Project_data):
            try:
                for field, value in item.items():
                    if field not in project_attributes:
                        raise serializers.FieldDoesNotExist(
                            f"The field '{field}' does not exist in the Project Model data."
                        )
                    else:
                        setattr(project_instance_list[index], field, value)
                project_instance_list[index].save()
            except:
                Projects.objects.create(personal_info=instance, **item)

    def update_publications(self, instance, validated_data):
        if "publications" not in validated_data:
            raise serializers.ValidationError(
                f" key [ publications ]does not exist in item."
            )
        publication_data = validated_data.pop("publications")
        publication_attributes = [
            "title",
            "authors",
            "journal",
            "year",
            "link",
        ]

        pub_instance_list = Publication.objects.filter(personal_info__id=instance.id)
        # if not pub_instance_list:
        #     # raise serializers.ValidationError(
        #     #     f"Publication instances with Personal ID {instance.id} does not exist."
        #     # )
        for index, item in enumerate(publication_data):
            try:
                for field, value in item.items():
                    if field not in publication_attributes:
                        raise serializers.FieldDoesNotExist(
                            f"The field '{field}' does not exist in the Publication Model data."
                        )
                    else:
                        setattr(pub_instance_list[index], field, value)
                pub_instance_list[index].save()
            except:
                Publication.objects.create(personal_info=instance, **item)


class PersonalInfo__Serializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "locality",
            "region",
            "title",
            "email",
            "linkedin",
            "facebook",
            "github",
            "site",
            "twittername",
        ]

    def update(self, instance, validated_data):
        self.update_personal_info(instance, validated_data)
        return instance

    def update_personal_info(self, instance, validated_data):
        fields_to_update = [
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "locality",
            "region",
            "title",
            "email",
            "linkedin",
            "facebook",
            "github",
            "site",
            "twittername",
        ]

        for field in fields_to_update:
            setattr(
                instance, field, validated_data.get(field, getattr(instance, field))
            )
        instance.save()


class EducationListCreateSerializer_Get_Request(serializers.ModelSerializer):
    education_start_date = serializers.DateField(format="%Y-%m-%d")
    education_end_date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Education
        fields = [
            "name",
            "location",
            "schoolurl",
            "education_start_date",
            "education_end_date",
            "degree",
            "description",
        ]


class JobSerializer_Get_Request(serializers.ModelSerializer):
    accomplishment = JobAccomplishmentSerializer()
    job_start_date = serializers.DateField(format="%Y-%m-%d")
    job_end_date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Job
        fields = [
            "company",
            "companyurl",
            "location",
            "title",
            "description",
            "job_start_date",
            "job_end_date",
            "is_current",
            "is_public",
            "image",
            "accomplishment",
        ]


class PersonalInfo_Serializer_Get_Request(PersonalInfo_Serializer):
    overview = OverviewSerializer()
    education = EducationListCreateSerializer_Get_Request(many=True)
    job = JobSerializer_Get_Request()
    skill = SkillAndSkillLevelSerializer(many=True)
    programming_area = ProgrammingAreaSerializer(many=True)
    projects = ProjectsSerializer(many=True)
    publications = PublicationSerializer(many=True)
