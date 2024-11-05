import json

from django.core.management.base import BaseCommand, CommandError
from apis_core.apis_relations.models import Property
from apis_ontology.models import Person, Family


class Command(BaseCommand):
    help = (
        "Ingest Schuh index entities from schuh_index.json"
    )

    def handle(self, *args, **options):
        with open("schuh_mappings.json", "w") as f:
            data = {}
            data.update({c.schuh_index_id: c.pk for c in Person.objects.all() if getattr(c, "schuh_index_id", None) })
            data.update({c.schuh_index_id: c.pk for c in Family.objects.all() if getattr(c, "schuh_index_id", None) })
            f.write(json.dumps(data))    