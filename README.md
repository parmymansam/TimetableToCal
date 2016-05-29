# TimetableToCal
Simple web scraper that retrieves the units currently enrolled in for the semester and when/where the classes are. 
Uses the Google Calander API to add the events to a calander.
##Requires:
  - BeautifulSoup
  - Google Calendar API
  - Getpass
  - Requests

### Limitations:
  Limited to classes that are once a week and to semesters, not trimesters.

##To use:
  1.  Enter Student ID and password at prompt
  2.  Allow access to google calander to create the events
  3.  Program will create a calander called Curtin Units and add the events to it
  
##To-Do:
  - Add color coding to events
  - Give ability for program to read semester dates from Curtin academic dates pdf
  - Add a GUI
  - Account for fortnightly/once every XXX/XXX per semester units
