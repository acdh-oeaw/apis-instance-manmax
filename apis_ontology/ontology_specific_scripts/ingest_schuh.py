import json
from apis_ontology.models import Person, Place, Family, Organisation, GroupOfPersons, Battle, GenericEvent, Tournament, Role
from apis_core.apis_metainfo.models import Uri
"""
'aspell',
            'battle',
            'callname',
            'comptext',
            'corr',
            'event',
            'family',
            'group',
            'keyword',
            'org',
            'person',
            'place',
            'ref',
            'role',
            'role ',
          
            'tournament'"""


def ingest_schuh():
    with open("apis_ontology/ontology_specific_scripts/schuh_index.json") as f:
        read_file = f.read()
        data = json.loads(read_file)

    for entity_model, entity_type in [
        (Person, "person"),
        (Place, "place"),
        (Family, "family"),
        (Organisation, "org"),
        (GroupOfPersons, "group"),
        (Battle, "battle"),
        (Tournament, "tournament"),
        (Role, "role")
    ]:
        for entity_data in data[entity_type]:
            try:
                e = entity_model.objects.get(schuh_index_id=entity_data["id"])
                print("Alredy exists", entity_type, e)
            except entity_model.DoesNotExist:
                print("Ingesting", entity_type, entity_data)
                entity = entity_model(
                    name=entity_data["label"] + f" [{entity_type}]",
                    created_by="schuh_index",
                    modified_by="schuh_index",
                    schuh_index_id=entity_data["id"],
                    alternative_schuh_ids=entity_data["additional_ids"]
                )
                entity.save(auto_created=True)


def run(*args, **options):
    def main_run():
        ingest_schuh()

    main_run()
