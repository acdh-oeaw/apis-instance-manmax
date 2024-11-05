from django.core.management.base import BaseCommand, CommandError
from apis_core.apis_relations.models import Property
from apis_ontology.models import construct_properties


class Command(BaseCommand):
    help = (
        "Ingest Schuh index entities from schuh_index.json"
    )

    def handle(self, *args, **options):
        from apis_ontology.ontology_specific_scripts.ingest_schuh import ingest_schuh
        ingest_schuh()