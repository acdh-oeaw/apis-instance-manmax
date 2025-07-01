from django.core.management.base import BaseCommand, CommandError
from apis_core.apis_relations.models import Property
from apis_ontology.models import Factoid
from apis_ontology.viewsets import get_unpack_factoid

import json

class Command(BaseCommand):
    help = (
        "Creates a dump of Factoid data"
    )

    def handle(self, *args, **options):
        data = []
        errors = []
        count = Factoid.objects.count()
        for i, factoid in enumerate(Factoid.objects.all()):
            print(f"Extracting factoid {i} of {count}: {factoid}")
            try:
                data.append(get_unpack_factoid(factoid.pk))
            except Exception as e:
                errors.append(f"{factoid.pk}: Error: {e}\n")
        with open("FactoidData.DUMP.json", "w") as f:
            f.write(json.dumps(data, default=str))
            
        with open("FactoidExtractionErrors.txt", "w") as f:
            f.writelines(errors)
            
       