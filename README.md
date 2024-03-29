# Rasa Log Formatting Script

This is a script to help review [Rasa](https://rasa.com) open source debug logs. It takes a Rasa logfile as input and writes a markdown table to stdout.

The script has been updated to support Rasa Pro [flows](https://rasa.com/docs/rasa-pro/concepts/flows).

```sh
python rasalog.py rasa.log > rasalog.md
```

Here's an example of the results:

## processing rasa.log

## Session Id: **ecdb5829dad64856a06a759ce89e38c8**

| User | Bot | Actions |
|---|---|---|
| | | New session ecdb5829dad64856a06a759ce89e38c8 |
| hi (greet) | | |
| | | Predicted **utter_greet_joke** |
| | Hi, welcome to the Jokebot | |
| | | Predicted **utter_help_joke** |
| | You can ask for Geek jokes, Corny jokes. Also, Kanye, Ron Swanson, Creed, Breaking Bad, Inspiring or Trump quotes. | |
| swanson (out_of_scope) | | |
| | | Predicted **utter_out_of_scope** |
| | Sorry, I'm not sure how to respond to that. Type "help" for assistance. | |
| ron swanson (ron_quote) | | |
| | | Predicted **action_ron** |
| | | Calling action action_ron |
| | There are only three ways to motivate people: money, fear, and hunger. - Ron Swanson | |
| geek quote (geek_joke) | | |
| | | Predicted **action_geek** |
| | | Calling action action_geek |
| | On two occasions I have been asked, ‘Pray, Mr. Babbage, if you put into the machine wrong figures, will the right answers come out?’ I am not able rightly to apprehend the kind of confusion of ideas that could provoke such a question.” - [Charles Babbage](http://quotes.stormconsultancy.co.uk/quotes/8) | |
| geek (geek_joke) | | |
| | | Predicted **action_geek** |
| | | Calling action action_geek |
| | I don’t care if it works on your machine! We are not shipping your machine! - [Ovidiu Platon](http://quotes.stormconsultancy.co.uk/quotes/11) | |
| versin (version) | | |
| | | Predicted **utter_version** |
| | Oct 15, 2022 | |
| | | Predicted **action_version** |
| | | Calling action action_version |

total intents: 7  

entity_counts:  
