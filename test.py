from bs4 import BeautifulSoup
import requests
import datetime
import os

# page = requests.get("https://m.bus-transport.ru/time-table/GTP_01/500005300")
# soup = BeautifulSoup(page.content, "html.parser")
# time_data = soup.find_all("div")
# timetable = []
# next = True
# for time in time_data:
#     time_text = time.text.strip()
#     if time_text == '':
#         next = True
#     if next == False:
#         timetable.append([hour, time_text])
#     if (next == True) and (time_text != '') and (time_text.isnumeric()):
#         hour = time_text
#         next = False
# print(timetable)

# page = requests.get("https://m.bus-transport.ru/route/GTP_14/")
# soup = BeautifulSoup(page.content, "html.parser")
# target = soup.find_all("h3")
# list = target[0].find_next_sibling()
# stops = list.find_all("a")
# for stop in stops:
#     print(stop.text.strip())

# date = datetime.date.today()
# new_date = "{}.{}.{}".format(date.day, date.month, date.year)
# print(new_date)


# if t.weekday() < 5:
#     days_until_saturday = 5 - t.weekday
#     date_weekend = t + timedelta(days=days_until_saturday)
#     date_weekend_url = "?date=" 

print(os.path.isfile("./output.json"))