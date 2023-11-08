import json

from citeproc.source.json import CiteProcJSON
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import formatter
from citeproc import Citation, CitationItem

bib_style = CitationStylesStyle("harvard1", validate=False)


def create_html_citation_from_csl_data_string(csl_data):
    json_data = json.loads(csl_data)
    bib_source = CiteProcJSON([json_data])

    bibliography = CitationStylesBibliography(bib_style, bib_source, formatter.html)
    
    citation1 = Citation([CitationItem(json_data["id"])])

    bibliography.register(citation1)

    return str(bibliography.bibliography()[0])