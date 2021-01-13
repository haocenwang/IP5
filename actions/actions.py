from typing import Dict, Text, Any, List, Union

from rasa.shared.core.events import UserUttered
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

        return {"from_date": date_temp}

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
            return {"from_time": None}
        else:
            return {"from_date": date_temp, "from_time": time_temp}


class CheckRoom(Action):
    option_time_start = []
    option_time_end = []
    all_options = []

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
        # http request
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
        db = self.create_room_db()  # get the database of the room information
        temp_num_p = []

        # select all the rooms which the number of person is equal or bigger then required
        for i in range(1, len(db)):
            if num_p <= db[i][1]:
                temp_num_p.append(db[i])

        # select the room type which is required
        # 1 means true, 0 means false
        temp_room_type = []
        index = 0
        for i in range(len(db[0])):
            if room_type == db[0][i]:
                index = i

        for i in range(len(temp_num_p)):
            if temp_num_p[i][index] == 1:
                temp_room_type.append(temp_num_p[i])

        ######################
        # timetable = self.create_timetable_db()
        timetable = quickstart.getapi()
        # dispatcher.utter_message(text="length: " + str(len(timetable)))
        date_temp = tracker.get_slot('from_date')
        time_temp = tracker.get_slot('from_time')

        date_temp = str.split(date_temp, '-')
        date = ""

        for i in range(len(date_temp)):
            date += date_temp[i]
        # date = int(date)

        year = int(date_temp[0])
        month = int(date_temp[1])
        day = int(date_temp[2])

        time_temp = str.split(time_temp, ":")
        time_start = ""

        for i in range(len(time_temp)):
            time_start += time_temp[i];
        # time_start = int(time_start)

        hour = int(time_temp[0])
        minute = int(time_temp[1])
        second = int(time_temp[2])

        duration = tracker.get_slot('duration')

        time = datetime.datetime(year, month, day, hour, minute, second) + \
               datetime.timedelta(minutes=duration)

        time_end = ""
        time_int_temp = str(time.time())
        time_int_temp = str.split(time_int_temp, ":")
        for j in range(len(time_int_temp)):
            time_end += time_int_temp[j]
        # time_end = int(time_end)

        eventstart = int(date + time_start)
        eventend = int(date + time_end)
        rooms = []
        room_timetable = []
        booked = True

        # only the rooms, which fits the requirement of the user, are left
        for i in range(len(temp_room_type)):
            dispatcher.utter_message(text="Possibilities are: " + str(temp_room_type[i][0]))
            rooms.append("Room: " + str(temp_room_type[i][0]))
            # check the timetable whether this room is available or not
            room = "Room: " + str(temp_room_type[i][0])
            # find the room in timetable and check the time
            for i in range(len(timetable)):
                if timetable[i][0] == room:
                    room_timetable.append(timetable[i])

        for i in range(len(room_timetable)):
            print("timetable[i][0]: " + room_timetable[i][0])

        start_index = 0
        if len(room_timetable) > 0:
            for i in range(len(room_timetable)):
                temp_timetable = room_timetable[i][1:]
                print(temp_timetable)
                while start_index < len(temp_timetable):
                    if ((temp_timetable[start_index] <= eventstart) &
                            (temp_timetable[start_index + 1] > eventstart)):
                        booked = False
                        dispatcher.utter_message(text="Start Time Conflict with room: " + room_timetable[i][0])
                        break
                    else:
                        start_index += 2
                start_index = 0;
                while start_index < len(temp_timetable) - 1:
                    if ((temp_timetable[start_index] < eventend) &
                            (temp_timetable[start_index + 1] > eventend)):
                        booked = False
                        dispatcher.utter_message(text="End Time Conflict with room: " + room_timetable[i][0])
                        break
                    else:
                        start_index += 2

                if booked:
                    dispatcher.utter_message(text="Booking successfull")
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
                        'location': str(room_timetable[i][0]),
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
                    dispatcher.utter_message(text="Enter 0 to exit")
                    break
                else:
                    continue

            if not booked:
                dispatcher.utter_message(text="Sorry. There is no room available according to your requirement")
                dispatcher.utter_message(text="I am going to look some Options for you")

                index_option = 1
                room_index = 0
                for i in range(len(room_timetable)):
                    start = int(date + '080000')
                    end = int(date + '200000')
                    # print(start)
                    # print(end)
                    temp_time = []
                    temp_timetable = room_timetable[i][1:]
                    print(temp_timetable)
                    for i in range(len(temp_timetable)):
                        if (int(temp_timetable[i]) >= start) & (int(temp_timetable[i]) <= end):
                            temp_time.append(int(temp_timetable[i]))
                    # print(temp_time)

                    if temp_time.__contains__(start):
                        index = 1;
                        while index < len(temp_time):
                            self.option_time_start.append(temp_time[index])
                            index += 2
                    else:
                        self.option_time_start.append(start)
                        index = 1
                        while index < len(temp_time):
                            self.option_time_start.append(temp_time[index])
                            index += 2

                    print(self.option_time_start)

                    if (temp_time.__contains__(end)):
                        if (self.option_time_start.__contains__(start)):
                            index = 0
                            while (index < len(temp_time)):
                                self.option_time_end.append(temp_time[index])
                                index += 2
                        else:
                            index = 0
                            while (index < len(temp_time)):
                                self.option_time_end.append(temp_time[index])
                                index += 2

                    else:
                        if (self.option_time_start.__contains__(start)):
                            index = 0
                            while (index < len(temp_time)):
                                self.option_time_end.append(temp_time[index])
                                index += 2
                        else:
                            index = 2
                            while (index < len(temp_time)):
                                self.option_time_end.append(temp_time[index])
                                index += 2
                        self.option_time_end.append(end)
                    print(self.option_time_end)

                    if (len(self.option_time_start) > len(self.option_time_end)):
                        self.option_time_start = self.option_time_start[:-1]

                    room = room_timetable[room_index][0]
                    room_index += 1

                    for i in range(len(self.option_time_start)):
                        start = str(self.option_time_start[i])
                        start = start[8:]
                        start_time = datetime.time(int(start[:2]), int(start[2:4]), int(start[4:]))
                        end = str(self.option_time_end[i])
                        end = end[8:]
                        end_time = datetime.time(int(end[:2]), int(end[2:4]), int(end[4:]))
                        string = "Option " + str(index_option) + " " + room + \
                                 " between " + str(start_time) + \
                                 " and " + str(end_time)
                        dispatcher.utter_message(string)
                        self.all_options.append(string)
                        index_option += 1
                    self.option_time_start = []
                    self.option_time_end = []
                dispatcher.utter_message(template="utter_ask_num_option")

        return []


