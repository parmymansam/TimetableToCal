import requests
from bs4 import BeautifulSoup
import getpass
import re
import time

days = {
    'Monday' : 0,
    'Tuesday' : 1,
    'Wednesday' : 2,
    'Thursday' : 3,
    'Friday' : 4 }
    
username = input("Input StudentID: ")
password = getpass.getpass()

payload = {
    'submit' : 'Login',
    'UserName' : username,
    'Password' : password
}

print ("\nTrying login with username: " + payload['UserName'])
url = 'https://oasis.curtin.edu.au/Auth/LogOn'
with requests.Session() as s:

    p = s.post(url, data=payload)
    r = s.get('https://estudent.curtin.edu.au/eStudent/SM/StudentTtable10.aspx?r=%23CU.ESTU.STUDENT&f=%23CU.EST.TIMETBL.WEB')
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    units = []
    
    print("\nUnits currently enrolled in: \n")
    for item in soup.select('.cssTtableSspNavMasterSpkInfo2 span'):
        units.append(''.join(item.findAll(text=True)))
    i = 0
    for unit in soup.select('.cssTtableSspNavDetailsContainerPanel'):
        print (units[i] + "\n")
        for classtype in unit.select('.cssTtableNavActvTop'):
            type = classtype.select('.cssTtableSspNavActvNm')
            when = classtype.select('.cssTtableNavMainWhen .cssTtableNavMainContent')
            where = classtype.select('.cssTtableNavMainWhere .cssTtableNavMainContent')
            daytime = []
            print(''.join(type[0].findAll(text=True)).strip())
            print(''.join(where[0].findAll(text=True)).strip())
            swhen = ''.join(when[0].findAll(text=True)).strip()
            daytime = swhen.replace("-", " ").split()
            day = daytime[0]
            start = [daytime[1], daytime[2]]
            end = [daytime[3], daytime[4]]
            
            print(day)
            print(start)
            print(end)
            
        print("\n\n")
        i = i + 1