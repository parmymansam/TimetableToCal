
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

semDates = {
    '2016Sem1': '2/29/16',
    '2016Sem2': '8/1/16',
    '2017Sem1': '2/27/16',
    '2017Sem2': '8/31/16',
    '2018Sem1': '2/26/16',
    '2018Sem2': '8/30/16'
}
Days = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday':2,
    'Thursday':3,
    'Friday':4
}

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

    #start_string = str(week[2]) + "-" + str(week[1]) + "-" + str(week[0] + day) + " " + str(when[1].hour) + ":" + str(when[1].minute)
    startweek = datetime(week[2], week[1], week[0], when[1].hour, when[1].minute, 0)
    #startweek = datetime.strptime(start_string, "%Y-%m-%d %H:%M")
    start = startweek + day
    
    #end_string = str(week[2]) + "-" + str(week[1]) + "-" + str(week[0] + day) + " " + str(when[3].hour) + ":" + str(when[3].minute)
    endweek = datetime(week[2], week[1], week[0], when[3].hour, when[3].minute, 0)
    #endweek = datetime.strptime(end_string, "%Y-%m-%d %H:%M")
    end = endweek + day

    return ClassEvent(typeE, start, end, day, where)

def get_credentials():
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

def createEvent(classevent, unitname, calID, service):
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
                'RRULE:FREQ=WEEKLY;COUNT=12'
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method' : 'popup', 'minutes': 10}
            ]
        }
    }

    event = service.events().insert(calendarId=calID, body=event).execute()
            
def createCalendar(creds, service):
    calendar = {
    'summary': 'Curtin Class Timetable',
    'timeZone': 'Australia/Perth'
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    print("Calender made")
    return created_calendar['id']
    
def addToCalendar(cal_id, units, service):
    
    for unit in units:
        print("\n\nAdding events for " + unit.name)
        
        for event in unit.classEvents:
            print("Adding " + event.type)
            createEvent(event, unit.name, cal_id, service)  
        
if __name__ == '__main__':
    
    username = input("Student ID: ")
    password = getpass.getpass()
    day = int(input("Day: "))
    month = int(input("Month: "))
    year = int(input("Year: "))
    week = [day, month, year]
    
    scraper = Scraper(username, password, week)
    
    creds = get_credentials()
    http = creds.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    calID = createCalendar(creds, service)
    addToCalendar(calID, scraper.units, service)
    
