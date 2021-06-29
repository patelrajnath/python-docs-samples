import json
import re

import pandas as pd

train_df = pd.read_csv('NLU_V2/200924v3_train_original_split_kfold1_nlu_9960sample_64intents.csv')
test_df = pd.read_csv('NLU_V2/200924v3_test_original_split_kfold1_nlu_1076sample_64intents.csv')

# df = pd.concat([train_df, test_df])
df = train_df

intent_query_dict = dict()

for index, row in df.iterrows():
    intent = row.labels
    text = row.text
    try:
        intent_query_dict[intent].append(text)
    except:
        intent_query_dict[intent] = [text]

print(len(intent_query_dict))

for key in intent_query_dict:
    key_slug = str(key).lower().replace(' ', '_')
    key_slug = re.sub('[^0-9a-zA-Z_]+', '', key_slug)
    key_slug = key_slug[:100]
    print(key_slug, len(key_slug))
    payload_template_response = {'name': key_slug, 'auto': True, 'responses': [{'resetContexts': False,
                                                                           'messages': [{'type': 0, 'lang': 'en',
                                                                                         'speech': None
                                                                                         }]
                                                                           }]}
    payload_template_response['responses'][0]['messages'][0]['speech'] = [key]
    print(payload_template_response)
    with open('nludata/nlu.agent.' + key_slug + '.json', 'w') as outfile:
        json.dump(payload_template_response, outfile)

    queries = intent_query_dict[key]
    payload_template_query_list = list()
    for query in queries:
        payload_template_query = {
            'isTemplate': False,
            'count': 0,
            'updated': 0,
            'data': [{'text': None, 'userDefines': False}]
        }
        payload_template_query['data'][0]['text'] = query
        payload_template_query_list.append(payload_template_query)
    with open('nludata/nlu.agent.' + key_slug + '_usersays_en.json', 'w') as outfile:
        json.dump(payload_template_query_list, outfile)