from django.core.management.base import BaseCommand, CommandError
from apis_core.apis_relations.models import Property
from apis_ontology.models import Factoid
from apis_ontology.viewsets import get_unpack_factoid

import json

class Command(BaseCommand):
    help = (
        "Create and label relationships between entities by running "
        "the construct_properties() function in your app's models.py file."
    )

    def handle(self, *args, **options):
        data = []
        errors = []
        for factoid in Factoid.objects.all():
            try:
                data.append(get_unpack_factoid(factoid.pk))
            except Exception as e:
                errors.append(f"{factoid.pk}: Error: {e}\n")
        with open("FactoidData.BACKUP.json", "w") as f:
            f.write(json.dumps(data))
            
        with open("FactoidExtractionErrors.txt", "w") as f:
            f.writelines(errors)
            
       