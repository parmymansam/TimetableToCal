from bs4 import BeautifulSoup
import requests
import getpass

class Unit:
    def __init__(self, name, classEvents):
        self.name = name
        self.classEvents = classEvents
    
class ClassEvent:
    def __init__(self, type, time, place)
        self.type = type
        self.time = time
        self.place = place

    
class Scraper:
    def __init__(self, username, password):
        self.units[] = units
        
        payload = {
        'UserName' : username,
        'Password' : password,
        'submit' : 'Login' 
        }
        
        login_url = 'https://oasis.curtin.edu.au'
        timetable_url = 'https://estudent.curtin.edu.au/eStudent/SM/StudentTtable10.aspx?r=%23CU.ESTU.STUDENT&f=%23CU.EST.TIMETBL.WEB'
        
        with requests.sessions as session:
            p = session.post(url, data = payload)
            r = session.get(timetable_url)
            data = r.text
            soup = BeautifulSoup(data)
            
            
if __name__ == '__main__':
    
    username = input("Student ID: ")
    password = getpass.getpass()
    
    Scraper(username, password)