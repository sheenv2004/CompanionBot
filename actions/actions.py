# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
# from nrclex import NRCLex
from rasa_sdk.events import SlotSet
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from Weather import weather
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase

## Action method to perform query on the in memory knowlwdge base
class ActionMyKB(ActionQueryKnowledgeBase):
    def __init__(self):
        # load knowledge base with data from the given file
        knowledge_base = InMemoryKnowledgeBase("knowledge_base_data.json")        
        super().__init__(knowledge_base)

    def utter_attribute_value(self,dispatcher: CollectingDispatcher,
        object_name: Text,
        attribute_name: Text,
        attribute_value: Text,
    ):
        """
        Utters a response that informs the user about the attribute value of the
        attribute of interest.
        Args:
            dispatcher: the dispatcher
            object_name: the name of the object
            attribute_name: the name of the attribute
            attribute_value: the value of the attribute
        """
        if attribute_value:
            dispatcher.utter_message(
                # text=f"'{object_name}' has the value '{attribute_value}' for attribute '{attribute_name}'."
                text=f"{attribute_value}."
            )
        else:
            dispatcher.utter_message(
                text=f"Did not find a valid value for attribute '{attribute_name}' for object '{object_name}'."
            )  
## Method to classify positie/negative emotions
class ActionEmotion(Action):

    def name(self) -> Text:
        return "action_emotion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sample_text = str(tracker.latest_message["text"])
        nlp = spacy.load('en_core_web_sm')
        text = sample_text
        nlp.add_pipe("spacytextblob")
        doc = nlp(text)
        emotion_detected="negative" if doc._.blob.polarity< 0.00 else "positive"
        return [SlotSet("emotion",emotion_detected)]

## Method to get weather updates        
class ActionClimate(Action):
    def name(self) -> Text:
        return "action_climate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city=tracker.get_slot("city")
        city="Belfast"
        temp=(weather("city"))
        dispatcher.utter_template("utter_temp",tracker,temp=temp)
        return []        
## Method to submit form
class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        SendEmail(
            tracker.get_slot("email"),
            tracker.get_slot("subject"),
            tracker.get_slot("message")
        )
        dispatcher.utter_message("I have sent the email to {}".format(tracker.get_slot("email")))
        return []
## Method to send email
def SendEmail(toaddr,subject,message):
        fromaddr = "sheenvwork@gmail.com"        
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject
        body = message
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
         # Authentication
        try:
            s.login(fromaddr, "hxrgdkgvdsppoyiq")
            text = msg.as_string()
            s.sendmail(fromaddr, toaddr, text)
        except Exception as exc:
            print("An Error occured while sending email.")
            print(exc)
        finally:
            # terminating the session
            s.quit()





