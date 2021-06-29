import ast
import os
from time import sleep

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Chatbot-012b76b52f9f.json"
project_id='chatbot-288308'


def create_entity_type(display_name, kind):
    """Create an entity type with the given display name."""
    import dialogflow_v2 as dialogflow
    entity_types_client = dialogflow.EntityTypesClient()

    parent = entity_types_client.project_agent_path(project_id)
    entity_type = dialogflow.types.EntityType(
        display_name=display_name, kind=kind)

    response = entity_types_client.create_entity_type(parent, entity_type)

    print('Entity type created: \n{}'.format(response))


dict_file = 'NLU_V2/nlu_entities.txt'
with open(dict_file,'r') as f:
   ents_dict = ast.literal_eval(f.read())
print(ents_dict)

for idx, key in enumerate(ents_dict):
    print(key)
    try:
        create_entity_type(key, 'KIND_LIST')
        sleep(0.10)
    except:
        pass
