import apis_ontology.django_init

import json
from collections import defaultdict

from django.db import transaction
from django.views.generic import TemplateView

from rest_framework import viewsets
from rest_framework.response import Response

from apis_core.apis_relations.models import TempTriple, Property
from apis_ontology.models import Factoid, Gendering, Naming, Person, Place
from django.forms.models import model_to_dict
from apis_core.utils.caching import get_contenttype_of_class, get_entity_class_of_name
from apis_bibsonomy.models import Reference
from apis_bibsonomy.utils import get_bibtex_from_url

from django.shortcuts import render
from apis_ontology.model_config import model_config
from apis_ontology.utils import create_html_citation_from_csl_data_string
from django.db.models import Q


FIELDS_TO_EXCLUDE = [
    "start_date",
    "start_start_date",
    "end_start_date",
    "end_date",
    "start_end_date",
    "end_end_date",
]


def get_unpack_statement(obj):
    triples = TempTriple.objects.filter(subj=obj).all()
    return_dict = defaultdict(list)
    for triple in triples:
        rel_name = triple.prop.name_forward.replace(" ", "_")

        rel_obj = triple.obj
        rel_obj_type = rel_obj.__class__.__name__.lower()
        related_obj_def = model_config[rel_obj_type]
        fields_to_get = related_obj_def["fields"].keys()
        current_obj_dict = (
            {
                "__object_type__": rel_obj_type,
                **model_to_dict(
                    rel_obj, fields=fields_to_get, exclude=FIELDS_TO_EXCLUDE
                ),
                **get_unpack_statement(rel_obj),
            }
            if rel_obj.__entity_type__ == "Statements"
            else {
                "__object_type__": rel_obj_type,
                "id": rel_obj.id,
                "label": rel_obj.name,
            }
        )
        for related_statement_name in related_obj_def["relations_to_statements"]:
            if related_statement_name not in current_obj_dict:
                current_obj_dict[related_statement_name] = [{}]

        return_dict[rel_name].append(current_obj_dict)

    return return_dict


def get_unpack_factoid(pk):
    obj = Factoid.objects.get(pk=pk)
    try:
        ref = Reference.objects.get(object_id=pk)
        # ic(ref.__dict__)
        reference = {
            "id": ref.bibs_url,
            "text": create_html_citation_from_csl_data_string(ref.bibtex),
            "pages_start": ref.pages_start,
            "pages_end": ref.pages_end,
            "folio": ref.folio,
        }
    except:
        reference = None

    # print(str(ref), ref.bibtex)
    # reference["bibtex"] = json.loads(reference["bibtex"])
    # print(reference.__dict__)
    statements = get_unpack_statement(obj)
    statements["has_statements"]
    # print(statements["has_statement"])

    return_data = {
        "id": obj.id,
        "name": obj.name,
        "source": reference,
        "has_statements": statements["has_statement"],
    }
    print(return_data)
    return return_data


def create_parse_statements(statements):
    created_statements = []
    for statement in statements:
        try:
            if not statement.get("__object_type__"):
                print("missing statement type here")
                raise Exception("No Statement type: skip")
            object_type_config = model_config[statement["__object_type__"]]
        except Exception as e:
            continue

        fields = {
            k: v for k, v in statement.items() if k in object_type_config["fields"]
        }

        statement_obj = object_type_config["model_class"](**fields)
        statement_obj.save()
        created_statements.append(statement_obj)

        for relation_name, related_entity_list in statement.items():
            if relation_name in object_type_config["relations_to_entities"]:
                property_model = object_type_config["relations_to_entities"][
                    relation_name
                ]["property_class"]

                related_entities = [
                    related_item
                    for related_item in related_entity_list
                    if model_config[related_item["__object_type__"]]["entity_type"]
                    == "Entities"
                ]

                for related_entity in related_entities:
                    model_class = model_config[related_entity["__object_type__"]][
                        "model_class"
                    ]
                    related_instance = model_class.objects.get(pk=related_entity["id"])
                    tt = TempTriple(
                        subj=statement_obj, obj=related_instance, prop=property_model
                    )
                    tt.save()

            if relation_name in object_type_config["relations_to_statements"]:
                property_model = object_type_config["relations_to_statements"][
                    relation_name
                ]["property_class"]
                try:
                    related_statements = create_parse_statements(
                        [
                            related_item
                            for related_item in related_entity_list
                            if model_config[related_item["__object_type__"]][
                                "entity_type"
                            ]
                            == "Statements"
                        ]
                    )

                    for related_statement in related_statements:
                        tt = TempTriple(
                            subj=statement_obj,
                            obj=related_statement,
                            prop=property_model,
                        )
                        tt.save()
                except Exception as e:
                    continue

    return created_statements


