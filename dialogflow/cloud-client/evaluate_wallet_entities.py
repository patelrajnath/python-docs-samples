import ast

with open('dialogflow_wallet-test_entities.txt','r') as f:
   ents_dict = ast.literal_eval(f.read())

for ent in ents_dict:
    print(ent)
