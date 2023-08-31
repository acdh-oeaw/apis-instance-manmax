import apis_ontology.django_init

import json
from collections import defaultdict

from rest_framework import viewsets
from rest_framework.response import Response

from apis_core.apis_relations.models import TempTriple, Property
from apis_ontology.models import Factoid
from django.forms.models import model_to_dict
from apis_core.utils.caching import get_contenttype_of_class
from icecream import ic

from apis_ontology.model_config import model_config


    
    
FIELDS_TO_EXCLUDE = ["start_date", "start_start_date", "end_start_date", "end_date", "start_end_date", "end_end_date"]
    
def get_unpack_statement(obj):
    triples =TempTriple.objects.filter(subj=obj).all()
    return_dict = defaultdict(list)
    for triple in triples:
        rel_name = triple.prop.name_forward
        
        rel_obj = triple.obj
        ic(type(rel_obj))
        rel_obj_type = rel_obj.__class__.__name__.lower()
        related_obj_def = model_config[rel_obj_type]
        fields_to_get = related_obj_def["fields"].keys()
        current_obj_dict = {"__object_type__": rel_obj_type, **model_to_dict(rel_obj, fields=fields_to_get, exclude=FIELDS_TO_EXCLUDE), **get_unpack_statement(rel_obj)} if rel_obj.__entity_type__ == "Statements" else {"__object_type__": rel_obj_type, "id": rel_obj.id, "label": rel_obj.name}
        
        return_dict[rel_name].append(current_obj_dict)
        
    return return_dict
    
    
def get_unpack_factoid(pk):
    obj = Factoid.objects.get(pk=pk)
    return get_unpack_statement(obj)


def create_parse_statements(statements):
    created_statements = []
    for statement in statements:
        ic("Creating " + statement["__object_type__"])
        object_type_config = model_config[statement["__object_type__"]]
        fields = {k: v for k, v in statement.items() if k in object_type_config["fields"]}
        
        statement_obj = object_type_config["model_class"](**fields)
        statement_obj.save(auto_created=True)
        created_statements.append(statement_obj)

     
        for relation_name, related_entity_list in statement.items():
            if relation_name in object_type_config["relations"]:
                
                property_model = object_type_config["relations"][relation_name]["property_class"]
       
                
                related_statements = create_parse_statements([related_item for related_item in related_entity_list if model_config[related_item["__object_type__"]]["entity_type"] == "Statements"])
                related_entities = [related_item for related_item in related_entity_list if model_config[related_item["__object_type__"]]["entity_type"] == "Entities"]
                
                for related_entity in related_entities:
                    model_class = model_config[related_entity["__object_type__"]]["model_class"]
                    related_instance = model_class.objects.get(pk=related_entity["id"])
                    tt = TempTriple(subj=statement_obj, obj=related_instance, prop=property_model)
                    tt.save()
                    
                for related_statement in related_statements:
                    tt = TempTriple(subj=statement_obj, obj=related_statement, prop=property_model)
                    tt.save()
                
    return created_statements


def create_parse_factoid(data):
    factoid = Factoid()
    factoid.save(auto_created=True) #TODO: change auto_created to false for API
    statements = create_parse_statements(data["has_statement"])
    for statement in statements:
        statement_class = statement.__class__
        property_class = Property.objects.get(subj_class=get_contenttype_of_class(Factoid), obj_class=get_contenttype_of_class(statement_class), name_forward="has_statement")
        tt = TempTriple(subj=factoid, obj=statement, prop=property_class)
        tt.save()
        
    with open("test_write_output.json", "w") as f:
        f.write(json.dumps(get_unpack_factoid(factoid)))
    
        
        
class FactoidViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        return Response(get_unpack_factoid(pk=pk))
    
if __name__ == "__main__":
    with open("apis_ontology/test_new_factoid_data.json") as f:
        data = json.loads(f.read())
        create_parse_factoid(data)