def create_parse_factoid(data):
    factoid = Factoid(name=data["name"])
    factoid.save()

    for statement in data["has_statements"]:
        if not statement.get("__object_type__"):
            print("ERROR HERE")
            raise Exception("A statement type must be selected")

    statements = create_parse_statements(data["has_statements"])
    for statement in statements:
        statement_class = statement.__class__
        property_class = Property.objects.get(
            subj_class=get_contenttype_of_class(Factoid),
            obj_class=get_contenttype_of_class(statement_class),
            name_forward="has_statement",
        )
        tt = TempTriple(subj=factoid, obj=statement, prop=property_class)
        tt.save()

    reference_data = data["source"]
    # ic(reference_data)
    ref = Reference(
        bibs_url=reference_data["id"],
        bibtex=get_bibtex_from_url(reference_data["id"]),
        pages_start=reference_data.get("pages_start", None),
        pages_end=reference_data.get("pages_end", None),
        folio=reference_data.get("folio", None),
        object_id=factoid.pk,
        content_type=get_contenttype_of_class(Factoid),
    )
    # TODO add notes field!

    ref.save()
    # ic(ref.__dict__)

    return factoid


def recursive_delete_statements(statement):
    # print(statement)
    relations_to_statements = {
        k
        for k in model_config[statement.__class__.__name__.lower()][
            "relations_to_statements"
        ]
    }
    for relation_name in relations_to_statements:
        model_class_ct = get_contenttype_of_class(
            model_config[statement.__class__.__name__.lower()]["model_class"]
        )
        property = Property.objects.get(
            subj_class=model_class_ct, name_forward=relation_name.replace("_", " ")
        )
        temp_triples = TempTriple.objects.filter(subj=statement, prop=property)
        for temp_triple in temp_triples:
            recursive_delete_statements(temp_triple.obj)
    statement.delete()


def edit_parse_statements(related_entities, temp_triples_in_db):
    # temp_triples_in_db are for only one field!!!
    # print("==========")
    incoming_statements = {
        st.get("id"): st for st in related_entities if st.get("id", None)
    }

    for id, statement in incoming_statements.items():
        if not statement.get("__object_type__"):
            print("No statement type selected", statement)
            raise Exception("No statement type selected")

    for tt in temp_triples_in_db:
        object_type_config = model_config[tt.obj.__class__.__name__.lower()]

        # If related_entity is already there AND it's a statement, update...
        if (
            tt.obj.id in incoming_statements
            and object_type_config["entity_type"] == "Statements"
        ):
            # print("EXISTS", tt.obj)
            fields = {
                k: v
                for k, v in incoming_statements[tt.obj.id].items()
                if k in object_type_config["fields"]
            }
            for k, v in fields.items():
                # print(k, v)
                setattr(tt.obj, k, v)
            # print(tt.obj)
            tt.obj.save()  # TODO: save this now

            # do related entities once updating new...related_entities
            # If statement already exists, we need to update related entities for each field
            relation_to_entities = {
                k: v
                for k, v in incoming_statements[tt.obj.id].items()
                if k in object_type_config["relations_to_entities"]
            }
            for k, v in relation_to_entities.items():
                property = Property.objects.get(
                    subj_class=get_contenttype_of_class(
                        object_type_config["model_class"]
                    ),
                    name_forward=k.replace("_", " "),
                )
                inner_temp_triples_in_db = TempTriple.objects.filter(
                    subj=tt.obj, prop=property
                )
                inner_tt_in_db_by_obj_id = {
                    tt.obj.id for tt in inner_temp_triples_in_db
                }

                incoming_relation_to_entities_by_id = {item["id"] for item in v}
                for itt in inner_temp_triples_in_db:
                    if itt.obj.id not in incoming_relation_to_entities_by_id:
                        itt.delete()

                for incoming_relation in v:
                    if incoming_relation["id"] not in inner_tt_in_db_by_obj_id:
                        relation_object_to_add = model_config[
                            incoming_relation["__object_type__"]
                        ]["model_class"].objects.get(pk=incoming_relation["id"])
                        itt = TempTriple(
                            subj=tt.obj, obj=relation_object_to_add, prop=property
                        )
                        itt.save()

            # Relations to statements...

            relations_to_statements = {
                k: v
                for k, v in incoming_statements[tt.obj.id].items()
                if k in object_type_config["relations_to_statements"]
            }
            for k, v in relations_to_statements.items():
                property = Property.objects.get(
                    subj_class=get_contenttype_of_class(
                        object_type_config["model_class"]
                    ),
                    name_forward=k.replace("_", " "),
                )
                inner_temp_triples_in_db = TempTriple.objects.filter(
                    subj=tt.obj, prop=property
                )
                # Just call recursively
                statements_to_create = edit_parse_statements(
                    v, inner_temp_triples_in_db
                )
                for statement in statements_to_create:
                    itt = TempTriple(subj=tt.obj, obj=statement, prop=property)
                    itt.save()

                # print(inner_temp_triples_in_db)
            # print("RELATIONS", relations_to_statements)

            # Do update
        elif (
            model_config[tt.obj.__class__.__name__.lower()]["entity_type"]
            == "Statements"
        ):
            # if it is in the DB but not in Statements (and it's a statement) on the attached field, delete
            # recursively!
            recursive_delete_statements(tt.obj)

    # Now deal with new statements (FOR ONLY ONE KEY!)

    # If the statement is new, everything beneath it is also new.
    # so we create new statements all the way down;
    # and no need to do this 'triple already exists' business even on related Entities
    new_related_statements = [st for st in related_entities if not st.get("id", None)]

    # TODO: uncomment line below
    created_statements = create_parse_statements(new_related_statements)

    return created_statements


