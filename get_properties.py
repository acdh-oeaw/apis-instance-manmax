from apis_ontology import django_init

from apis_core.apis_relations.models import Property
from collections import defaultdict
from django.db import models
import datetime
import json

from apis_core.utils.caching import (
    get_all_ontology_classes,
    get_contenttype_of_class,
    get_entity_class_of_name,
)
from django.db.models.fields.related import RelatedField
from django.db.models.fields import Field
from django.contrib.postgres.fields import ArrayField

from pprint import pprint




INTERNAL_FIELDS = {"review", "status", "references", "published", "head_statement", "reconcile_text", "certainty", "certainty_values"}

PROPERTY_LIST = []


for p in  Property.objects.all():
    property_def = {"name": p.name, "reverse_name": p.name_reverse, "domain": [], "range": []}
    for subj_ct in p.subj_class.all():
        property_def["domain"].append(subj_ct.model_class().__name__)
        
    for obj_ct in p.obj_class.all():
        property_def["range"].append(obj_ct.model_class().__name__)
    
    PROPERTY_LIST.append(property_def)




TYPE_LOOKUP = {
    models.AutoField: "int",
    models.CharField: "string",
    models.BooleanField: "Boolean",
    models.DateField: "date",
    models.DateTimeField: "datetime",
    models.TextField: "string",
    models.JSONField: "json"
}

FIELD_MAP = defaultdict(lambda: {"name": None, "domain": [], "range": []  })

for c in get_all_ontology_classes():
    for f in c._meta.get_fields():
        if (
            isinstance(f, Field)
            and not isinstance(f, (RelatedField, ArrayField))
            and f.attname not in INTERNAL_FIELDS
            and f.editable
        ):
            #print(TYPE_LOOKUP[type(f)])
            FIELD_MAP[f.name]["name"] = f.name
            FIELD_MAP[f.name]["domain"].append(c.__name__)
            FIELD_MAP[f.name]["range"].append(TYPE_LOOKUP[type(f)])
            FIELD_MAP[f.name]["range"] = list(set(FIELD_MAP[f.name]["range"]))

PROPERTY_LIST.extend(FIELD_MAP.values())


with open("property_types.json", "w") as f:    
    f.write(json.dumps(PROPERTY_LIST, indent=4, ensure_ascii=False))
    
    

STATEMENT_LIST = []
ENTITY_LIST = []
for c in get_all_ontology_classes():
    if hasattr(c, "__entity_type__") and c.__entity_type__ == "Statements":
        STATEMENT_LIST.append(c.__name__)
        
    if hasattr(c, "__entity_type__") and c.__entity_type__ == "Entities":
        ENTITY_LIST.append(c.__name__)


with open("statement_types.json", "w") as f:
    f.write(json.dumps(STATEMENT_LIST, indent=4, ensure_ascii=False))
    
with open("entity_types.json", "w") as f:
    f.write(json.dumps(ENTITY_LIST, indent=4, ensure_ascii=False))