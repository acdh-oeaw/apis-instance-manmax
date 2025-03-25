import apis_ontology.django_init
from collections import deque
import datetime
import json

from django.db import models
from django.db.models.fields import Field
from django.db.models.fields.related import RelatedField


from apis_core.utils.caching import (
    get_all_ontology_classes,
    get_contenttype_of_class,
    get_entity_class_of_name,
)
from apis_core.apis_relations.models import Property

from apis_ontology.models import (
    Factoid,
    Typology,
    ManMaxTempEntityClass,
    construct_properties,
    overridden_properties,
)


from django.contrib.postgres.fields import ArrayField


INTERNAL_FIELDS = {"review", "status", "references", "published"}

TYPE_LOOKUP = {
    models.AutoField: int,
    models.CharField: str,
    models.BooleanField: bool,
    models.DateField: datetime.date,
    models.DateTimeField: datetime.datetime,
    models.TextField: str,
    models.JSONField: "json"
}


def build_field_dict(model_class):
    field_dict = {}
    for field in model_class._meta.get_fields():
        if (
            isinstance(field, Field)
            and not isinstance(field, (RelatedField, ArrayField))
            and field.attname not in INTERNAL_FIELDS
            and field.editable
        ):
            field_dict[field.attname] = {
                "field_type": TYPE_LOOKUP[type(field)] if TYPE_LOOKUP[type(field)] == "json" else TYPE_LOOKUP[type(field)].__name__,
                "blank": field.blank,
                "default": field.get_default(),
                "verbose_name": field.verbose_name,
                "help_text": field.help_text,
            }
            if field.max_length:
                field_dict[field.attname]["max_length"] = field.max_length
            if field.choices:
                field_dict[field.attname]["choices"] = field.get_choices()
    return field_dict


def build_relations_dict(model_class):
    properties = Property.objects.filter(
        subj_class=get_contenttype_of_class(model_class)
    )
    properties_to_override = set()
    if model_class in overridden_properties:
        properties_to_override = {
            prop.name.replace(" ", "_") for prop in overridden_properties[model_class]
        }
        # ic(model_class, properties_to_override)

    relations_dict = {}
    for property in properties:
        property_name = property.name_forward.replace(" ", "_").replace("/", "")
        omit_rels = getattr(model_class, "__omit_rels__", set())

        # ic(model_class, property)
        if (
            property.name_forward != "has related statement"
            and property_name not in properties_to_override
        ):
            relations_dict[property_name] = {
                "property_class": property,
                "allowed_types": [
                    cls_contentttype.model_class().__name__.lower()
                    for cls_contentttype in property.obj_class.all()
                ],
            }
    return relations_dict


def build_relation_to_types(model_class):
    relations_to_entities = {}
    relations_to_statements = {}
    rels = build_relations_dict(model_class)
    print(rels)
    for rel_name, rel_def in rels.items():
        related_types = set(
            [
                getattr(get_entity_class_of_name(rel_type), "__entity_type__", "Entity")
                for rel_type in rel_def["allowed_types"]
            ]
        )
        if len(related_types) > 1:
            raise Exception(
                f"Model class {model_class} on field {rel_name} is related to Entities and Statements: {rel_def['allowed_types']}"
            )
        related_type = related_types.pop()

        if related_type == "Entities":
            relations_to_entities[rel_name] = rel_def
        elif related_type == "Statements":
            relations_to_statements[rel_name] = rel_def

    return relations_to_entities, relations_to_statements


def get_parent_classes(model_class):
    parent_classes = deque()
    for c in model_class.mro():
        if c is ManMaxTempEntityClass:
            break
        if c is model_class:
            continue
        parent_classes.appendleft(c.__name__.lower())
    return list(parent_classes)

non_certainty_fields = {"id",
    "name",
    "internal_notes",
    "start_date",
    "start_start_date",
    "end_start_date",
    "end_date",
    "start_end_date",
    "end_end_date",
    "notes",
    "head_statement",
    "certainty_values"
    "certainty"}


def build_certainty_value_template(model_class):
    fields = {**build_field_dict(model_class), **build_relations_dict(model_class)}.keys()
    
    fields = [field for field in fields if field not in non_certainty_fields]

    return {field: {"certainty": 4, "notes": ""} for field in fields}

def build_model_config_dict(model_class):
    relations_to_entities, relations_to_statements = build_relation_to_types(
        model_class
    )
    return {
        "entity_type": model_class.__entity_type__,
        "entity_group": model_class.__entity_group__,
        "reified_relation": getattr(model_class, "__is_reified_relation_type__", False),
        "zotero_reference": getattr(model_class, "__zotero_reference__", False),
        "fields": build_field_dict(model_class),
        "relations_to_entities": relations_to_entities,
        "relations_to_statements": relations_to_statements,
        "model_class": model_class,
        "verbose_name": model_class._meta.verbose_name,
        "verbose_name_plural": model_class._meta.verbose_name_plural,
        "description": model_class.__doc__,
        "parent_classes": get_parent_classes(model_class),
        "subclasses": [c.__name__.lower() for c in model_class.__subclasses__()]
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
    print(overridden_properties)
    model_config = build_model_config()

    with open("model_config.json", "w") as f:
        f.write(json.dumps(model_config, default=lambda x: None))
    # build_relation_to_entity_dict(get_entity_class_of_name("order"))
