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
user_msg_time = None
print(f"# Rasa Log Analysis\n")
print(f"- processing `{sys.argv[1]}`\n")
print("## Config\n")
print("| Config | Value |")
print("|---|---|")

# Get config values - have to do this first because LLM model name is not provided until after first conversation starts
line_cnt = 0
with open(sys.argv[1]) as f:
    while True:
        line = f.readline()
        line_cnt += 1
        if "Instantiated NLG " in line:
            # Instantiated NLG to 'TemplatedNaturalLanguageGenerator'
            nlg = re.search("Instantiated NLG to '(.+?)'", line).group(1)
            print(f"| nlg | {nlg} |")
        if "rasa.core.tracker_store  - Connected to" in line:
            # rasa.core.tracker_store  - Connected to InMemoryTrackerStore
            tracker_store = re.search(
                "rasa.core.tracker_store  - Connected to (.*).", line
            ).group(1)
            print(f"| tracker_store | {tracker_store} |")
        if "\"llmfactory.create.embedder" in line:
            # rasa.shared.utils.llm  - {"config": {"_type": "openai", "model": "text-embedding-ada-002"}, "event": "llmfactory.create.embedder", "level": "debug"}
            model = re.search(
                "\{\"_type\": \"openai\", \"model\": \"(.+?)\"", line
            ).group(1)
            print(f"| embedding_model | {model} |")
        if "llmfactory.create.embedder     config={" in line:
            # llmfactory.create.embedder     config={'_type': 'openai', 'model': 'text-embedding-ada-002'}
            model = re.search(
                "config=\{'_type': 'openai', 'model': '(.+?)'", line
            ).group(1)
            print(f"| embedding_model | {model} |")
        if "\"enterprise_search_policy.load" in line:
            # rasa_plus.ml.enterprise_search_policy  - {"config": {"priority": 6, "vector_store": {"type": "faiss", "source": "./docs/txt"}}, "event": "enterprise_search_policy.load", "level": "info"}
            llm = re.search("\"model_name\": \"(.+?)\"", line)
            if llm:
                llm = llm.group(1)
            else:
                llm = "gpt-3.5-turbo"
            print(f"| entsearch.llm | {llm} |")
            vector_store = re.search("\"type\": \"(.+?)\",", line).group(1)
            print(f"| vector_store | {vector_store} |")
        if "enterprise_search_policy.load  config=" in line:
            # enterprise_search_policy.load  config={'priority': 6, 'vector_store': {'type': 'faiss', 'source': './docs'}}
            # enterprise_search_policy.load  config={'priority': 6, 'vector_store': {'type': 'faiss', 'source': './docs'}, 'llm': {'model_name': 'gpt-4'}}
            llm = re.search("'model_name': '(.+?)'", line)
            if llm:
                llm = llm.group(1)
            else:
                llm = "gpt-3.5-turbo"
            print(f"| entsearch.llm | {llm} |")
            vector_store = re.search("'type': '(.+?)',", line).group(1)
            print(f"| vector_store | {vector_store} |")
        if "\"llmfactory.create.llm" in line:
            time = get_timestamp(line)
            # rasa.shared.utils.llm  - {"config": {"_type": "openai", "request_timeout": 5, "temperature": 0.0, "model_name": "gpt-3.5-turbo"}, "event": "llmfactory.create.llm", "level": "debug"}
            llm_type = re.search("\"type\": \"(.+?)\",", line)
            if llm_type:
                llm_type = llm_type.group(1)
            else:
                llm_type = re.search("\"_type\": \"(.+?)\",", line)
                if llm_type:
                    llm_type = llm_type.group(1)
            model_name = re.search("\"model_name\": \"(.+?)\"", line).group(1)
            print(f"| llm_type | {llm_type} |")
            print(f"| llm_model_name | {model_name} |")
            break
        if "llmfactory.create.llm          config" in line:
            time = get_timestamp(line)
            # rasa.engine.graph  - {"config": {"_type": "openai", "request_timeout": 5, "temperature": 0.0, "model_name": "gpt-3.5-turbo"}, "event": "llmfactory.create.llm", "level": "debug"}
            # llmfactory.create.llm          config={'_type': 'openai', 'request_timeout': 7, 'temperature': 0.0, 'model_name': 'gpt-4', 'max_tokens': 256}
            # rasa.shared.utils.llm  - [debug    ] llmfactory.create.llm          config={'_type': 'openai', 'request_timeout': 5, 'temperature': 0.0, 'model_name': 'gpt-4'}
            llm_type = re.search("'type': '(.+?)',", line)
            if llm_type:
                llm_type = llm_type.group(1)
            else:
                llm_type = re.search("'_type': '(.+?)',", line)
                if llm_type:
                    llm_type = llm_type.group(1)
            model_name = re.search("'model_name': '(.+?)'", line).group(1)
            print(f"| llm_type | {llm_type} |")
            print(f"| llm_model_name | {model_name} |")
            break
        if line_cnt > 200:
            break