class ValidateNumOption(FormValidationAction):

    def name(self) -> Text:
        return 'validate_booking_form'

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""
        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_num_option(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate num_people value."""

        if self.is_int(value) and int(value) >= 0:
            dispatcher.utter_message(text="In progress")
            return {"num_option": value}
        else:
            dispatcher.utter_message(text="Wrong Number")
            # validation failed, set slot to None
            return {"num_option": None}


class BookingConfirm(Action):

    def name(self) -> Text:
        return 'confirm_booking_action'

    def run(
            self,
            dispatcher,
            tracker: Tracker,
            domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        num_option = tracker.get_slot("num_option")
        dispatcher.utter_message("num_option: " + str(num_option))
        if num_option == 0:
            dispatcher.utter_message(text="Thank you for your visit")
        else:
            num_option -= 1
            all_options = CheckRoom.all_options
            string = all_options[num_option]
            string = string.split()

            start_time = string[5]
            print("start_time: " + start_time)
            start_time = start_time.translate({ord(':'): None})
            #print(start_time)
            end_time = string[7]
            print("end_time: " + end_time)
            end_time = end_time.translate({ord(':'): None})
            # print(start_time)

            date_temp = tracker.get_slot('from_date')
            date_temp = str.split(date_temp, '-')
            date = ""

            for i in range(len(date_temp)):
                date += date_temp[i]
            # date = int(date)

            year = int(date_temp[0])
            month = int(date_temp[1])
            day = int(date_temp[2])

            start = datetime.datetime(year, month, day,
                                      int(start_time[:2]), int(start_time[2:4]), int(start_time[4:]))

            end = datetime.datetime(year, month,day,
                                    int(end_time[:2]),int(end_time[2:4]), int(end_time[4:]))

            time_sec = int(datetime.timedelta.total_seconds(end - start) / 60)
            print(time_sec)

            duration = tracker.get_slot('duration')
            if (time_sec > duration):
                end = datetime.datetime(year, month,day,
                                        int(start_time[:2]), int(start_time[2:4]), int(start_time[4:])) + \
                      datetime.timedelta(minutes=duration)

            else:
                end = datetime.datetime(year, month,day,
                                        int(end_time[:2]),int(end_time[2:4]), int(end_time[4:]))
            print(start)
            print(end)

            start = str(start)
            start = start.split()
            date = start[0]
            start = start[1]
            end = str(end)
            end = end.split()
            end = end[1]
            room = string[2] + " " + string[3]
            print(start)
            print(end)
            print(room)
            create_event = {
                'summary': 'Meeting',
                'location': room,
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

        return []
