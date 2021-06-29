#!/usr/bin/env python

# Copyright 2017 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""DialogFlow API Detect Intent Python sample with text inputs.

Examples:
  python detect_intent_texts.py -h
  python detect_intent_texts.py --project-id PROJECT_ID \
  --session-id SESSION_ID \
  "hello" "book a meeting room" "Mountain View"
  python detect_intent_texts.py --project-id PROJECT_ID \
  --session-id SESSION_ID \
  "tomorrow" "10 AM" "2 hours" "10 people" "A" "yes"
"""

import argparse
import json
import os
import pickle
import re
import uuid
from re import finditer
from time import sleep

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Chatbot-012b76b52f9f.json"


# [START dialogflow_detect_intent_text]
def detect_intent_texts(project_id, session_id, language_code):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()
    session_id = '1234567'
    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))

    import pandas as pd

    with open('HuaweiAlliance/test-alliance_with_labels', 'rb') as fp:
        TEST_DATA = pickle.load(fp)

    correct_count = 0
    total_count = 0
    predictions = []
    true_labels = []
    predicted_entities = dict()
    true_labels_for_testing = list()
    ne_class_list = set()
    sample_count = 10000
    with open('log.txt', 'w') as log:
        for index, example in enumerate(TEST_DATA):
            text, label, ent_dict = example
            if len(text) >= 256:
                continue
            entities = ent_dict
            ent_labels = dict()
            for ent in entities:
                start, stop, ent_type = ent
                ent_type = ent_type.replace('_', '')
                ne_class_list.add(ent_type)
                if ent_type in ent_labels:
                    ent_labels[ent_type].append((start, stop))
                else:
                    ent_labels[ent_type] = [(start, stop)]
            true_labels_for_testing.append(ent_labels)
            # print(true_labels_for_testing)
            true_labels.append(label)
            intent = str(label)
            total_count += 1
            text_input = dialogflow.types.TextInput(
                text=text, language_code=language_code)

            query_input = dialogflow.types.QueryInput(text=text_input)

            response = session_client.detect_intent(
                session=session, query_input=query_input)

            print('=' * 20)
            # print(response)
            intent_predicted = response.query_result.fulfillment_text
            if intent_predicted.strip():
                predictions.append(int(intent_predicted))
            else:
                predictions.append(-1)

            if intent == intent_predicted:
                correct_count += 1
            else:
                log.write('True:' + intent + '\n')
                log.write('Predicted:' + intent_predicted + '\n\n')
            parameters = response.query_result.parameters.fields
            # print(parameters)
            entity_dict = dict()
            for ent in parameters:
                for item in parameters[ent].list_value:
                    try:
                        entity_text_len = len(item)
                        entity_dict[entity_text_len].add((item, ent))
                    except:
                        entity_dict[entity_text_len] = {(item, ent)}

            predicted_entities[index] = entity_dict

            print('Query text: {}'.format(response.query_result.query_text))
            # print('Query Entities: {0}'.format(parameters))
            print('Detected intent: {} (confidence: {})\n'.format(
                response.query_result.intent.display_name,
                response.query_result.intent_detection_confidence))
            print('Fulfillment text: {}\n'.format(
                response.query_result.fulfillment_text))
            # sleep(0.25)
            print("Total count:{}, Correct count:{}".format(total_count, correct_count))
            if index == sample_count:
                break
    print("Accuracy:{}".format(correct_count/total_count))
    pred_df = pd.Series(predictions)
    true_df = pd.Series(true_labels)
    pred_df.reset_index(drop=True, inplace=True)
    true_df.reset_index(drop=True, inplace=True)
    acc = accuracy_score(true_df, pred_df)
    print("Accuracy sklearn:{}".format(acc))

    print(f1_score(true_df, pred_df, average='weighted'))
    print(precision_score(true_df, pred_df, average='weighted'))
    print(recall_score(true_df, pred_df, average='weighted'))

    test_segments = list()
    for idx, example in enumerate(TEST_DATA):
        raw_text, _, _ = example
        if len(raw_text) >= 256:
            continue
        entity_dict = predicted_entities[idx]
        entities_list = list()
        result = []
        for index in sorted(entity_dict, reverse=True):
            for ent, key in entity_dict[index]:
                # print(ent, key)
                for match in finditer(re.escape(ent), raw_text):
                    is_new = False
                    start, stop = match.span()
                    for low, high in result:
                        if (low <= start <= high) or (low <= stop <= high):
                            break
                    else:
                        is_new = True
                        result.append((start, stop))
                    if is_new:
                        entities_list.append((start, stop, key))
        # For evaluation
        test_segments.append((raw_text, entities_list))
        if idx == sample_count:
            break

    results_of_prediction = list()
    for example in test_segments:
        _, entities = example
        ent_labels = dict()
        for ent in entities:
            start, stop, ent_type = ent
            ent_type = ent_type.replace('_', '')
            if ent_type in ent_labels:
                ent_labels[ent_type].append((start, stop))
            else:
                ent_labels[ent_type] = [(start, stop)]
        results_of_prediction.append(ent_labels)
    print(len(results_of_prediction), len(true_labels_for_testing))
    from eval.quality import calculate_prediction_quality

    f1, precision, recall, results = \
        calculate_prediction_quality(true_labels_for_testing,
                                     results_of_prediction,
                                     tuple(ne_class_list))
    print(f1, precision, recall, results)
# [END dialogflow_detect_intent_text]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--project-id',
        help='Project/agent id.  Required.',
        required=True)
    parser.add_argument(
        '--session-id',
        help='Identifier of the DetectIntent session. '
        'Defaults to a random UUID.',
        default=str(uuid.uuid4()))
    parser.add_argument(
        '--language-code',
        help='Language code of the query. Defaults to "en-US".',
        default='en-US')
    args = parser.parse_args()

    detect_intent_texts(
        args.project_id, args.session_id, args.language_code)
