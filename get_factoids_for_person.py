from apis_ontology import django_init

import json

from apis_core.apis_relations.models import TempTriple
from apis_ontology.models import Factoid, GenericStatement, Person
from apis_ontology.viewsets import get_unpack_factoid

""" target_persons = [
    53338,
    76036,
    51184,
    53935,
    51863,
    53938,
    55371,
    51576,
    74913,
    76062,
    75972,
    51604,
    52800,
    75185,
    85758,
    50986,
    51862,
    53420,
    53139,
    56063,
    54882,
    76482,
    54267,
    76070,
] """

target_persons = [Person.objects.first().pk]


def get_subj_until_factoid(pk):
    tt = TempTriple.objects.filter(obj=pk).first()
    if not tt:
        return None
    if isinstance(tt.subj, Factoid):
        print("Getting Factoid", tt.subj.pk)
        return tt.subj
    return get_subj_until_factoid(tt.subj.pk)


def persons():
    for person_pk in target_persons:
        yield from Person.objects.filter(pk=person_pk).all()


def generic_statement_subj():
    for person in persons():
        for item in person.triple_set_from_obj.iterator():
            yield item.subj


def direct_statements():
    for subj in generic_statement_subj():
        direct_statement = GenericStatement.objects.filter(pk=subj.pk).first()
        if factoid := get_subj_until_factoid(direct_statement.pk):
            yield factoid


def factoid_generator():

    yield from direct_statements()


print("=== UNPACKING FACTOIDS")


with open("factoid_from_person_output.json", "w") as f:
    factoid_ids_written = set()
    f.write("[\n")
    for i, factoid in enumerate(factoid_generator()):
        if factoid.pk in factoid_ids_written:
            continue
        else:
            factoid_ids_written.add(factoid.pk)

        print("Unpacking Factoid", factoid.pk)
        if unpacked_factoid := get_unpack_factoid(factoid.pk):
            if i > 0:
                f.write(",\n")
            f.write(json.dumps(unpacked_factoid, default=str))
    f.write("\n]")
