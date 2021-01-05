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

from actions import quickstart


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
            #http request
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
            #quickstart.getapi()
            num_p = tracker.get_slot('num_persons')
            room_type = tracker.get_slot('room_type')
            db = self.create_room_db() #get the database of the room information
            temp_num_p = []
            booked = True
            new_timetable = []

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

            timetable = self.create_timetable_db()
            date_temp = tracker.get_slot('from_date')
            date_temp = str.split(date_temp, '-')
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

            posistion = 0
            rooms = []

            #only the rooms, which fits the requirement of the user, are left
            for i in range(len(temp_room_type)):
                dispatcher.utter_message(text="Possibilities are: " + str(temp_room_type[i][0]))
                rooms.append(temp_room_type[i][0])
                #check the timetable whether this room is available or not
                room = int(temp_room_type[i][0])
                #find the room in timetable and check the time
                index = timetable[0].index(room)
                temp_timetable = []

                for i in range(len(timetable)):
                    if (timetable[i][index] == date):
                        temp_timetable.append(timetable[i][index:index + 3])

                if(len(temp_timetable)>0):
                    for j in range(len(temp_timetable)):
                        start = int(temp_timetable[j][1])
                        end = int(temp_timetable[j][2])
                        if (start < time_start < end):
                            #dispatcher.utter_message(text="there is meeting with this start time")
                            posistion = j
                            booked = False
                            break
                        if (start < time_end < end):
                            #dispatcher.utter_message(text="here is meeting with this end time")
                            posistion = j
                            booked = False
                            break
                else:
                    booked = True
                    new_timetable.append([room,date,time_start,time_end,room_type])

            if (len(new_timetable)>0):
                dispatcher.utter_message(text="Booking successfull")
                for i in range(len(new_timetable)):
                    dispatcher.utter_message(text="Room: " + str(new_timetable[i][0]) + " Date: " + str(date)
                                             + " - " +  str(time_start) + " until " + str(time_end))
                    date_temp = str(date)
                    date_temp = date_temp[:4] + "-" + date_temp[4:]
                    date = date_temp[:7] + "-" + date_temp[7:]

                    time_temp = str(time_start)
                    time_temp = time_temp[:2] + ":" + time_temp[2:]
                    start = time_temp[:5] + ":" + time_temp[5:]

                    time_temp = str(time_end)
                    time_temp = time_temp[:2] + ":" + time_temp[2:]
                    end = time_temp[:5] + ":" + time_temp[5:]

                    dispatcher.utter_message(date + " " + start + " " + end)
                    create_event = {
                        'summary': 'Meeting',
                        'location': 'Room: ' + str(new_timetable[i][0]),
                        'description': '',
                        'start': {
                            'dateTime': date + 'T' + start,
                            'timeZone': 'Europe/Zurich',
                        },
                        'end': {
                            'dateTime': date + 'T' + end,
                            'timeZone': 'Europe/Zurich',
                        },

                        'attendees': [
                            {'email': 'lpage@example.com'},
                            {'email': 'sbrin@example.com'},
                        ],
                        'reminders': {
                            'useDefault': False,
                            'overrides': [
                                {'method': 'email', 'minutes': 24 * 60},
                                {'method': 'popup', 'minutes': 10},
                            ],
                        },
                    }
                    quickstart.postapi(create_event)
            else:
                dispatcher.utter_message(text="Sorry. There is no room available according to your requirement")
                dispatcher.utter_message(text="I am going to look some Options for you")
                temp_newtime = []
                for i in range(len(rooms)):
                    if (posistion == 0):
                        if (temp_timetable[0][1] != 80000):
                            start = 80000
                            end = temp_timetable[0][1]
                            dispatcher.utter_message(text="Option 1: " + "Room " + str(rooms[i])
                                                          + " On " + str(date) + " : " + str(start)
                                                          + " until " + str(end) + " is free")
                        else:
                            start = temp_timetable[0][2]
                            end = temp_timetable[1][1]
                            dispatcher.utter_message(text="Option 1: " + "Room " + str(room[i])
                                                          + "On " + str(date) + " : " + str(start)
                                                          + " - " + str(end) + " is free")
                    else:
                        dispatcher.utter_message(text="else")
                        start1 = temp_timetable[posistion - 1][2]
                        end1 = temp_timetable[posistion][1]
                        start2 = temp_timetable[posistion][2]
                        end2 = temp_timetable[posistion + 1][1]
                        dispatcher.utter_message(text="Option 1: " + "Room " + str(room[i])
                                                 + "On " + str(date) + " : " + str(start1)
                                                 + " - " + str(start2) + " is free")
                        break

                room_without_type = []
                for i in range(len(temp_num_p)):
                    room_without_type.append(temp_num_p[i][0])

                for j in range(len(rooms)):
                    room_without_type.remove(rooms[j])

                db_rooms = []
                for k in range(len(room_without_type)):
                    index = timetable[0].index(room_without_type[k])
                    temp_elements = []
                    for i in range(len(timetable)):
                        if (timetable[i][index] == date):
                            temp_elements.append(timetable[i][index:index + 3])
                    booked = True
                    p = 0
                    if (len(temp_elements) != 0):
                        for i in range(len(temp_elements)):
                            start = int(temp_elements[i][1])
                            end = int(temp_elements[i][2])
                            if (start < int(time_start) < end):
                                p = i
                                booked = False
                                break
                            if (start < int(time_end) < end):
                                p = i
                                booked = False
                                break

                    else:
                        dispatcher.utter_message(text= "Option 2: Room without " + str(room_without_type[k])
                                                       + "(without " + room_type + ")" + " On " + str(date)
                                                       + " : " + str(time_start) + " until " + str(time_end))

            return []

