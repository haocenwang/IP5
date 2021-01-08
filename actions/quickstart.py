from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def postapi(create_evnets):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    #post Calendar API
    event = service.events().insert(calendarId='primary', body=create_evnets).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def getapi():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 100 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    #json_string = json.dumps(events)
    #print(json_string)

    timetable = []
    index = 0
    if not events:
        print('No upcoming events found.')
    for event in events:
        room_id = []
        start = event['start'].get('dateTime', event['start'].get('date'))
        room = event['location']
        room_id.append(room)
        if (timetable.__contains__(room_id) == False):
            timetable.append(room_id)
        index += 1

    for i in range(len(timetable)):
        loc = timetable[i]
        #print(timetable[i])
        for event in events:
            room = event['location']
            # print(room)
            if (room == loc[0]):
                start = event['start'].get('dateTime', event['start'].get('date'))
                date_start = start[:10]
                date_start = date_start.translate({ord('-'): None})
                start_time = start[11:19]
                start_time = int(date_start + start_time.translate({ord(':'): None}))
                end = event['end'].get('dateTime', event['end'].get('date'))
                date_end = end[:10]
                date_end = date_end.translate({ord('-'): None})
                end_time = end[11:19]
                end_time = int(date_end + end_time.translate({ord(':'): None}))
                timetable[i].append(start_time)
                timetable[i].append(end_time)

    #print(timetable)
    return timetable


