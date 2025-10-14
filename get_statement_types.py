import apis_ontology.django_init
from apis_ontology.models import GenericStatement

def recursive_get_subclasses(c):
    items = []
    for sc in c.__subclasses__():
        items.append(sc)
        items.extend(recursive_get_subclasses(sc))
    return items

with open("statement_types.csv", "w") as f:
    for c in recursive_get_subclasses(GenericStatement):
        f.write(f"{c._meta.verbose_name},{c.__name__}\n")