from pathlib import Path

from lxml import etree


DOCS_PATH = "generated-documentation"

def get_xml_files():
    for file_path in Path(DOCS_PATH, "Statements").iterdir():
        f = file_path.open()
        tree = etree.parse(source=f, parser=etree.XMLParser(ns_clean=True))
        yield tree

def build_doc_objects():
    docs_object = {}
    
    for i, tree in enumerate(get_xml_files()):
        if tree.xpath("/documentation/@for")[0] == "gendering":
            type_identifier, doc = build_doc_object(tree)
            
            docs_object[type_identifier] = doc 

    print(docs_object)



def build_doc_object(tree):
    type_identifier = tree.xpath("/documentation/@for")[0]
    doc_object = {}
    
    doc_object["verbose_name"] = tree.xpath("/documentation/verbose-name")[0].text
    doc_object["verbose_name_plural"] = tree.xpath("/documentation/verbose-name-plural")[0].text
    doc_object["description_short"] = list(tree.xpath("/documentation/description-short")[0].itertext())[0].strip()
    description_long_element = tree.xpath("/documentation/description-long/*[1]")
    doc_object["description_long"] = etree.tounicode(description_long_element[0]).strip() if description_long_element else ""
    
    fields = {}
    field_elements = tree.xpath("/documentation/fields/field")
    
    for fe in field_elements:
        
        field_description_element = fe.xpath("./field-description/*[1]")
        field_description = etree.tounicode(field_description_element[0]) if field_description_element else ""
        
        fields[str(fe.xpath("./@name")[0])] = {
            "verbose_name": fe.xpath("./verbose-name")[0].text,
            "field_description": field_description,
            "input_help": fe.xpath("./input-help")[0].text or ""
        }
    doc_object["fields"] = fields
    
    
    entity_relation_elements = tree.xpath("/documentation/entity-relations/entity-relation")
    entity_relations = {}
    for ere in entity_relation_elements:
        relation_description_element = ere.xpath("./relation-description/*[1]")
        relation_description = etree.tounicode(relation_description_element[0]) if relation_description_element else ""
        
        entity_relations[str(ere.xpath("./@property-name")[0])] = {
            "verbose_name": ere.xpath("./verbose-name")[0].text,
            "relation_description": relation_description,
            "input_help": ere.xpath("./input-help")[0].text or ""
        }
    doc_object["entity_relations"] = entity_relations
    
    statement_relation_elements = tree.xpath("/documentation/statement-relations/statement-relation")
    statement_relations = {}
    for sre in statement_relation_elements:
        relation_description_element = sre.xpath("./relation-description/*[1]")
        relation_description = etree.tounicode(relation_description_element[0]) if relation_description_element else ""
        
        statement_relations[str(sre.xpath("./@property-name")[0])] = {
            "verbose_name": sre.xpath("./verbose-name")[0].text,
            "relation_description": relation_description,
            "input_help": sre.xpath("./input-help")[0].text or ""
        }
        
    doc_object["statement_relations"] = statement_relations
    
    
    return type_identifier, doc_object
    

if __name__ == "__main__":
    build_doc_objects()