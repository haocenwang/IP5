from typing import Dict, Text, Any, List, Union

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.forms import FormAction
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import dateutil.parser
import csv
import datetime

class ValidateRoomForm(FormValidationAction):
    """Example of a form validation action."""

    def name(self) -> Text:
        return "validate_room_form"

    @staticmethod
    def room_type_db() -> List[Text]:
        """Database of supported cuisines."""

        return [
            "window",
            "computer",
            "screen",
        ]

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_room_type(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate room_type value."""

        if value.lower() in self.room_type_db():
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"room_type": value}
        else:
            dispatcher.utter_message(template="utter_wrong_room_type")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"cuisine": None}


    
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
         
         return {"from_date":date_temp}
    
    def validate_from_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
         """Validate from_date value."""
         date = tracker.get_slot('from_time')
         date_temp = date[0:10]
         time_temp = date[11:19]

         if time_temp == "00:00:00":
            return {"from_time":None}
         else:
            return {"from_date":date_temp,"from_time":time_temp}




    class CheckRoom(Action):

        def name(self) -> Text:
            return 'check_room_action'

        @staticmethod
        def create_room_db():
            with open('/Users/haoce/Documents/IP5/data/room.csv', 'r') as f:
                mycsv = list(csv.reader(f))
                elements = []
                for i in range(len(mycsv)):
                    text = mycsv[i][0]
                    text = str.split(text, ";")
                    temp = []
                    for j in range(len(text)):
                        temp.append(text[j])
                    elements.append(temp)

                for k in range(1, len(elements)):
                    for l in range(len(elements[0])):
                        elements[k][l] = int(elements[k][l])

            return elements

        @staticmethod
        def create_timetable_db():
            with open('/Users/haoce/Documents/IP5/data/timetable.csv', 'r') as f:
                mycsv = list(csv.reader(f))
                elements = []
                for i in range(len(mycsv)):
                    temp = str.split(mycsv[i][0], ";")
                    elements.append(temp)

                for i in range(len(elements)):
                    for j in range(len(elements[0])):
                        if (elements[i][j].isdigit()):
                            elements[i][j] = int(elements[i][j])

                return elements


        def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

            num_p = tracker.get_slot('num_persons')
            room_type = tracker.get_slot('room_type')
            db = self.create_room_db() #get the database of the room information
            temp_num_p = []
            booked = True

            #select all the rooms which the number of person is equal or bigger then required
            for i in range(1,len(db)):
                if num_p <= db[i][1]:
                    temp_num_p.append(db[i])

            #select the room type which is required
            #1 means true, 0 means false
            temp_room_type = []
            index = 0
            for i in range(len(db[0])):
                if room_type == db[0][i]:
                    index = i

            for i in range(len(temp_num_p)):
                if temp_num_p[i][index] == 1:
                    temp_room_type.append(temp_num_p[i])

            #only the rooms, which fits the requirement of the user, are left
            for i in range(len(temp_room_type)):
                dispatcher.utter_message(text="Possibilities are: " + str(temp_room_type[i][0]))

                #check the timetable whether this room is available or not
                timetable = self.create_timetable_db()
                room = int(temp_room_type[i][0])
                date_temp = tracker.get_slot('from_date')
                date_temp = str.split(date_temp,'-')
                date = ""

                for i in range(len(date_temp)):
                    date += date_temp[i]
                date = int(date)

                year = int(date_temp[0])
                month = int(date_temp[1])
                day = int(date_temp[2])

                time_temp = tracker.get_slot('from_time')
                time_temp = str.split(time_temp, ":")
                time_start = ""

                for i in range(len(time_temp)):
                    time_start += time_temp[i];
                time_start = int(time_start)

                hour = int(time_temp[0])
                minute = int(time_temp[1])
                second = int(time_temp[2])

                duration = tracker.get_slot('duration')

                time = datetime.datetime(year, month, day, hour, minute, second) + datetime.timedelta(minutes=duration)

                time_end = ""
                time_int_temp = str(time.time())
                time_int_temp = str.split(time_int_temp, ":")
                for j in range(len(time_int_temp)):
                    time_end += time_int_temp[j]
                time_end = int(time_end)

                dispatcher.utter_message(text="Until Here all good: Date: " + str(date) + " Time Start: " + str(time_start)
                                         + " Time End: " + str(time_end))

                #find the room in timetable and check the time
                index = timetable[0].index(room)
                temp_timetable = []
                new_timetable = []
                for i in range(len(timetable)):
                    if (timetable[i][index] == date):
                        temp_timetable.append(timetable[i][index:index + 3])

                if(len(temp_timetable)>0):
                    for j in range(len(temp_timetable)):
                        start = int(temp_timetable[j][1])
                        end = int(temp_timetable[j][2])
                        if (start < time_start < end):
                            dispatcher.utter_message(text="there is meeting with this start time")
                            booked = False
                            break
                        if (start < time_end < end):
                            dispatcher.utter_message(text="here is meeting with this end time")
                            booked = False
                            break
                        else:
                            booked = True
                else:
                    booked = True

                if (booked):
                    dispatcher.utter_message(text="Booking successfull")
                else:
                    dispatcher.utter_message(text="Booking unsuccessfull")


            return []

