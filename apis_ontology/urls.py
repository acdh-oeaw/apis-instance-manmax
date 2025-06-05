from apis.urls import urlpatterns


from .viewsets import (
    FactoidViewSet,
    AutocompleteViewSet,
    SolidJsView,
    EntityViewSet,
    PersonViewSet,
    EdiarumPersonViewset,
    EdiarumPlaceViewset,
    EdiarumOrganisationViewset,
    LeaderboardViewSet,
    UsersViewSet,
    ExampleViewSet
)
from django.urls import path, re_path

from django.shortcuts import render
from django.templatetags.static import static

from django.conf import settings
from django.contrib.auth.decorators import login_required as django_login_required

from django.contrib.auth.decorators import user_passes_test


def frontend(request):
    return render(request, static("index.html"))


def login_required(view):
    if settings.DEV_VERSION == True:
        return view
    return django_login_required(view)


custom_url_patterns = [
    path(
        "ediarum/organisation/",
        EdiarumOrganisationViewset.as_view(
            {"get": "list"}, name="ediarum-organisation"
        ),
    ),
    path(
        "ediarum/person/",
        EdiarumPersonViewset.as_view({"get": "list"}, name="ediarum-person"),
    ),
    path(
        "ediarum/place/",
        EdiarumPlaceViewset.as_view({"get": "list"}, name="ediarum-place"),
    ),
    path(
        "manmax/factoid-builder/create",
        login_required(SolidJsView.as_view()),
        name="solidcreate",
    ),
    re_path(
        r"manmax/factoid-builder/edit/\d*",
        login_required(SolidJsView.as_view()),
        name="solidedit",
    ),
    path(
        "manmax/factoid-builder/example",
        login_required(SolidJsView.as_view()),
        name="example_interface_list",
    ),
    path(
        "manmax/factoid-builder/example/create",
        login_required(SolidJsView.as_view()),
        name="example_interface_create",
    ),
    path(
        "manmax/factoid-builder/example/<int:pk>",
        login_required(SolidJsView.as_view()),
        name="example_interface_view",
    ),
 
    path("manmax/example/", 
         login_required(ExampleViewSet.as_view({"get": "list"})), 
         name="example_list"
    ),
    path("manmax/example/<int:pk>", 
         login_required(ExampleViewSet.as_view({"get": "retrieve"})), 
         name="example_get"
    ),
    path("manmax/example/create", 
         login_required(ExampleViewSet.as_view({"post": "create"})), 
         name="example_create_post"
    ),
    path("manmax/example/<int:pk>/", 
         login_required(ExampleViewSet.as_view({"post": "update"})), 
         name="example_update_post"
    ),
    path(
        "manmax/factoid-builder/leaderboard",
        login_required(SolidJsView.as_view()),
        name="leaderboardfrontend",
    ),
    
    path(
        "manmax/factoid-builder/", login_required(SolidJsView.as_view()), name="solid"
    ),
    path(
        "manmax/autocomplete/<str:subj_entity_type>/<str:relation_name>",
        login_required(AutocompleteViewSet.as_view({"get": "list"})),
        name="autocomplete",
    ),
    path(
        "manmax/leaderboard/",
        login_required(LeaderboardViewSet.as_view({"get": "list"})),
        name="list_viewset",
    ),
    path(
        "manmax/users/",
        login_required(UsersViewSet.as_view({"get": "list"})),
        name="list_users",
    ),
    path(
        "manmax/factoids/",
        login_required(FactoidViewSet.as_view({"get": "list"})),
        name="list_factoid",
    ),
    path(
        "manmax/factoids/edit/<int:pk>",
        login_required(FactoidViewSet.as_view({"post": "update"})),
        name="factoid",
    ),
    path(
        "manmax/factoids/<int:pk>",
        login_required(FactoidViewSet.as_view({"get": "retrieve"})),
        name="factoid",
    ),
    path(
        "manmax/factoids/create",
        login_required(FactoidViewSet.as_view({"post": "create"})),
        name="create_factoid",
    ),
    path(
        "manmax/factoids/api/create/",
        FactoidViewSet.as_view({"post": "create"}),
        name="create_factoid_api",
    ),
    path(
        "manmax/person/create",
        login_required(PersonViewSet.as_view({"post": "create"})),
        name="create_entity",
    ),
    path(
        "manmax/<str:entity_type>/create",
        login_required(EntityViewSet.as_view({"post": "create"})),
        name="create_entity",
    ),
]

urlpatterns += custom_url_patterns