print("\n## Sessions\n")
print("| Time | User | Bot | Action | Slot\/Flow |")
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
                session_id = re.search(
                    "Starting a new session for conversation ID '(.+)'", line
                ).group(1)
            print(f"## Session Id: **{session_id}**\n")
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
                bot_uttered = f"{bot_uttered[0:40]}... ({len(bot_uttered)}b)"
            print(f"| {time} | | {bot_uttered} | {elapsed_time_msg} | |")
        if "Starting a new session for conversation ID" in line:
            # Starting a new session for conversation ID '+12063844441'
            id = re.search(
                "Starting a new session for conversation ID '(.+?)'", line
            ).group(1)
            print(f"| {time} | | | New session {id} | |")
        if "Calling action endpoint to run action" in line:
            # Calling action endpoint to run action 'action_session_start'
            action = re.search(
                "Calling action endpoint to run action '(.+?)'", line
            ).group(1)
            print(f"| {time} | | | **{action}** | |")
        if "[UserMessage(text" in line:
            # [UserMessage(text: who is the vice president of enrollment, sender_id: d9f23a29f6de4e15a3af15b91075f14a)]
            user_msg_time = time
            intent_count += 1
            m = re.search("\[UserMessage\(text: (.*), sender_id", line).group(1)
            print(f"| {time} | {m} | | | |")
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
            prediction_policy = re.search(
                "Predicted next action using (.*).", line
            ).group(1)
        if " with confidence " in line:
            # Predicted next action 'image_form' with confidence 1.00
            # Predicted next action 'action_listen' with confidence 1.00.
            results = re.search(
                "Predicted next action '(.+?)' with confidence (.*).$", line
            )
            action = results.group(1)
            conf = results.group(2)
            # if action not in ["action_listen"]:
            print(f"| {time} | | | {action}/{prediction_policy} ({conf}) | |")
        if " flow.step.run.flow_end " in line:
            # flow.step.run.flow_end         flow_id=event_signup step_id=END
            flow_id = re.search("flow_id=(.*) ", line).group(1)
            print(f"| {time} | | |  | flow_end/{flow_id} |")
        if " flow.execution.loop " in line:
            # flow.execution.loop            flow_id=pattern_continue_interrupted previous_step_id=START
            flow_id = re.search("flow_id=(.*) ", line).group(1)
            print(f"| {time} | | |  | flow_start/{flow_id} |")
            # WARNING  langchain.llms.base  - Retrying langchain.llms.openai.completion_with_retry.<locals>._completion_with_retry in 4.0 seconds as it raised Timeout: Request timed out: HTTPSConnectionPool(host='api.openai.com', port=443): Read timed out. (read timeout=5).
        if " ERROR " in line:
            if "Request timed out" in line and "nlg.llm.error" in line:
                # flow.execution.loop            flow_id=pattern_continue_interrupted previous_step_id=START
                # ERROR    rasa_plus.ml.enterprise_search_policy  - [error    ] nlg.llm.error                  error=Timeout(message="Request timed out
                print(f"| {time} | | |  | **ERROR: NLG TIMEOUT** |")
            elif "Request timed out" in line:
                # asyncio  - Task was destroyed but it is pending!
                # ERROR    rasa_plus.ml.enterprise_search_policy  - {"error": "Timeout(message=\"Request timed out: HTTPSConnectionPool(host='api.openai.com', port=443): Read timed out. (read timeout=5)\", http_status=None, request_id=None)", "event": "nlg.llm.error", "level": "error"}
                print(f"| {time} | | |  | **ERROR TIMEOUT** |")
            elif "asyncio" in line and "Task was destroyed but it is pending!" in line:
                # asyncio  - Task was destroyed but it is pending!
                print(f"| {time} | | |  | **ERROR asyncio** |")
            else:
                error_msg = re.search("ERROR    (.*)$", line).group(1)
                print(f"| {time} | | |  | **ERROR {error_msg}** |")

            # print(f"user: {m}\n  intent: {intent}")

print(f"\ntotal intents: {intent_count}  \n")
print(f"entity_counts:  ")
for key in entity_counts:
    print("...", key, " = ", entity_counts[key], "  ")
