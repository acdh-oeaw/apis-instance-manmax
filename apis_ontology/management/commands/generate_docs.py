from django.core.management.base import BaseCommand, CommandError
from apis_core.apis_relations.models import Property
from apis_ontology.models import construct_properties

import pathlib

EXCLUDED_FIELDS = {"id",
    "name",
    "internal_notes",
    "start_date",
    "start_start_date",
    "end_start_date",
    "end_date",
    "start_end_date",
    "end_end_date",
    "start_date_written",
    "end_date_written",
    "notes",
    "head_statement",
    "certainty_values",
    "certainty",
}

def build_allowed_types(field_config):
    from apis_ontology.model_config import model_config as model_config_objects
    
    if not field_config.get("allowed_types", None):
        return ""
    
    template = """<allowed-types>
                <!-- For reference only: is not imported and has no effect -->"""
    
    for allowed_type in field_config["allowed_types"]:
        template += f'''
                <allowed-type name="{allowed_type}">{model_config_objects[allowed_type]["verbose_name"]}</allowed-type>'''
        
    template += """
            </allowed-types>"""    
    return template
        
        
        
def build_entity_relations_definitions(model_config):
    template = "<entity-relations>"
    for field_name, field_config in model_config["relations_to_entities"].items():
        if field_name in EXCLUDED_FIELDS:
            continue
        
        template += (
    f'''
        <entity-relation property-name="{field_name}">
            <verbose-name>{field_name.replace("_", " ")}</verbose-name>
            <relation-description><!-- Appears under verbose name. May contain HTML as well-formed fragments. --></relation-description>
            <input-help><!-- Appears under the input --></input-help>
            {build_allowed_types(field_config)}
        </entity-relation >
    '''
    )
    template += "</entity-relations>"
    return template


def build_statement_relations_definitions(model_config):
    template = "<statement-relations>"
    for field_name, field_config in model_config["relations_to_statements"].items():
        if field_name in EXCLUDED_FIELDS:
            continue
        
        template += (
    f'''
        <statement-relation property-name="{field_name}">
            <verbose-name>{field_name.replace("_", " ")}</verbose-name>
            <relation-description><!-- Appears under verbose name. May contain HTML as well-formed fragments. --></relation-description>
            <input-help><!-- Appears under the input --></input-help>
            {build_allowed_types(field_config)}
        </statement-relation >
    '''
    )
    template += "</statement-relations>"
    return template



def build_field_definitions(model_config):
    template = "<fields>"
    for field_name, field_config in model_config["fields"].items():
        if field_name in EXCLUDED_FIELDS:
            continue
        
        template += (
    f'''
        <field name="{field_name}">
            <verbose-name>{field_config["verbose_name"]}</verbose-name>
            <field-description><!-- Appears under verbose name. May contain HTML *one* well-formed fragment. --></field-description>
            <input-help><!-- Appears under the input field -->{field_config["help_text"]}</input-help>
        </field>
    '''
    )
    template += "</fields>"
    return template

def build_documentation_file(model_name_lowercase, model_config):
    template = (
f'''
<!-- {model_config["verbose_name"]} Documentation 

- Do *not* change XML @property values as these are used to connect docs back to model types
- Use only HTML where it is suggested in a comment!
- Make sure HTML is well-formed. Wrap everything in a <div>! 

-->
<documentation for="{model_name_lowercase}">
    <verbose-name>{model_config["verbose_name"]}</verbose-name>
    <verbose-name-plural>{model_config["verbose_name_plural"]}</verbose-name-plural>
    <description-short>
        <!-- Appears in documentation pop-up -->
        {model_config["description"]}
    </description-short>
    <description-long>
        <!-- To be used in main documentation page. May contain HTML *one* well-formed fragment. -->
    </description-long>
    {build_field_definitions(model_config)}
    {build_entity_relations_definitions(model_config)}
    {build_statement_relations_definitions(model_config)}
</documentation>
''')
    return template





class Command(BaseCommand):
    help = (
        "Generate documentation"
    )

    def handle(self, *args, **options):
        from apis_ontology.model_config import model_config
        
        print(options)
        
        pathlib.Path("./generated-documentation", "Entities").mkdir(exist_ok=True)
        pathlib.Path("./generated-documentation", "Statements").mkdir(exist_ok=True)
        
        for model_name, model_config in model_config.items():
            doc = build_documentation_file(model_name, model_config)
            print("Building doc for", model_config["entity_type"], model_config["model_class"].__name__)
            
            
            path = pathlib.Path("./generated-documentation", model_config["entity_type"], f'{model_config["model_class"].__name__}.xml')
            if not path.is_file():
                print("Writing file...")
                path.absolute().write_text(doc)
            else:
                print("Already exists")
            
            
        