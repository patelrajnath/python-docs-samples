import json
import re

import pandas as pd

train_df = pd.read_excel("HuaweiAlliance/200908_alliance_train_60_human_paraphrase_answers_v2.xlsx", sheet_name='Sheet1')
valid_df = pd.read_excel("HuaweiAlliance/200908_alliance_val_10_human_paraphrase_answers_v2.xlsx", sheet_name='Sheet1')
test_df = pd.read_excel("HuaweiAlliance/200908_alliance_test_30_human_paraphrase_answers_v2.xlsx", sheet_name='Sheet1')

df = pd.concat([train_df, valid_df])
# df = test_df

intent_query_dict = dict()

for index, row in df.iterrows():
    intent = row.labels
    text = row.question
    try:
        intent_query_dict[intent].append(text)
    except:
        intent_query_dict[intent] = [text]

print(len(intent_query_dict))
# exit()
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
    with open('alliancedata/alliance.agent.' + key_slug + '.json', 'w') as outfile:
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
    with open('alliancedata/alliance.agent.' + key_slug + '_usersays_en.json', 'w') as outfile:
        json.dump(payload_template_query_list, outfile)