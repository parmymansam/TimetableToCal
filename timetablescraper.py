from bs4 import BeautifulSoup
import requests
import getpass
import time
import 

class Unit:
    def __init__(self, name, classEvents):
        self.name = name
        self.classEvents = classEvents
    
class ClassEvent:
    def __init__(self, type, start, end, day, place):
        self.type = type
        self.start = start
        self.end = end
        self.day = day
        self.place = place

def formatWhen(inString):
    return inString.replace("-", " ").split()

    
def makeClassEvent(type, when, where):
    day = when[0]
    start = [when[1], when[2]]
    end = [when[3], when[4]]
    
    return ClassEvent(type, start, end, day, where)
    
class Scraper:
    def __init__(self, username, password):
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
        print("Mark 2")
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
                
                event = makeClassEvent(type, when, where)
                events.append(event)
            
            newUnit = Unit(unitName[i], events)
            self.units.append(newUnit)
            i = i + 1
def createCalenderEvents(units):
        
if __name__ == '__main__':
    
    username = input("Student ID: ")
    password = getpass.getpass()
    
    scraper = Scraper(username, password)
    