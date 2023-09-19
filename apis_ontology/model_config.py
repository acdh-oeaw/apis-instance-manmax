import apis_ontology.django_init

import datetime
import json

from django.db import models
from django.db.models.fields import Field
from django.db.models.fields.related import RelatedField
from icecream import ic


from apis_core.utils.caching import get_all_ontology_classes, get_contenttype_of_class, get_entity_class_of_name
from apis_core.apis_relations.models import Property

from apis_ontology.models import Factoid, Typology, construct_properties, overridden_properties


from django.contrib.postgres.fields import ArrayField



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
        
        if isinstance(field, Field) and not isinstance(field, (RelatedField, ArrayField)) and field.attname not in INTERNAL_FIELDS and field.editable:
           
            field_dict[field.attname] = {
                "field_type": TYPE_LOOKUP[type(field)].__name__,
                "blank": field.blank,
                "default": field.get_default(),
                "verbose_name": field.verbose_name,
                "help_text": field.help_text
                
            }
            if field.max_length:
                field_dict[field.attname]["max_length"] = field.max_length
            if field.choices:
                field_dict[field.attname]["choices"] = field.get_choices()
                
            
    return field_dict


def build_relations_dict(model_class):
    
    properties = Property.objects.filter(subj_class=get_contenttype_of_class(model_class))
    properties_to_override = set()
    if model_class in overridden_properties:
        properties_to_override = {prop.name.replace(" ", "_") for prop in overridden_properties[model_class]}
        #ic(model_class, properties_to_override)
    
    relations_dict = {}
    for property in properties:
        property_name = property.name_forward.replace(" ", "_").replace("/", "")
        omit_rels = getattr(model_class, "__omit_rels__", set())
        
     
        #ic(model_class, property)
        if property.name_forward != "has related statement" and property_name not in properties_to_override:
            relations_dict[property_name] = {"property_class": property, "allowed_types": [cls_contentttype.model_class().__name__.lower() for cls_contentttype in property.obj_class.all()]}
    return relations_dict

def build_relation_to_types(model_class):
    relations_to_entities = {}
    relations_to_statements = {}
    rels = build_relations_dict(model_class)
    for rel_name, rel_def in rels.items():
        related_types = set([getattr(get_entity_class_of_name(rel_type), "__entity_type__", "Entity") for rel_type in rel_def["allowed_types"]])
        if len(related_types) > 1:
            raise Exception(f"Model class {model_class} is related to Entities and Statements")
        related_type = related_types.pop()
        
        if related_type == "Entities":
            relations_to_entities[rel_name] = rel_def
        elif related_type == "Statements":
            relations_to_statements[rel_name] = rel_def
        
    return relations_to_entities, relations_to_statements
            
    

def build_model_config_dict(model_class):
    relations_to_entities, relations_to_statements = build_relation_to_types(model_class)
    return {
        "entity_type": model_class.__entity_type__, 
        "entity_group": model_class.__entity_group__,
        "fields": build_field_dict(model_class),
        "relations_to_entities": relations_to_entities,
        "relations_to_statements": relations_to_statements,
        "model_class": model_class,
        "verbose_name": model_class._meta.verbose_name,
        "verbose_name_plural": model_class._meta.verbose_name_plural
    }
    

def build_model_config():
    
    model_config = dict()
    for model in get_all_ontology_classes():
        if model not in [Factoid, Typology]:
            model_config[model.__name__.lower()] = build_model_config_dict(model)
    
    return model_config


model_config = build_model_config()

if __name__ == "__main__":
    construct_properties()
    #ic(overridden_properties)
    model_config = build_model_config()

    with open("model_config.json", "w") as f:
        f.write(json.dumps(model_config, default=lambda x: None))
    #build_relation_to_entity_dict(get_entity_class_of_name("order"))