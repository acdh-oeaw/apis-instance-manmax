import apis_ontology.django_init

from icecream import ic

from apis_core.apis_relations.models import Property, TempTriple
from apis_ontology.models import Person, Factoid
from apis_ontology.viewsets import get_unpack_factoid





def recursive_get_factoid(statement):
    tt = TempTriple.objects.filter(obj=statement).first()
    if isinstance(tt.subj, Factoid):
        return tt.subj
    else:
        return recursive_get_factoid(tt.subj)
    


import datetime

start = datetime.datetime.now()

person = Person.objects.filter(name__icontains="maximilian").first()
person = TempTriple.objects.filter(obj=person)
person_factoids = {recursive_get_factoid(tt.subj) for tt in person}
person_factoids_unpacked = [get_unpack_factoid(f.pk) for f in person_factoids]
end = datetime.datetime.now() - start

ic(person_factoids_unpacked)
ic(end.total_seconds())
ic(len(person_factoids))