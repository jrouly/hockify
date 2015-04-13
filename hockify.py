# hockify

from bs4 import BeautifulSoup
import requests, time, csv

page = requests.get("http://www.nhl.com/ice/schedulebyseason.htm")
soup = BeautifulSoup(page.text)

schedule_tbl = soup.find(class_="data schedTbl")
rows = schedule_tbl.find_all("tr")[1:]
rows = [row.find_all("td", class_=["date", "team", "time", "tvInfo"]) for row in rows]

breakdown = [{
        "date": row[0].text.replace("\n",""),
        "visiting_team": row[1].text.replace("\n",""),
        "home_team": row[2].text.replace("\n",""),
        "time": row[3].text.replace("\n",""),
        "network": row[4].text.replace("\n","")
        } for row in rows
]

for entry in breakdown:
    entry['date'] = entry['date'][:entry['date'].find('2015')+4]

clean_time = lambda inp: inp if "TBD" in inp else inp[:inp.find('ET')+2]

for entry in breakdown:
    entry['time'] = clean_time(entry['time'])

headers = [
        "Subject",
        "Start Date",
        "Start Time",
        "End Date",
        "End Time",
        "All Day Event",
        "Description",
        "Location",
        "Private"
]

subject = lambda entry: entry['visiting_team'] + " vs " + entry['home_team']
start_date = lambda entry: entry['date']
start_time = lambda entry: "7:00 pm" if "TBD" in entry['time'] else entry['time']
end_date = start_date
end_time = start_time
description = lambda entry: entry['network']
location = lambda entry: entry['home_team']

fp = open("hockey.csv", "w")
hockeywriter = csv.DictWriter(fp, fieldnames=headers)

hockeydict = [
        {
            "Subject":subject(entry),
            "Start Date":start_date(entry),
            "Start Time": start_time(entry),
            "End Date": end_date(entry),
            "End Time":end_time(entry),
            "All Day Event":False,
            "Description":description(entry),
            "Location":location(entry),
            "Private":False
        } for entry in breakdown
]

hockeywriter.writeheader()

for hockey in hockeydict:
    if hockey['Start Time'] == "7:00 pm":
        hockey['Start Time'] = "7:00 PM ET"
    if hockey['End Time'] == "7:00 pm":
        hockey['End Time'] = "7:00 PM ET"

for hockey in hockeydict:
    hockey['Start Time'] = time.strftime("%I:%M %p", time.strptime(hockey['Start Time'], "%I:%M %p ET"))
    hockey['End Time'] = time.strftime("%I:%M %p", time.strptime(hockey['End Time'], "%I:%M %p ET"))

for hockey in hockeydict:
    hockey['Start Date'] = time.strftime("%m/%d/%Y", time.strptime(hockey['Start Date'], "%a %b %d, %Y"))
    hockey['End Date'] = time.strftime("%m/%d/%Y", time.strptime(hockey['End Date'], "%a %b %d, %Y"))

hockeywriter.writerows(hockeydict)

fp.close()

# hockify
