import apis_ontology.django_init

import datetime
import json

from django.db import models
from django.db.models.fields import Field
from django.db.models.fields.related import RelatedField
from icecream import ic


from apis_core.utils.caching import get_all_ontology_classes, get_contenttype_of_class
from apis_core.apis_relations.models import Property

from apis_ontology.models import Factoid

model_config = dict()

INTERNAL_FIELDS = {"review", "status", "references", "published"}

TYPE_LOOKUP = {
    models.AutoField: int,
    models.CharField: str,
    models.BooleanField: bool,
    models.DateField: datetime.date,
    models.DateTimeField: datetime.datetime,
    models.TextField: str
}


def build_field_dict(model_class):
   
    field_dict = {}
    for field in model_class._meta.get_fields():
        
        if isinstance(field, Field) and not isinstance(field, (RelatedField)) and field.attname not in INTERNAL_FIELDS and field.editable:
            
            field_dict[field.attname] = {
                "field_type": TYPE_LOOKUP[type(field)].__name__,
                "blank": field.blank,
                "default": field.get_default()
                
            }
            if field.max_length:
                field_dict[field.attname]["max_length"] = field.max_length
            if field.choices:
                field_dict[field.attname]["choices"] = field.get_choices()    
            
    return field_dict


def build_relations_dict(model_class):
    
    
    properties = Property.objects.filter(subj_class=get_contenttype_of_class(model_class))
 
    
    relations_dict = {}
    for property in properties:
        property_name = property.name_forward.replace(" ", "_")
        omit_rels = getattr(model_class, "__omit_rels__", set())
        
     
        
        if property.name_forward != "has related statement" and property_name not in omit_rels:
            relations_dict[property_name] = {"property_class": property, "allowed_types": [cls_contentttype.model_class().__name__.lower() for cls_contentttype in property.obj_class.all()]}
    return relations_dict

def build_model_config_dict(model_class):
    
    return {
        "entity_type": model_class.__entity_type__, 
        "entity_group": model_class.__entity_group__,
        "fields": build_field_dict(model_class),
        "relations": build_relations_dict(model_class),
        "model_class": model_class
    }
    


for model in get_all_ontology_classes():
    if model is not Factoid:
        model_config[model.__name__.lower()] = build_model_config_dict(model)
    
    
#ic(model_config)
"""
with open("model_config.json", "w") as f:
    f.write(json.dumps(model_config))
"""