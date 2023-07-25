from apis.settings.base import *
import re
import dj_database_url
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# REDMINE_ID = "14590"
APIS_LIST_VIEWS_ALLOWED = False
APIS_DETAIL_VIEWS_ALLOWED = False
FEATURED_COLLECTION_NAME = "FEATURED"
# MAIN_TEXT_NAME = "ÖBL Haupttext"
BIRTH_REL_NAME = "geboren in"
DEATH_REL_NAME = "verstorben in"
APIS_LOCATED_IN_ATTR = ["located in"]
APIS_BASE_URI = "https://manmax.acdh.oeaw.ac.at/"
# APIS_OEBL_BIO_COLLECTION = "ÖBL Biographie"

APIS_SKOSMOS = {
    "url": os.environ.get("APIS_SKOSMOS", "https://vocabs.acdh-dev.oeaw.ac.at"),
    "vocabs-name": os.environ.get("APIS_SKOSMOS_THESAURUS", "apisthesaurus"),
    "description": "Thesaurus of the APIS project. Used to type entities and relations.",
}

APIS_BIBSONOMY = [
    {
        "type": "zotero",  # or zotero
        "url": "https://api.zotero.org",  # url of the bibsonomy instance or zotero.org
        "user": os.environ.get(
            "APIS_BIBSONOMY_USER"
        ),  # for zotero use the user id number found in settings
        "API key": os.environ.get("APIS_BIBSONOMY_PASSWORD"),
        "group": "2556736",
    }
]
APIS_BIBSONOMY_FIELDS = ["self"]
APIS_AUTOCOMPLETE_SETTINGS = "apis_ontology.settings.autocomplete_settings"

ALLOWED_HOSTS = re.sub(
    r"https?://",
    "",
    os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,manmax.acdh-dev.oeaw.ac.at"),
).split(",")
# You need to allow '10.0.0.0/8' for service health checks.

ALLOWED_CIDR_NETS = ["10.0.0.0/8", "127.0.0.0/8"]

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
    # "rest_framework.permissions.DjangoModelPermissions",
    "rest_framework.permissions.IsAuthenticated",
    # "rest_framework.permissions.DjangoObjectPermissions",
    # use IsAuthenticated for every logged in user to have global edit rights
)

# HAYSTACK_DEFAULT_OPERATOR = "OR"

DEBUG = True
DEV_VERSION = False

SPECTACULAR_SETTINGS["COMPONENT_SPLIT_REQUEST"] = True
SPECTACULAR_SETTINGS["COMPONENT_NO_READ_ONLY_REQUIRED"] = True

DATABASES = {}

# DATABASES["default"] = dj_database_url.parse(os.environ['DATABASE_LOCAL'], conn_max_age=600)
DATABASES["default"] = dj_database_url.config(conn_max_age=600)


MAIN_TEXT_NAME = "ÖBL Haupttext"

LANGUAGE_CODE = "de"

INSTALLED_APPS = ["apis_override_select2js"] + INSTALLED_APPS + ["apis_bibsonomy"]


MIDDLEWARE += ["apis_ontology.middleware.get_request.RequestMiddleware"]

# STATICFILES_DIRS = [BASE_DIR + "/member_images"]

# APIS_COMPONENTS = ['deep learning']

# APIS_BLAZEGRAPH = ('https://blazegraph.herkules.arz.oeaw.ac.at/metaphactory-play/sparql', 'metaphactory-play', 'KQCsD24treDY')


APIS_RELATIONS_FILTER_EXCLUDE += ["annotation", "annotation_set_relation"]

