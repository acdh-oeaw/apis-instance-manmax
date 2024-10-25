from django.core.management.base import BaseCommand, CommandError

from apis_ontology.models import GenericStatement


import json

class Command(BaseCommand):
    help = (
        "Add Certainty Values to Statements"
    )

    def handle(self, *args, **options):
        print("running")
        for gs in GenericStatement.objects.all():
            gs.build_certainty_value_blank()
            gs.save(auto_created=True)
            
            
       