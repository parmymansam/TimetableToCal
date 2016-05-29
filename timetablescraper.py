
from bs4 import BeautifulSoup
import requests
import getpass
from datetime import datetime
from datetime import timedelta

import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Curtin Timetable Add'

semDates = [
    [datetime(2016,2,29,0,0,0), 5, 8],
    [datetime(2016,8,1,0,0,0), 5, 9],
    [datetime(2017,2,27,0,0,0), 7, 8],
    [datetime(2017,7,31,0,0,0), 5, 9],
    [datetime(2018,2,26,0,0,0), 6, 9],
    [datetime(2018,7,30,0,0,0), 5, 9]
]

Days = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday':2,
    'Thursday':3,
    'Friday':4
}

TIMETABLENAME = 'University Timetable'
class Unit:
    def __init__(self, name, classEvents):
        self.name = name
        self.classEvents = classEvents
    
class ClassEvent:
    def __init__(self, type, start, end, day, where):
        self.type = type
        self.start = start
        self.end = end
        self.day = day
        self.where = where

def formatWhen(inString):
    result = inString.replace("-", " ").split()
    
    result[1] = datetime.strptime(result[1]+result[2],"%I:%M%p")
    result[3] = datetime.strptime(result[3]+result[4],"%I:%M%p")
        
    return result

    
def makeClassEvent(typeE, when, where, week):
    day = timedelta(days=Days[when[0]])
   
    startweek = datetime(week.year, week.month, week.day, when[1].hour, when[1].minute, 0)
    start = startweek + day
    
    endweek = datetime(week.year, week.month, week.day, when[3].hour, when[3].minute, 0)
    end = endweek + day

    return ClassEvent(typeE, start, end, day, where)
    
class Scraper:
    def __init__(self, username, password, week):
        self.units = []
        
        payload = {
        'UserName' : username,
        'Password' : password,
        'submit' : 'Login' 
        }
        login_url = 'https://oasis.curtin.edu.au/Auth/LogOn'
        timetable_url = 'https://estudent.curtin.edu.au/eStudent/SM/StudentTtable10.aspx?r=%23CU.ESTU.STUDENT&f=%23CU.EST.TIMETBL.WEB'
        
        with requests.Session() as session:
            p = session.post(login_url, data = payload)
            r = session.get(timetable_url)
            data = r.text
            soup = BeautifulSoup(data, "html.parser")
        
        unitName = []
        for unit in soup.select('.cssTtableSspNavMasterSpkInfo2'):
            unitName.append(''.join(unit.findAll(text=True)))

        i = 0
        for unit in soup.select('.cssTtableSspNavDetailsContainerPanel'):
            events = []
            for classevent in unit.select('.cssTtableNavActvTop'):
                raw_type = classevent.select('.cssTtableSspNavActvNm')
                raw_time = classevent.select('.cssTtableNavMainWhen .cssTtableNavMainContent')
                raw_where = classevent.select('.cssTtableNavMainWhere .cssTtableNavMainContent')

                type = ''.join(raw_type[0].findAll(text=True)).strip()
                time = ''.join(raw_time[0].findAll(text=True)).strip()
                where = ''.join(raw_where[0].findAll(text=True)).strip()
                
                when = formatWhen(time)
                
                event = makeClassEvent(type, when, where, week)
                events.append(event)
            
            newUnit = Unit(unitName[i], events)
            self.units.append(newUnit)
            i = i + 1
    
  
class GoogleCalender:
    def __init__(self):
        self.creds = self.get_credentials()
        self.http = self.creds.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=self.http)
        print(self.calendar_exist())
        if self.calendar_exist() == False:
            self.cal_id = self.createCalendar()

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential. 
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'curtin_calendar_create.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def calendar_exist(self):
        page_token = None
        exists = False

        while True:
          calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
          for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == TIMETABLENAME:
                exists = True
                self.cal_id = calendar_list_entry['id']
                break
          page_token = calendar_list.get('nextPageToken')
          if not page_token:
            break

        return exists

    def createCalendar(self):
        calendar = {
        'summary': TIMETABLENAME,
        'timeZone': 'Australia/Perth'
        }

        created_calendar = self.service.calendars().insert(body=calendar).execute()
        print("Calender made")
        return created_calendar['id']

    def addToCalendar(self, units, sem_breaks):
        for unit in units:
            print("\n\nAdding events for " + unit.name)
            
            for event in unit.classEvents:
                print("Adding " + event.type)
                self.createEvent(event, unit.name, sem_breaks)

    def createEvent(self, classevent, unitname, sem_breaks):
        event = {
            'summary' : unitname + ' - ' +classevent.type,
            'location' : classevent.where,
            'start' : {
                'dateTime' : classevent.start.strftime("%Y-%m-%dT%H:%M:00+08:00"),
                'timeZone' : 'Australia/Perth'
            },
            'end' : {
                'dateTime' : classevent.end.strftime("%Y-%m-%dT%H:%M:00+08:00"),
                'timeZone' : 'Australia/Perth'
            },
                'recurrence' : [
                    'RRULE:FREQ=WEEKLY;COUNT=14'

            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method' : 'popup', 'minutes': 10}
                ]
            }
        }

        event = self.service.events().insert(calendarId=self.cal_id, body=event).execute()
        
        instances = self.service.events().instances(calendarId=self.cal_id, eventId=event['id']).execute()
        firstbreak = instances['items'][sem_breaks[0] - 1]
        secondbreak = instances['items'][sem_breaks[1] - 1]
        
        firstbreak['status'] = 'cancelled'
        secondbreak['status'] = 'cancelled'

        updated_instance = self.service.events().update(calendarId=self.cal_id, eventId=firstbreak['id'], body=firstbreak).execute()
        updated_instance = self.service.events().update(calendarId=self.cal_id, eventId=secondbreak['id'], body=secondbreak).execute()


if __name__ == '__main__':
    
    username = input("Student ID: ")
    #password = getpass.getpass()

    now = datetime.now();

    for indx, start in enumerate(semDates):
        if start[0] > now:
            week = semDates[indx - 1][0]
            sem_breaks = [semDates[indx - 1][1], semDates[indx - 1][2]]
            break
    
    scraper = Scraper(username, 'Galaexy64523', week)

    calendar = GoogleCalender()
    calendar.addToCalendar(scraper.units, sem_breaks)
    
