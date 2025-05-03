from drf_spectacular.utils import extend_schema_field, OpenApiTypes
from rest_framework import serializers
from rest_framework.fields import DateField


@extend_schema_field(OpenApiTypes.DATE)
class CustomDateField(DateField):
    pass


schema_personalinfo_serializer = {
    "first_name": "Katie",
    "middle_name": "Jill",
    "last_name": "Davis",
    "suffix": "DDS",
    "locality": "Jessica_mouth",
    "region": "Alabama",
    "title": "Accountant, chartered",
    "email": "greenkelli@example.com",
    "linkedin": "http://hutchinson.org/",
    "facebook": "http://gregory.com/",
    "github": "http://www.thomas-harper.com/",
    "site": "http://www.phelps-hicks.com/",
    "twittername": "samuel90",
    "overview": {
        "text": "Whether order talk want result professor professional. Staff growth individual window player those five. Child government name around about.\nMoment ok hot court."
    },
    "education": [
        {
            "name": "eight",
            "location": "North Jon",
            "schoolurl": "https://www.stone-logan.com/",
            "education_start_date": {
                "01-01-2020": True,
                "2021-01-31": True,
            },
            "education_end_date": {
                "01-01-2020": True,
                "2021-01-31": True,
            },
            "degree": " degree",
            "description": "Onto production back. Response gun read child.",
        }
    ],
    "job": {
        "company": "Rodgers-Johnson_________________",
        "companyurl": "http://www.osborne.net/",
        "location": "Charlesville",
        "title": "Surveyor, building control_________________",
        "description": "Friend south start do win. Late wrong bank between.",
        "job_start_date": {
            "01-01-2020": True,
            "2021-01-31": True,
        },
        "job_end_date": {
            "01-01-2020": True,
            "2021-01-31": True,
        },
        "is_current": True,
        "is_public": True,
        "image": "",
        "accomplishment": {
            "job_accomplishment": "Range him around morning buy rest process."
        },
    },
    "skill": [{"text": "thing", "skill_level": "Expert"}],
    "programming_area": [
        {"programming_area_name": "FRONTEND", "programming_language_name": "TypeScript"}
    ],
    "projects": [
        {
            "project_name": "challenge",
            "short_description": "Throw list describe walk true stand try. Record miss year war stand direction. Office six car south gun.",
            "long_description": "Short do machine PM value boy onto. Above company herself.",
            "link": "https://www.allen-wall.com/",
        },
        {
            "project_name": "theory",
            "short_description": "Product community scene network ground minute and. American require individual well.",
            "long_description": "Usually through hear share share current course. That science floor subject war remember deep best. Throw box along real.",
            "link": "http://www.pugh.com/",
        },
    ],
    "publications": [
        {
            "title": "Receive game we kind or.",
            "authors": "Lauren Wilson",
            "journal": "grow",
            "year": "2017",
            "link": "http://wilkerson.org/",
        },
        {
            "title": "Through floor close everything.",
            "authors": "Amy Joseph",
            "journal": "police",
            "year": "1980",
            "link": "http://www.davis.net/",
        },
    ],
}
