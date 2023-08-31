from apis.urls import urlpatterns


from .viewsets import FactoidViewSet
from django.urls import path

custom_url_patterns = [
    path("manmax/factoids/<int:pk>", FactoidViewSet.as_view({"get": "retrieve"}), name="factoid")
]

urlpatterns += custom_url_patterns