def edit_parse_factoid(data, pk):
    if data["id"] != pk:
        raise Exception
    factoid = Factoid.objects.get(pk=data["id"])
    factoid.name = data["name"]
    factoid.save()

    reference_data = data["source"]

    # When updating a reference, get the old references
    reference = Reference.objects.get(object_id=factoid.pk)

    # And then change the start and end pages and folio
    reference.pages_start = reference_data.get("pages_start", None)
    reference.pages_end = reference_data.get("pages_end", None)
    reference.folio = reference_data.get("folio", None)

    # If in fact we have selected a different source, update the id and bibtex
    if reference.bibs_url != reference_data["id"]:
        reference.bibs_url = reference_data["id"]
        reference.bibtex = get_bibtex_from_url(reference_data["id"])
    reference.save()

    has_statement_prop = Property.objects.get(
        subj_class=get_contenttype_of_class(Factoid), name_forward="has_statement"
    )
    temp_triples_in_db = TempTriple.objects.filter(
        subj_id=factoid.pk, prop=has_statement_prop
    )
    new_statements = edit_parse_statements(data["has_statements"], temp_triples_in_db)
    for statement in new_statements:
        tt = TempTriple(subj=factoid, obj=statement, prop=has_statement_prop)
        tt.save()

    return factoid


from rest_framework.decorators import authentication_classes, permission_classes


class AutocompleteViewSet(viewsets.ViewSet):
    def list(self, request, subj_entity_type=None, relation_name=None):
        print(subj_entity_type, model_config[subj_entity_type]["relations_to_entities"])
        relatable_type_names = model_config[subj_entity_type]["relations_to_entities"][
            relation_name
        ]["allowed_types"]

        if filter_by_type := request.query_params.get("filter_by_type", None):
            relatable_models = [model_config[filter_by_type]["model_class"]]
        else:
            relatable_models = [
                model_config[name]["model_class"] for name in relatable_type_names
            ]

        search_items = request.query_params["q"].lower().split(" ")

        q = Q()
        for si in search_items:
            q &= (Q(name__icontains=si) | Q(internal_notes__icontains=si))
            

        results = []
        for model in relatable_models:
            matches = [
                {
                    "label": match.name,
                    "id": match.id,
                    "__object_type__": model.__name__.lower(),
                }
                for match in model.objects.filter(q)
            ]
            results += matches
            
        def sort_func(match):
            try:
                return match["label"].lower().index(search_items[0])
            except:
                return 100
            

        # TODO: figure out why this sort does not work...
        results.sort(key=sort_func)

        return Response(results)


class FactoidViewSet(viewsets.ViewSet):
    def list(self, request):
        print(request.user)

        factoids = Factoid.objects.filter(name__icontains=request.query_params["q"])
        if request.query_params.get("currentUser"):
            factoids = factoids.filter(created_by=request.user.username)

        factoids = factoids.order_by("-modified_when")
        factoids_serializable = [
            {
                "id": f.id,
                "name": f.name,
                "created_by": f.created_by,
                "created_when": f.created_when,
                "modified_by": f.modified_by,
                "modified_when": f.modified_when,
            }
            for f in factoids
        ]
        return Response(factoids_serializable)

    def retrieve(self, request, pk=None):
        return Response(get_unpack_factoid(pk=pk))

    def create(self, request):
        with transaction.atomic():
            try:
                factoid = create_parse_factoid(request.data)
            except Exception as e:
                print("error", e)
                return Response(
                    {"message": f"Erstellung eines Factoids fehlgeschlagen: {str(e)}"},
                    status=400,
                )

            return Response(get_unpack_factoid(pk=factoid.pk))

    def update(self, request, pk=None):
        with transaction.atomic():
            try:
                factoid = edit_parse_factoid(request.data, pk)
            except Exception as e:
                print("error", e)
                return Response(
                    {"message": f"Erstellung eines Factoids fehlgeschlagen: {str(e)}"},
                    status=400,
                )
            return Response(get_unpack_factoid(pk=factoid.pk))


