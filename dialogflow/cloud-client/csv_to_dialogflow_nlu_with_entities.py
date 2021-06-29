import json
import pickle
import re
import uuid

intent_query_dict = dict()
with open ("NLU_V2/train-nlu-v3_with-labels", 'rb') as fp:
    TRAIN_DATA = pickle.load(fp)

for example in TRAIN_DATA:
    text, intent, entities = example
    try:
        intent_query_dict[intent].append((text, entities))
    except:
        intent_query_dict[intent] = [(text, entities)]



entity_value_list = dict()
for key in intent_query_dict:
    # key_slug = key.lower().replace(' ', '_')
    # key_slug = re.sub('[^0-9a-zA-Z_]+', '', key)
    key_slug = str(key)[:100]
    payload_template_response = {'name': key_slug, 'auto': True,
                                 'responses': [{'resetContexts': False,
                                                "parameters": [],
                                                'messages': [{'type': 0, 'lang': 'en', 'speech': []}]
                                                }]
                                 }
    payload_template_response['responses'][0]['messages'][0]['speech'] = [key]
    queries = intent_query_dict[key]
    payload_template_query_list = list()
    params_list = set()
    for q in queries:
        query, entity = q

        payload_template_query = {
            'isTemplate': False,
            'count': 0,
            'updated': 0,
            'data': []
        }

        ents = entity["entities"]
        ents_dict = dict()
        for ent in ents:
            start, end, ent_type = ent
            ents_dict[start] = ent
        slice_start = 0
        query_len = len(query)
        for key in sorted(ents_dict):
            template_ent = {
                "text": None,
                "meta": None,
                "alias": None,
                "userDefined": True
            }

            template_text = {
                'text': None,
                'userDefines': False
            }

            start, end, ent_type = ents_dict[key]
            if ent_type not in params_list:
                param_template = {
                    "name": ent_type,
                    "dataType": "@" + ent_type,
                    "value": "$" + ent_type,
                }
                params_list.add(ent_type)
                payload_template_response['responses'][0]['parameters'].append(param_template)

            if start == 0:
                entity = query[start:end]
                # print('entity:'.format(entity))
                template_ent['text'] = entity
                template_ent['meta'] = '@' + ent_type
                template_ent['alias'] = ent_type
                payload_template_query['data'].append(template_ent)
                try:
                    entity_value_list[ent_type].add(entity)
                except:
                    entity_value_list[ent_type] = {entity}
            else:
                text = query[slice_start:start]
                template_text['text'] = text
                payload_template_query['data'].append(template_text)

                entity = query[start:end]
                template_ent['text'] = entity
                template_ent['meta'] = '@' + ent_type
                template_ent['alias'] = ent_type
                payload_template_query['data'].append(template_ent)
                try:
                    entity_value_list[ent_type].add(entity)
                except:
                    entity_value_list[ent_type] = {entity}

                # print('text:{}'.format(text))
                # print('entity:{}'.format(entity))
            slice_start = end
        print(query_len, slice_start)

        template_text = {
            'text': None,
            'userDefines': False
        }
        if slice_start < query_len:
            text = query[slice_start:]
            template_text['text'] = text
            payload_template_query['data'].append(template_text)
            # print("text:{}".format(text))

        payload_template_query_list.append(payload_template_query)

    # print(payload_template_response)
    with open('nludata_with_entities/intents/nlu_with_entities.agent.' + key_slug + '.json', 'w') as outfile:
        json.dump(payload_template_response, outfile)

    with open('nludata_with_entities/intents/nlu_with_entities.agent.' + key_slug + '_usersays_en.json', 'w') as outfile:
        json.dump(payload_template_query_list, outfile)


for key in entity_value_list:
    # print(payload_template_response)
    ent_type_template = {
        "id": str(uuid.uuid4()),
        "name": key,
        "isOverridable": True,
        "isEnum": False,
        "isRegexp": False,
        "automatedExpansion": False,
        "allowFuzzyExtraction": False
    }

    with open('nludata_with_entities/entities/' + key + '.json', 'w') as outfile:
        json.dump(ent_type_template, outfile)

    entity_strings = entity_value_list[key]
    entity_json_list = []
    for entity in entity_strings:
        entity_value_template = {
            "value": entity,
            "synonyms": [entity]
        }
        entity_json_list.append(entity_value_template)
    with open('nludata_with_entities/entities/' + key + '_entries_en.json', 'w') as outfile:
        json.dump(entity_json_list, outfile)
