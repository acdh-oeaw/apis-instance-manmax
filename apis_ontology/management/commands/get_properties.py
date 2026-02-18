import json

from django.core.management.base import BaseCommand, CommandError
from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_relations.models import Property


class Command(BaseCommand):
    help = "Writes schema to a file"
    def handle(self, *args, **options):

       for p in  Property.objects.all():
           for subj_ct in p.subj_class.all():
               print(subj_ct.model_class().__name__)


    
    