class SolidJsView(TemplateView):
    template_name = "apis_ontology/solid_index.html"


class EntityViewSet(viewsets.ViewSet):
    def create(self, request, entity_type=None):
        print(request.data)

        object_model_config = model_config[entity_type]

        fields = {
            k: v for k, v in request.data.items() if k in object_model_config["fields"]
        }
        related_entities = {
            k: v
            for k, v in request.data.items()
            if k in object_model_config["relations_to_entities"]
        }
        entity_class = get_entity_class_of_name(entity_type)
        new_entity = entity_class(**fields)
        new_entity.save()

        for relationName, relationObjects in related_entities.items():
            subj_contenttype = get_contenttype_of_class(
                object_model_config["model_class"]
            )
            property = Property.objects.get(
                subj_class=subj_contenttype, name_forward=relationName.replace("_", " ")
            )
            for relationObject in relationObjects:
                obj_model = model_config[relationObject["__object_type__"]][
                    "model_class"
                ]
                obj = obj_model.objects.get(pk=relationObject["id"])
                tt = TempTriple(subj=new_entity, obj=obj, prop=property)
                tt.save()

        if object_model_config["zotero_reference"]:
            if source_id := request.data.get("source", {}).get("id"):
                ref = Reference(
                    bibs_url=source_id,
                    bibtex=get_bibtex_from_url(source_id),
                    pages_start=None,
                    pages_end=None,
                    folio=None,
                    object_id=new_entity.pk,
                    content_type=get_contenttype_of_class(entity_class),
                )
                ref.save()

        return Response(
            {
                "__object_type__": new_entity.__class__.__name__.lower(),
                "label": new_entity.name,
                "id": new_entity.id,
            }
        )


