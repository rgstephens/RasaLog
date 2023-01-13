import re
import sys

# k logs --selector=app.kubernetes.io/name=rasa -n financial-bot
# k cp -n financial-bot rasa-579d8467fb-6w7q9:rasa_events.json .
# rasa export 
# DEFAULT_LOG_FILE_NAME = "rasa_event.log"
# endpoints.yml
# event_broker:
#   type: file
#   path: rasa_events.json

intent_count = 0
entity_counts = {}
print(f"## processing {sys.argv[1]}\n")
print("| User | Bot | Action/Slots |")
print("|---|---|---|")
with open(sys.argv[1]) as f:
    while True:
        line = f.readline()
        # Received user message 'play wcrb' with intent '{'name': 'listen_station_live', 'confidence': 1.0}' and entities '[{'entity': 'station_callsign', 'start': 5, 'end': 9, 'confidence_entity': 0.9953266382217407, 'value': 'wcrb', 'extractor': 'DIETClassifier'}]'""2022-08-19 12:46:37 DEBUG    rasa.core.processor  - Action 'action_play_station' ended with events '[BotUttered('Here's WCRB.', {""elements"": null, ""quick_replies"": null, ""buttons"": null, ""attachment"": null, ""image"": null, ""custom"": {""payload"": {""nativevoice"": {""play"": {""items"": [{""guideId"": ""s28014"", ""title"": ""99.5 WCRB"", ""subTitle"": ""Classical Radio Boston"", ""imageUri"": ""http://cdn-profiles.tunein.com/s28014/images/logoq.png?t=1""}], ""tag"": ""Station"", ""title"": """"}, ""directive"": ""Play""}}, ""device_location"": ""42.4334675,-71.2080589""}}, {}, 1660913197.0372074), <rasa.shared.core.events.SlotSet object at 0x7f846c20e8b0>, <rasa.shared.core.events.SlotSet object at 0x7f846c20e970>, <rasa.shared.core.events.SlotSet object at 0x7f846c20eb50>]'
        if not line:
            break
        if "Starting a new session" in line:
            # Starting a new session for conversation ID 'lex'
            print("")
            session_id = re.search("Starting a new session for conversation ID '(.+)'", line).group(1)
            print(f"## Session Id: **{session_id}**")
            print("| User | Bot | Actions |")
            print("|---|---|---|")
        if "BotUttered" in line:
            # BotUttered('What is your phone number?',
            bot_uttered = re.search("BotUttered\('(.+)',", line).group(1)
            print(f"| | {bot_uttered} | |")
        if "Starting a new session for conversation ID" in line:
            # Starting a new session for conversation ID '+12063844441'
            id = re.search("Starting a new session for conversation ID '(.+?)'", line).group(1)
            print(f"| | | New session {id} |")
        if "Calling action endpoint to run action" in line:
            # Calling action endpoint to run action 'action_session_start'
            action = re.search("Calling action endpoint to run action '(.+?)'", line).group(1)
            print(f"| | | Calling action {action} |")
        if "Received user message" in line:
            intent_count += 1
            m = re.search("Received user message '(.+?)' with intent", line).group(1)
            intent = re.search("'name': '(.+?)'", line).group(1)
            entities = re.findall("'entity': '(.+?)'", line)
            values = re.findall("'value': '(.+?)'", line)
            print(f"| {m} ({intent}) | | |")
            i = 0
            for e in entities:
#            if entities:
                print(f"| | | {e}=**{values[i]}** |")
                i += 1
                # update entity counters
                if e not in entity_counts.keys():
                    entity_counts[e] = 1
                else:
                    entity_counts[e] += 1
        if "Request next slot " in line:
            # Request next slot 'phone_number'
            slot = re.search("Request next slot '(.+?)'", line).group(1)
            print(f"| | | Request slot **{slot}** |")
        if " with confidence " in line:
            # Predicted next action 'image_form' with confidence 1.00
            action = re.search("Predicted next action '(.+?)' with confidence (.+?)$", line).group(1)
            if action not in ["action_listen"]:
                print(f"| | | Predicted **{action}** |")

            #print(f"user: {m}\n  intent: {intent}")

print(f"\ntotal intents: {intent_count}  \n")
print(f"entity_counts:  ")
for key in entity_counts:
    print('...', key, ' = ', entity_counts[key], '  ')
