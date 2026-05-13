from django.core.management.base import BaseCommand, CommandError

from apis_ontology.models import GenericStatement, Unreconciled


import json


from apis_ontology.models import  Factoid, Unreconciled, GenericStatement
from apis_core.apis_relations.models import TempTriple
from apis_bibsonomy.models import Reference


def get_subj_until_factoid(pk):
    tt = TempTriple.objects.filter(obj=pk).first()
    if not tt:
        return None
    if isinstance(tt.subj, Factoid):
       
        return tt.subj
    return get_subj_until_factoid(tt.subj.pk)





def generic_statement_subj(ur_id):
    unreconciled = Unreconciled.objects.filter(pk=ur_id).first()
    for item in unreconciled.triple_set_from_obj.iterator():
        yield item.subj


def direct_statements_until_factoid(ur_id):
    for subj in generic_statement_subj(ur_id):
        direct_statement = GenericStatement.objects.filter(pk=subj.pk).first()
        if factoid := get_subj_until_factoid(direct_statement.pk):
            return factoid

class Command(BaseCommand):
    help = (
        "Add Certainty Values to Statements"
    )

    def handle(self, *args, **options):
        for ur in Unreconciled.objects.all():
            try:
                factoid = direct_statements_until_factoid(ur)
                print("Adding", factoid.pk, "as factoid for", ur.pk)
                ur.is_in_factoid = factoid
                ur.save()
            except Exception as e:
                print("Error:", e)
            
            
       