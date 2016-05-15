import requests
from bs4 import BeautifulSoup
import getpass

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
            time = classtype.select('.cssTtableNavMainWhen .cssTtableNavMainContent')
            where = classtype.select('.cssTtableNavMainWhere .cssTtableNavMainContent')
            
            print(''.join(type[0].findAll(text=True)).strip())
            print(''.join(time[0].findAll(text=True)).strip())
            print(''.join(where[0].findAll(text=True)).strip() + "\n")
            
        print("\n\n")
        i = i + 1