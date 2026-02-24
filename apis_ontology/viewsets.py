import json
from collections import Counter, OrderedDict, defaultdict

from apis_bibsonomy.models import Reference
from apis_bibsonomy.utils import get_bibtex_from_url
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response

from apis_core.apis_relations.models import Property, TempTriple
from apis_core.utils.caching import get_contenttype_of_class, get_entity_class_of_name
from apis_ontology.model_config import model_config
from apis_ontology.models import (
    Example,
    Factoid,
    Gendering,
    Naming,
    Organisation,
    Person,
    Place,
    Unreconciled,
)
from apis_ontology.utils import create_html_citation_from_csl_data_string

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
            else (
                {
                    "__object_type__": rel_obj_type,
                    "id": rel_obj.id,
                    "label": rel_obj.name,
                    "unreconciled_type": rel_obj.unreconciled_type,
                }
                if rel_obj_type == "unreconciled"
                else {
                    "__object_type__": rel_obj_type,
                    "id": rel_obj.id,
                    "label": rel_obj.name,
                }
            )
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
    except Exception:

        reference = None

    # print(str(ref), ref.bibtex)
    # reference["bibtex"] = json.loads(reference["bibtex"])
    # print(reference.__dict__)
    statements = get_unpack_statement(obj)
    statements["has_statements"]
    # print(statements["has_statement"])

    return_data = {
        "id": obj.id,
        "review": {
            "reviewed": obj.reviewed,
            "reviewed_by": obj.review_by,
            "review_notes": obj.review_notes,
            "problem_flagged": obj.problem_flagged,
            "contains_unreconciled": obj.contains_unreconciled,
        },
        "name": obj.name,
        "source": reference,
        "has_statements": statements["has_statement"],
        "created_by": obj.created_by,
        "created_when": obj.created_when,
        "modified_by": obj.modified_by,
        "modified_when": obj.modified_when,
    }
    # print(return_data)
    return return_data


def create_inline_reified_relation(data):
    object_model_config = model_config[data["__object_type__"]]

    fields = {k: v for k, v in data.items() if k in object_model_config["fields"]}
    related_entities = {
        k: v
        for k, v in data.items()
        if k in object_model_config["relations_to_entities"]
    }
    entity_class = get_entity_class_of_name(data["__object_type__"])
    new_entity = entity_class(**fields)
    new_entity.save()

    for relationName, relationObjects in related_entities.items():
        subj_contenttype = get_contenttype_of_class(object_model_config["model_class"])
        property = Property.objects.get(
            subj_class=subj_contenttype, name_forward=relationName.replace("_", " ")
        )
        for relationObject in relationObjects:
            obj_model = model_config[relationObject["__object_type__"]]["model_class"]
            obj = obj_model.objects.get(pk=relationObject["id"])
            tt = TempTriple(subj=new_entity, obj=obj, prop=property)
            tt.save()
    return new_entity


