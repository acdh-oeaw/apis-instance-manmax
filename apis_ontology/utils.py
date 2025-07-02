import json

from citeproc.source.json import CiteProcJSON
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import formatter
from citeproc import Citation, CitationItem

from apis_ontology.models import  Factoid, Unreconciled, GenericStatement
from apis_core.apis_relations.models import TempTriple
from apis_bibsonomy.models import Reference

bib_style = CitationStylesStyle("harvard1", validate=False)


def create_html_citation_from_csl_data_string(csl_data):
    json_data = json.loads(csl_data)
    bib_source = CiteProcJSON([json_data])

    bibliography = CitationStylesBibliography(bib_style, bib_source, formatter.html)
    
    citation1 = Citation([CitationItem(json_data["id"])])

    bibliography.register(citation1)

    return str(bibliography.bibliography()[0])


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


def direct_statements_until_factoid(ur_id, source_id):
    for subj in generic_statement_subj(ur_id):
        direct_statement = GenericStatement.objects.filter(pk=subj.pk).first()
        if factoid := get_subj_until_factoid(direct_statement.pk):
            ref = Reference.objects.get(object_id=factoid.pk)
            if ref and ref.bibs_url == source_id:
                yield factoid


def get_factoids_for_unreconciled(unreconciled_id, source_id):
  
    unreconcileds_with_same_name = Unreconciled.objects.filter(name=Unreconciled.objects.get(id=unreconciled_id).name)
    

    matching_factoids = {}
    for ur in unreconcileds_with_same_name:
        if factoids := list(direct_statements_until_factoid(ur.pk, source_id)):
            factoid = factoids[0]
            matching_factoids[ur.pk] = {"id": factoid.pk, "name": factoid.name}
        
    return matching_factoids