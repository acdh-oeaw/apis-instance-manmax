from apis.urls import urlpatterns


from .viewsets import FactoidViewSet, AutocompleteViewSet, SolidJsView, EntityViewSet
from django.urls import path

from django.shortcuts import render
from django.templatetags.static import static

from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import user_passes_test

def frontend(request):
    return render(request, static("index.html"))
    

custom_url_patterns = [
    path("manmax/factoids", FactoidViewSet.as_view({"get": "list"}), name="list_factoid"),
    path("manmax/factoids/edit/<int:pk>", FactoidViewSet.as_view({"post": "update"}), name="factoid"),
    path("manmax/factoids/<int:pk>", FactoidViewSet.as_view({"get": "retrieve"}), name="factoid"),
    path("manmax/factoids/create", FactoidViewSet.as_view({"post": "create"}), name="create_factoid"),
    path("manmax/<str:entity_type>/create", EntityViewSet.as_view({"post": "create"}), name="create_entity"),
    path("manmax/factoid-builder/", login_required(SolidJsView.as_view()), name="solid"),
    path("manmax/autocomplete/<str:subj_entity_type>/<str:relation_name>", AutocompleteViewSet.as_view({"get": "list"}), name="autocomplete"),
    
]

urlpatterns += custom_url_patterns