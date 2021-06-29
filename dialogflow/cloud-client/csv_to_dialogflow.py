import json

import pandas as pd

df = pd.read_csv('data/csv2zipdemo.csv')
intent_name_back = None
json_payload_response = dict()
json_payload_user_says = dict()
for index, row in df.iterrows():
    intent_name = row.IntentName
    query = row.Query
    response = row.Response
    if pd.isna(intent_name):
        if not pd.isna(query):
            try:
                json_payload_user_says[intent_name_back].add(query)
            except:
                json_payload_user_says[intent_name_back] = {query}
            print(intent_name_back)
        if not pd.isna(response):
            try:
                json_payload_response[intent_name_back].append(response)
            except:
                json_payload_response[intent_name_back] = [response]
        continue
    else:
        if not pd.isna(query):
            try:
                json_payload_user_says[intent_name].add(query)
            except:
                json_payload_user_says[intent_name] = {query}
            print(intent_name_back)
        if not pd.isna(response):
            try:
                json_payload_response[intent_name].append(response)
            except:
                json_payload_response[intent_name] = [response]
        intent_name_back = intent_name

print(json_payload_response)
print(json_payload_user_says)
for key in json_payload_response:
    payload_template_response = {'name': key, 'auto': True, 'responses': [{'resetContexts': False,
                                                                           'messages': [{'type': 0, 'lang': 'en',
                                                                                         'speech': None
                                                                                         }]
                                                                           }]}
    payload_template_response['responses'][0]['messages'][0]['speech'] = json_payload_response[key]
    print(payload_template_response)
    with open('data/' + key + '.json', 'w') as outfile:
        json.dump(payload_template_response, outfile)


for key in json_payload_user_says:
    queries = json_payload_user_says[key]
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
    with open('data/' + key + '_usersays_en.json', 'w') as outfile:
        json.dump(payload_template_query_list, outfile)