def create_parse_statements(statements):
    created_statements = []
    for statement in statements:
        try:
            if not statement.get("__object_type__", None):
                print("missing statement type here")
                raise Exception("No Statement type: skip")
            object_type_config = model_config[statement["__object_type__"]]
        except Exception:
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

                for related_item in related_entity_list:
                    if model_config[related_item["__object_type__"]][
                        "reified_relation"
                    ] and not related_item.get("id", None):
                        new_entity = create_inline_reified_relation(related_item)
                        tt = TempTriple(
                            subj=statement_obj, obj=new_entity, prop=property_model
                        )
                        tt.save()

                related_entities = [
                    related_item
                    for related_item in related_entity_list
                    if model_config[related_item["__object_type__"]]["entity_type"]
                    == "Entities"
                    and not (
                        model_config[related_item["__object_type__"]][
                            "reified_relation"
                        ]
                        and not related_item.get("id", None)
                    )
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

                unreconciled_entities = [
                    related_item
                    for related_item in related_entity_list
                    if related_item["__object_type__"] == "unreconciled"
                ]
                # print(unreconciled_entities)
                for unreconciled_entity in unreconciled_entities:
                    unreconciled_name = unreconciled_entity.get(
                        "name", unreconciled_entity.get("label")
                    )
                    unreconciled_object = Unreconciled(
                        name=unreconciled_name,
                        unreconciled_type=unreconciled_entity["unreconciled_type"],
                    )
                    unreconciled_object.save()
                    tt = TempTriple(
                        subj=statement_obj, obj=unreconciled_object, prop=property_model
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
                except Exception:
                    continue

    return created_statements


def contains_unreconciled(data):
    for k, v in data.items():
        if k == "__object_type__" and (
            v == "unreconciled" or v == "unknownstatementtype"
        ):
            return True

        if isinstance(v, list):
            for item in v:
                if contains_unreconciled(item):
                    return True

    return False


def create_parse_factoid(data):

    factoid = Factoid(
        name=data["name"], contains_unreconciled=contains_unreconciled(data)
    )
    factoid.save()

    for statement in data["has_statements"]:
        if not statement.get("__object_type__", None):

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

                        if isinstance(itt.obj, Unreconciled):
                            itt.obj.delete()

                for incoming_relation in v:

                    if incoming_relation["id"] not in inner_tt_in_db_by_obj_id:
                        relation_object_to_add = model_config[
                            incoming_relation["__object_type__"]
                        ]["model_class"].objects.get(pk=incoming_relation["id"])

                        if "reconcileValue" in incoming_relation:

                            if not relation_object_to_add.reconcile_text:
                                relation_object_to_add.reconcile_text = ""

                            if (
                                incoming_relation["reconcileValue"]
                                not in relation_object_to_add.reconcile_text
                            ):

                                relation_object_to_add.reconcile_text += (
                                    f" {incoming_relation['reconcileValue']}"
                                )
                            relation_object_to_add.save()

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
            print(relations_to_statements)
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


def edit_parse_factoid(data, pk, user=""):
    if data["id"] != pk:
        raise Exception
    factoid = Factoid.objects.get(pk=data["id"])
    factoid.name = data["name"]
    factoid.contains_unreconciled = contains_unreconciled(data)

    if data.get("review", {}).get("reviewed") and (
        factoid.reviewed != data.get("review", {}).get("reviewed")
        or factoid.review_notes != data.get("review", {}).get("review_notes")
        or factoid.problem_flagged != data.get("review", {}).get("problem_flagged")
    ):
        if (
            factoid.review
            and ", " in factoid.review
            and factoid.review_by.split(", ")[-1] != str(user)
        ):
            factoid.review_by = (
                str(factoid.review_by) + ", " + str(user)
                if factoid.review_by
                else str(user)
            )
        else:
            factoid.review_by = str(user)

    factoid.problem_flagged = data.get("review", {}).get("problem_flagged") or False
    factoid.reviewed = data.get("review", {}).get("reviewed") or False
    factoid.review_notes = data.get("review", {}).get("review_notes") or ""

    factoid.save()

    try:
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
    except Exception:
        reference_data = data["source"]
        reference = Reference(
            bibs_url=reference_data["id"],
            bibtex=get_bibtex_from_url(reference_data["id"]),
            pages_start=reference_data.get("pages_start", None),
            pages_end=reference_data.get("pages_end", None),
            folio=reference_data.get("folio", None),
            object_id=factoid.pk,
            content_type=get_contenttype_of_class(Factoid),
        )
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


@authentication_classes([])
@permission_classes([])
class UsersViewSet(viewsets.ViewSet):
    def list(self, request):
        results = [user.username for user in User.objects.all()]
        return Response(results)


class AutocompleteViewSet(viewsets.ViewSet):
    def list(self, request, subj_entity_type=None, relation_name=None):
        # (subj_entity_type, model_config[subj_entity_type]["relations_to_entities"])
        relatable_type_names = model_config[subj_entity_type]["relations_to_entities"][
            relation_name
        ]["allowed_types"]

        if filter_by_type := request.query_params.get("filter_by_type", None):
            relatable_models = [model_config[filter_by_type]["model_class"]]
        else:
            relatable_models = [
                model_config[name]["model_class"]
                for name in relatable_type_names
                if name != "unreconciled" and name != "typology"
            ]

        search_items = request.query_params["q"].lower().split(" ")
        count = int(request.query_params.get("count", 100))

        q = Q()
        for si in search_items:
            q &= Q(name__icontains=si)

            if hasattr(relatable_models, "internal_notes"):
                q |= Q(internal_notes__icontains=si)

            if hasattr(relatable_models, "reconcile_text"):
                q |= Q(reconcile_text__icontains=si)

        results = []
        for model in relatable_models:
            if len(results) < count:
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

        return Response(results[0:count])


PAGE_SIZE = 200


class FactoidViewSet(viewsets.ViewSet):
    def ids(self, request):
        return Response([f.pk for f in Factoid.objects.all()])
    
    def list(self, request):
        search_tokens = request.query_params.get("q", "").lower().split(" ")
        if not search_tokens:
            return Response({"message", "No search string"}, status=401)

        q = Q()
        for search_token in search_tokens:
            q &= Q(name__icontains=search_token)

        factoids = Factoid.objects.filter(q)

        if request.query_params.get("currentUser"):
            factoids = factoids.filter(created_by=request.user.username)

        if statusFilter := request.query_params.get("status"):
            print(statusFilter)
            if statusFilter == "unchecked":
                factoids = factoids.filter(reviewed=False)
            elif statusFilter == "checked":
                factoids = factoids.filter(reviewed=True, problem_flagged=False)
            elif statusFilter == "error":
                factoids = factoids.filter(reviewed=True, problem_flagged=True)
            elif statusFilter == "containsUnreconciled":
                factoids = factoids.filter(contains_unreconciled=True)

        if userFilter := request.query_params.get("user"):
            factoids = factoids.filter(created_by=userFilter)

        count = factoids.count()

        lower_bound = 0
        upper_bound = PAGE_SIZE

        if page_number := request.query_params.get("page"):
            page_number = int(page_number)
            lower_bound = (page_number - 1) * PAGE_SIZE
            upper_bound = page_number * PAGE_SIZE

        factoids = factoids.order_by("-modified_when")[lower_bound:upper_bound]

        factoids_serializable = {
            "count": count,
            "factoids": [
                {
                    "id": f.id,
                    "name": f.name,
                    "created_by": f.created_by,
                    "created_when": f.created_when,
                    "modified_by": f.modified_by,
                    "modified_when": f.modified_when,
                    "reviewed": f.reviewed,
                    "problem_flagged": f.problem_flagged,
                    "contains_unreconciled": f.contains_unreconciled,
                }
                for f in factoids
            ],
        }
        return Response(factoids_serializable)

    def retrieve(self, request, pk=None):
        return Response(get_unpack_factoid(pk=pk))

    def create(self, request):

        try:
            with transaction.atomic():
                factoid = create_parse_factoid(request.data)
        except Exception as e:
            print("ERROR CREATING FACTOID", e)
            # print(traceback.format_exc())
            return Response(
                {"message": f"Erstellung eines Factoids fehlgeschlagen: {str(e)}"},
                status=400,
            )

        return Response(get_unpack_factoid(pk=factoid.pk))

    def update(self, request, pk=None):

        try:
            with transaction.atomic():
                factoid = edit_parse_factoid(request.data, pk, request.user)
        except Exception as e:
            print("error", e)
            return Response(
                {"message": f"Erstellung eines Factoids fehlgeschlagen: {str(e)}"},
                status=400,
            )
        return Response(get_unpack_factoid(pk=factoid.pk))

    def current_dump(self, request):
        with open("FactoidData.DUMP.json") as f:
            data = json.loads(f.read())
        return Response(data)


class SolidJsView(TemplateView):
    template_name = "apis_ontology/solid_index.html"


class EntityViewSet(viewsets.ViewSet):
    def create(self, request, entity_type=None):
        print(">>", request.data)

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
        from apis_ontology.model_config import build_certainty_value_template

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
                    name=gendering_name,
                    gender=gendering_info["gender"],
                    certainty={"certainty": 4, "notes": ""},
                    certainty_values=build_certainty_value_template(Gendering),
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
                naming = Naming(
                    name=naming_name,
                    certainty={"certainty": 4, "notes": ""},
                    certainty_values=build_certainty_value_template(Naming),
                    **request.data["naming"],
                )

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
            # print(reference_data)
            # print(get_bibtex_from_url(reference_data["id"]))
            ref = Reference(
                bibs_url=reference_data["id"],
                bibtex=get_bibtex_from_url(reference_data["id"]),
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


@authentication_classes([])
@permission_classes([])
class EdiarumOrganisationViewset(viewsets.ViewSet):
    def list(self, request):
        if not request.query_params.get("q", None):
            return Response(
                {"message": "A query parameter must be provided"}, status=401
            )

        q = request.query_params["q"].lower()
        places = [
            model_to_dict(p)
            for p in Organisation.objects.filter(name__icontains=q)[0:100]
        ]

        places.sort(key=lambda match: match["name"].lower().index(q))
        response = render(request, "ediarum/list.xml", context={"data": places})
        response["content-type"] = "application/xml"
        return response


from apis_ontology.utils import get_factoids_for_unreconciled


class UnreconciledViewSet(viewsets.ViewSet):
    def list(self, request):
        if not request.query_params.get(
            "source", None
        ) and not request.query_params.get("id", None):
            return Response(
                {"message": "A source, id and type must be provided"}, status=401
            )
        factoids = get_factoids_for_unreconciled(
            request.query_params["id"], request.query_params["source"]
        )

        return Response(factoids)

    def create(self, request):

        reconcile_to_object_data = request.data.get("reconcile_to_object", None)
        if not reconcile_to_object_data:
            raise Exception("Reconcile to object data missing")
        reconciled_object_type = model_config[
            reconcile_to_object_data["__object_type__"]
        ]["model_class"]
        reconciled_object = reconciled_object_type.objects.get(
            pk=reconcile_to_object_data["id"]
        )

        reconciliations = request.data.get("reconciliations", None)
        if not reconciliations:
            raise Exception("Reconciliation data missing")

        ur_name = ""
        with transaction.atomic():

            for unreconciled_id, reconciliation in reconciliations.items():
                if not reconciliation.get("isSelected", False):
                    continue

                factoid_id = reconciliation["id"]
                factoid = Factoid.objects.get(pk=factoid_id)

                ur = Unreconciled.objects.get(pk=unreconciled_id)

                ur_name = ur.name

                tt = TempTriple.objects.get(obj__pk=ur.pk)

                tt_new = TempTriple(subj=tt.subj, obj=reconciled_object, prop=tt.prop)

                tt_new.save()

                tt.delete()
                ur.delete()

                factoid_data = get_unpack_factoid(factoid_id)
                factoid.contains_unreconciled = contains_unreconciled(factoid_data)

                factoid.save()

        reconciled_object.reconcile_text = (
            f"{reconciled_object.reconcile_text} {ur_name}"
        )
        return Response({"message": "Success"}, status=200)


class LeaderboardViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response(
            OrderedDict(
                Counter(f.created_by for f in Factoid.objects.all()).most_common()
            )
        )


def extract_statement_types(statement_list):
    statement_types = set()
    for statement in statement_list:
        statement_types.add(statement["__object_type__"])
        nested_statement_keys = {
            k
            for k in statement.keys()
            if k
            in model_config[statement["__object_type__"]]["relations_to_statements"]
        }
        for nested_statement_key in nested_statement_keys:
            statement_types.update(
                extract_statement_types(statement[nested_statement_key])
            )
    return statement_types


class ExampleViewSet(viewsets.ViewSet):
    @staticmethod
    def build_example_list_response(example: Example):
        example_data = json.loads(example.example)
        e = {
            "id": example.pk,
            "name": example_data["example_title"],
            "referenced_types": example_data.get("referenced_types", []),
        }
        return e

    def list(self, request):
        search_tokens = request.query_params.get("q", "").lower().split(" ")
        if not search_tokens:
            return Response({"message", "No search string"}, status=401)

        q = Q()
        for search_token in search_tokens:
            q &= Q(example__icontains=search_token)

        examples = Example.objects.filter(q)

        response = [self.build_example_list_response(example) for example in examples]
        return Response(response)

    def retrieve(self, request, pk=None):

        example = Example.objects.get(pk=pk)
        if example:
            response = json.loads(example.example)
            # response["referenced_types"] = [{"verbose_name": get_entity_class_of_name(t.model)._meta.verbose_name, "model_name": t.model} for t in example.models_referenced.all()]
            return Response(response)

    def update(self, request, pk=None):
        example = Example.objects.get(pk=pk)
        if not example:
            return Response(status=404)

        data = request.data
        statement_types = extract_statement_types(request.data["has_statements"])
        data["referenced_types"] = [
            {
                "verbose_name": get_entity_class_of_name(t)._meta.verbose_name,
                "model_name": t,
            }
            for t in statement_types
        ]

        example.example = json.dumps(data)
        example.save()
        statement_type_contenttypes = {
            get_contenttype_of_class(model_config[st]["model_class"])
            for st in statement_types
        }
        for statement_type_contenttype in statement_type_contenttypes:
            example.models_referenced.add(statement_type_contenttype)
        for existing_statement_type in example.models_referenced.all():
            if existing_statement_type not in statement_type_contenttypes:
                example.models_referenced.remove(existing_statement_type)

        return Response(data={"success": True}, status=200)

    def create(self, request):

        data = request.data
        statement_types = extract_statement_types(request.data["has_statements"])
        data["referenced_types"] = [
            {
                "verbose_name": get_entity_class_of_name(t)._meta.verbose_name,
                "model_name": t,
            }
            for t in statement_types
        ]

        created_example = Example(example=json.dumps(data))
        created_example.save()
        statement_type_contenttypes = {
            get_contenttype_of_class(model_config[st]["model_class"])
            for st in statement_types
        }
        for statement_type_contenttype in statement_type_contenttypes:
            created_example.models_referenced.add(statement_type_contenttype)

        return Response(
            {"id": created_example.pk, **json.loads(created_example.example)},
            status=200,
        )


if __name__ == "__main__":
    with open("apis_ontology/test_edit_factoid_data.json") as f:
        data = json.loads(f.read())
        edit_parse_factoid(data)
