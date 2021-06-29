import ast
import os

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


dict_file = 'HuaweiWallet/wallet_entities.txt'
ents_dict = dict()
with open(dict_file) as f:
    for line in f:
        if line.strip():
            ent_type, ents = line.split(':')
            if ent_type == "CARD_TYPE" or ent_type == "HUAWEI_DEVICE":
                ents_list = {ent.strip().lower() for ent in ents.split(',')}
                # Append "huawei" to cover the examples like "Huawei Honor 7X" as an entity
                ents_list.update({"huawei " + ent.strip().lower() for ent in ents.split(',')})
            else:
                ents_list = {ent.strip().lower() for ent in ents.split(',')}
            for entity in ents_list:
                ents_dict[ent_type] = ents_list
print(ents_dict)

for idx, key in enumerate(ents_dict):
    print(key)
    create_entity_type(key, 'KIND_LIST')
