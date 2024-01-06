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

def get_timestamp(line: str) -> str:
    """Extract timestamp from log line."""
    # 2021-08-19 12:46:37 DEBUG    rasa.core.processor  - Received user message 'play wcrb' with intent '{'name': 'listen_station_live', 'confidence': 1.0}' and entities '[{'entity': 'station_callsign', 'start': 5, 'end': 9, 'confidence_entity': 0.9953266382217407, 'value': 'wcrb', 'extractor': 'DIETClassifier'}]'
    # 2021-08-19 12:47:37 INFO    rasa.core.lock_store  - Deleted lock for conversation 'lex' 
    time = re.search("\d{2}:\d{2}:\d{2}", line)
    if time:
        time = time.group(0)
    return time

intent_count = 0
entity_counts = {}
print(f"# Rasa Log Analysis\n")
print(f"- processing `{sys.argv[1]}`\n")
print("| Time | User | Bot | Action | Slot |")
print("|---:|---|---|---|---|")
with open(sys.argv[1]) as f:
    while True:
        line = f.readline()
        # Received user message 'play wcrb' with intent '{'name': 'listen_station_live', 'confidence': 1.0}' and entities '[{'entity': 'station_callsign', 'start': 5, 'end': 9, 'confidence_entity': 0.9953266382217407, 'value': 'wcrb', 'extractor': 'DIETClassifier'}]'""2022-08-19 12:46:37 DEBUG    rasa.core.processor  - Action 'action_play_station' ended with events '[BotUttered('Here's WCRB.', {""elements"": null, ""quick_replies"": null, ""buttons"": null, ""attachment"": null, ""image"": null, ""custom"": {""payload"": {""nativevoice"": {""play"": {""items"": [{""guideId"": ""s28014"", ""title"": ""99.5 WCRB"", ""subTitle"": ""Classical Radio Boston"", ""imageUri"": ""http://cdn-profiles.tunein.com/s28014/images/logoq.png?t=1""}], ""tag"": ""Station"", ""title"": """"}, ""directive"": ""Play""}}, ""device_location"": ""42.4334675,-71.2080589""}}, {}, 1660913197.0372074), <rasa.shared.core.events.SlotSet object at 0x7f846c20e8b0>, <rasa.shared.core.events.SlotSet object at 0x7f846c20e970>, <rasa.shared.core.events.SlotSet object at 0x7f846c20eb50>]'
        if not line:
            break
        time = get_timestamp(line)
        if "Starting a new session" in line:
            # Starting a new session for conversation ID 'lex'
            # Starting a new session for conversation ID '{"workspaceId":"7b1af13b-0c42-40d3-9f0d-0e105f59a0f7","visitorId":"640eb43e43b804765ec7859f","conversationId":"640eb44f43b804765ec785a4"}'.
            print("")
            conversation_id = re.search('"conversationId":"(.+)"', line)
            if conversation_id:
                session_id = conversation_id.group(1)
            else:
                session_id = None
            # session_id = re.search('"conversationId":"(.+)"', line).group(1)
            if not session_id:
                session_id = re.search("Starting a new session for conversation ID '(.+)'", line).group(1)
            print(f"## Session Id: **{session_id}**")
            print("| Time | User | Bot | Actions | Slot |")
            print("|---:|---|---|---|---|")
        if "BotUttered" in line:
            if time and user_msg_time:
                elapsed_time = float(time[6:8]) - float(user_msg_time[6:8])
                elapsed_time_msg = f"(Latency **{elapsed_time} secs**)"
            else:
                elapsed_time_msg = ""
            user_msg_time = None
            # BotUttered('What is your phone number?',
            # Action 'form_contact_us' ended with events '[SlotSet(key: requested_slot, value: form_contact_us_last_name), BotUttered('None', {"elements": null, "quick_replies": null, "buttons": null, "attachment": null, "image": null, "custom": {"field": {"custom_provider": null, "custom_type": null, "index": 1, "key": "contact_us_last_name", "options": null, "question": "And your last name?", "required": true, "title": "Last Name", "type": "LAST_NAME"}, "form": {"fields": {"form_contact_us_email": "None", "form_contact_us_first_name": "dfhgfhfgh", "form_contact_us_last_name": "None", "form_contact_us_phone_number": "None"}, "fields_count": 4, "id": "contact_us", "title": "contact_us"}, "id": "449838", "type": "FORM_CS"}}, {"utter_action": "utter_ask_form_contact_us_form_contact_us_last_name"}, 1678691402.3533535)]'
            bot_uttered = re.search("BotUttered\('(.+)',", line).group(1)
            if len(bot_uttered) > 10:
                bot_uttered = f"{bot_uttered[0:10]}... ({len(bot_uttered)} chars)"
            print(f"| {time} | | | BotUttered: {bot_uttered}, {elapsed_time_msg} | |")
        if "Starting a new session for conversation ID" in line:
            # Starting a new session for conversation ID '+12063844441'
            id = re.search("Starting a new session for conversation ID '(.+?)'", line).group(1)
            print(f"| {time} | | | New session {id} | |")
        if "Calling action endpoint to run action" in line:
            # Calling action endpoint to run action 'action_session_start'
            action = re.search("Calling action endpoint to run action '(.+?)'", line).group(1)
            print(f"| {time} | | | Calling action {action} | |")
        if "Received user message" in line:
            user_msg_time = time
            intent_count += 1
            m = re.search("Received user message '(.*)' with intent", line).group(1)
            intent = re.search("'name': '(.+?)'", line).group(1)
            f1 = re.search("'confidence': (.+?)}", line).group(1)[0:4]
            entities = re.findall("'entity': '(.+?)'", line)
            values = re.findall("'value': '(.+?)'", line)
            print(f"| {time} | {m} ({intent}={f1}) | | | |")
            i = 0
            for e in entities:
#            if entities:
                print(f"| | | {e}=**{values[i]}** | |")
                i += 1
                # update entity counters
                if e not in entity_counts.keys():
                    entity_counts[e] = 1
                else:
                    entity_counts[e] += 1
        if "Validating extracted slots" in line:
            # Validating extracted slots: form_restaurant_booking
            slot_details = re.search("Validating extracted slots: (.*)", line)
            if slot_details:
                slot = slot_details.group(1)
                print(f"| {time} | | | | Extracted slot **{slot}** |")
        if "Request next slot " in line:
            # Request next slot 'phone_number'
            slot = re.search("Request next slot '(.+?)'", line).group(1)
            print(f"| {time} | | | | Request slot **{slot}** |")
        if "Predicted next action using " in line:
            # Predicted next action using RulePolicy
            # Predicted next action using RulePolicy.
            prediction_policy = re.search("Predicted next action using (.*).", line).group(1)
        if " with confidence " in line:
            # Predicted next action 'image_form' with confidence 1.00
            # Predicted next action 'action_listen' with confidence 1.00.
            results = re.search("Predicted next action '(.+?)' with confidence (.*).$", line)
            action = results.group(1)
            conf = results.group(2)
            # if action not in ["action_listen"]:
            print(f"| {time} | | | Predicted **{action}** using **{prediction_policy}** with conf **{conf}** | |")

            #print(f"user: {m}\n  intent: {intent}")

print(f"\ntotal intents: {intent_count}  \n")
print(f"entity_counts:  ")
for key in entity_counts:
    print('...', key, ' = ', entity_counts[key], '  ')