class PersonViewSet(viewsets.ViewSet):
    def create(self, request):
        # ic("creating person")

        object_model_config = model_config["person"]

        fields = {
            k: v for k, v in request.data.items() if k in object_model_config["fields"]
        }
        related_entities = {
            k: v
            for k, v in request.data.items()
            if k in object_model_config["relations_to_entities"]
        }

        entity_class = get_entity_class_of_name("person")
        new_entity = entity_class(**fields)
        new_entity.save()

        gendering_info = (
            request.data.get("gendering", None)
            if request.data.get("gendering", {}).get("gender")
            else None
        )
        naming_info = (
            request.data.get("naming", None)
            if request.data.get("naming", None)
            and any(
                request.data["naming"][subfield]
                for subfield in ["forename", "surname", "role_name", "add_name"]
            )
            else None
        )
        # If there is a gendering, or if there is a naming and any of the fields have been filled out...
        if gendering_info or naming_info:
            # Create a factoid...

            factoid_name = f"{new_entity.name}"
            if naming_info:
                names = ""  # .join(request.data["naming"][subfield] for subfield in ["forename", "surname", "role_name", "add_name"]).strip()
                if request.data["naming"]["forename"]:
                    names += f"{request.data['naming']['forename']}"
                if request.data["naming"]["add_name"]:
                    names += f''' "{request.data['naming']['add_name']}"'''
                if request.data["naming"]["surname"]:
                    names += f" {request.data['naming']['surname']}"
                if request.data["naming"]["role_name"]:
                    names += f", {request.data['naming']['role_name']}"

                factoid_name += f" heißt {names}"

            if gendering_info and naming_info:
                factoid_name += " und"

            if gendering_info:
                if gendering_info["gender"] in {"männlich", "weiblich"}:
                    factoid_name += f" ist {gendering_info['gender']}"
                else:
                    factoid_name += " hat unbekanntes Geschlecht"

            factoid_name = factoid_name.strip()
            factoid = Factoid(name=factoid_name)
            factoid.save()

            has_statement_property = Property.objects.get(
                subj_class=get_contenttype_of_class(Factoid),
                name_forward="has_statement",
            )
            if gendering_info:
                gendering_name = (
                    f"[GENDERING] {new_entity.name} ist {gendering_info['gender']}"
                    if gendering_info["gender"] in {"männlich", "weiblich"}
                    else f"[GENDERING] {new_entity.name} hat unbekanntes Geschlecht"
                )
                gendering = Gendering(
                    name=gendering_name, gender=gendering_info["gender"]
                )
                gendering.save()

                gendering_to_person_property = Property.objects.get(
                    subj_class=get_contenttype_of_class(Gendering),
                    obj_class=get_contenttype_of_class(Person),
                )

                gendering_to_person_tt = TempTriple(
                    subj=gendering, obj=new_entity, prop=gendering_to_person_property
                )
                gendering_to_person_tt.save()

                factoid_to_gendering_tt = TempTriple(
                    subj=factoid, obj=gendering, prop=has_statement_property
                )
                factoid_to_gendering_tt.save()

            if naming_info:
                names = ""  # .join(request.data["naming"][subfield] for subfield in ["forename", "surname", "role_name", "add_name"]).strip()
                if request.data["naming"]["forename"]:
                    names += f"{request.data['naming']['forename']}"
                if request.data["naming"]["add_name"]:
                    names += f''' "{request.data['naming']['add_name']}"'''
                if request.data["naming"]["surname"]:
                    names += f" {request.data['naming']['surname']}"
                if request.data["naming"]["role_name"]:
                    names += f", {request.data['naming']['role_name']}"
                naming_name = f"[NENNUNG] {new_entity.name} heißt {names}"
                naming = Naming(name=naming_name, **request.data["naming"])

                naming.save()

                naming_to_person_property = Property.objects.get(
                    subj_class=get_contenttype_of_class(Naming),
                    obj_class=get_contenttype_of_class(Person),
                )
                naming_to_person_tt = TempTriple(
                    subj=naming, obj=new_entity, prop=naming_to_person_property
                )
                naming_to_person_tt.save()

                factoid_to_naming_tt = TempTriple(
                    subj=factoid, obj=naming, prop=has_statement_property
                )
                factoid_to_naming_tt.save()

            reference_data = request.data["source"]
            print(reference_data)
            ref = Reference(
                bibs_url=reference_data["id"],
                bibtex=reference_data["text"],
                pages_start=reference_data.get("pages_start", None),
                pages_end=reference_data.get("pages_end", None),
                folio=reference_data.get("folio", None),
                object_id=factoid.pk,
                content_type=get_contenttype_of_class(Factoid),
            )
            ref.save()

        for relationName, relationObjects in related_entities.items():
            subj_contenttype = get_contenttype_of_class(
                object_model_config["model_class"]
            )
            property = Property.objects.get(
                subj_class=subj_contenttype, name_forward=relationName.replace("_", " ")
            )
            for relationObject in relationObjects:
                obj_model = model_config[relationObject["__object_type__"]][
                    "model_class"
                ]
                obj = obj_model.objects.get(pk=relationObject["id"])
                tt = TempTriple(subj=new_entity, obj=obj, prop=property)
                tt.save()

        return Response(
            {
                "__object_type__": new_entity.__class__.__name__.lower(),
                "label": new_entity.name,
                "id": new_entity.id,
            }
        )


def sort_func(q, match):
    q_index = match["name"].lower().index(q) + ord(match["name"][0])
    return q_index


@authentication_classes([])
@permission_classes([])
class EdiarumPersonViewset(viewsets.ViewSet):
    def list(self, request):
        if not request.query_params.get("q", None):
            return Response(
                {"message": "A query parameter must be provided"}, status=401
            )
        q = request.query_params["q"].lower()
        persons = [
            model_to_dict(p) for p in Person.objects.filter(name__icontains=q)[0:100]
        ]

        persons.sort(key=lambda match: sort_func(q, match))
        response = render(request, "ediarum/list.xml", context={"data": persons})
        response["content-type"] = "application/xml"
        return response


@authentication_classes([])
@permission_classes([])
class EdiarumPlaceViewset(viewsets.ViewSet):
    def list(self, request):
        if not request.query_params.get("q", None):
            return Response(
                {"message": "A query parameter must be provided"}, status=401
            )

        q = request.query_params["q"].lower()
        places = [
            model_to_dict(p) for p in Place.objects.filter(name__icontains=q)[0:100]
        ]

        places.sort(key=lambda match: match["name"].lower().index(q))
        response = render(request, "ediarum/list.xml", context={"data": places})
        response["content-type"] = "application/xml"
        return response


if __name__ == "__main__":
    with open("apis_ontology/test_edit_factoid_data.json") as f:
        data = json.loads(f.read())
        edit_parse_factoid(data)