# INSTALLED_APPS.append("apis_highlighter")
APIS_ENTITIES = {
    "Factoid": {"search": ["name", "internal_notes"]},
    "Person": {"search": ["name", "internal_notes"]},
    "Place": {"search": ["name", "internal_notes"]},
    "GroupOfPersons": {"search": ["name", "internal_notes"]},
    "Organisation": {"search": ["name", "internal_notes"]},
    "ConceptualObject": {"search": ["name", "internal_notes"]},
    "CompositeConceptualObject": {"search": ["name", "internal_notes"]},
    "PhysicalObject": {"search": ["name", "internal_notes"]},
    "CompositePhysicalObject": {"search": ["name", "internal_notes"]},
    "AcceptanceOfStatement": {"search": ["name", "internal_notes"]},
    "Role": {"search": ["name", "internal_notes"]},
    "Task": {"search": ["name", "internal_notes"]},
    "FictionalPerson": {"search": ["name", "internal_notes"]},
    "GenericStatement": {"search": ["name", "internal_notes"]},
    "Activity": {"search": ["name", "internal_notes"]},
    "CreationCommission": {"search": ["name", "internal_notes"]},
    "OwnershipTransfer": {"search": ["name", "internal_notes"]},
    "ArmourAssemblyAct": {"search": ["name", "internal_notes"]},
    "ArmourCreationAct": {"search": ["name", "internal_notes"]},
    "ArtworkCreationAct": {"search": ["name", "internal_notes"]},
    "AssemblyOfCompositeObject": {"search": ["name", "internal_notes"]},
    "AssignmentToRole": {"search": ["name", "internal_notes"]},
    "CreationOfOrganisation": {"search": ["name", "internal_notes"]},
    "Authoring": {"search": ["name", "internal_notes"]},
    "Birth": {"search": ["name", "internal_notes"]},
    "CreationAct": {"search": ["name", "internal_notes"]},
    "Death": {"search": ["name", "internal_notes"]},
    "Dedication": {"search": ["name", "internal_notes"]},
    "Election": {"search": ["name", "internal_notes"]},
    "Family": {"search": ["name", "internal_notes"]},
    "Gendering": {"search": ["name", "internal_notes"]},
    "MusicPerformance": {"search": ["name", "internal_notes"]},
    "MusicWork": {"search": ["name", "internal_notes"]},
    "MarriageBeginning": {"search": ["name", "internal_notes"]},
    "MarriageEnd": {"search": ["name", "internal_notes"]},
    "Naming": {
        "search": [
            "name",
            "forename",
            "surname",
            "role_name",
            "add_name",
            "internal_notes",
        ]
    },
    "Order": {"search": ["name", "internal_notes"]},
    "OwnershipTransfer": {"search": ["name", "internal_notes"]},
    "ParentalRelation": {"search": ["name", "internal_notes"]},
    "Payment": {"search": ["name", "internal_notes"]},
    "PerformanceOfTask": {"search": ["name", "internal_notes"]},
    "PerformanceOfWork": {"search": ["name", "internal_notes"]},
    "PreparationOfConceptualText": {"search": ["name", "internal_notes"]},
    "Printing": {"search": ["name", "internal_notes"]},
    "Redacting": {"search": ["name", "internal_notes"]},
    "RemovalFromRole": {"search": ["name", "internal_notes"]},
    "RoleOccupation": {"search": ["name", "internal_notes"]},
    "SecretarialAct": {"search": ["name", "internal_notes"]},
    "SiblingRelation": {"search": ["name", "internal_notes"]},
    "TextualCreationAct": {"search": ["name", "internal_notes"]},
    "TextualWork": {"search": ["name", "internal_notes"]},
    "ArtisticWork": {"search": ["name", "internal_notes"]},
    "Battle": {"search": ["name", "internal_notes"]},
 
    "Arms": {"search": ["name", "internal_notes"]},
    "CommunicatesWith": {"search": ["name", "internal_notes"]},
    "MilitaryCampaign": {"search": ["name", "internal_notes"]},
    "Tournament": {"search": ["name", "internal_notes"]},
    "Festivity": {"search": ["name", "internal_notes"]},
    "ParticipationInEvent": {"search": ["name", "internal_notes"]},
    "UtilisationInEvent": {"search": ["name", "internal_notes"]},
    "DecorationOfObject": {"search": ["name", "internal_notes"]},
    "TransportationOfObject": {"search": ["name", "internal_notes"]},
    "RepairOfObject": {"search": ["name", "internal_notes"]},
}


# find out the path to the current settings file
# and use it to add a custom template path to
# the template backends
ONTOLOGY_DIR = os.path.dirname(os.path.dirname(__file__))

for template in TEMPLATES:
    template["DIRS"].append(os.path.join(ONTOLOGY_DIR, "templates"))
    template["OPTIONS"]["context_processors"].append(
        "apis_ontology.custom_context_processors.grouped_menus"
    )
