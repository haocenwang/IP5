from typing import Dict, Text, Any, List, Union

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.forms import FormAction
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import dateutil.parser
import pandas as pd


class ValidateRoomForm(FormValidationAction):
    """Example of a form validation action."""

    def name(self) -> Text:
        return "validate_room_form"

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False
    
    def validate_num_persons(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate num_people value."""

        if self.is_int(value) and int(value) > 0:
            return {"num_persons": value}
        else:
            dispatcher.utter_message(template="utter_wrong_num_persons")
            # validation failed, set slot to None
            return {"num_persons": None}
    
    def validate_from_date(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
         """Validate from_date value."""
         date = tracker.get_slot('from_date')
         date_temp = date[0:10]
         time_temp = date[11:19]
         if time_temp == "00:00:00":
            dispatcher.utter_message(template="utter_ask_from_time")
            return {"from_date":date_temp}
         else:
            return {"from_date":date}
    
    def validate_from_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate from_date value."""
        time_slot = tracker.get_slot('from_time')
        get_time = time_slot[11:19]
        
        return {"from_time":get_time}

        
        