from bs4 import BeautifulSoup
import requests
import json
import pickle
import datetime
from datetime import timedelta
import os
import io
import sys

def main():
    parser = PTParser()
    # parser.update()
    # parser.getTimetable(14)
    # updated_stops = parser.checkTerminae([81])
    # if len(updated_stops) > 0:
    #     print("Обновлено расписание:")
    #     for stop in updated_stops:
    #         print(stop)
    parser.showTerminae([81])
    parser.listRoutes("bus")

class PTParser:
    def __init__(self):
        self.url = "https://m.bus-transport.ru/"
        if (os.path.isfile("./output.json") and os.path.getsize("./output.json")) > 0:
            with open("./output.json", 'r') as json_file:
                self.bus = json.load(json_file)

    def update(self):
        url_buses = "https://m.bus-transport.ru/addresses/2/routes-list/0/"
        url_trams = "https://m.bus-transport.ru/addresses/2/routes-list/2/"
        self.bus = self.parseRoutes(url_buses, "bus")

    def getRoute(self, number):
        output = [item for item in self.bus if item["number"] == str(number)]
        if not output:
            return False
        else:
            return output[0]

    def getTimetable(self, number):
        route = self.getRoute(number)
        direction = input("Please choose a direction (s/o):")
        if direction == "s":
            for i in route["stops_straight"]:
                print(i[0])
        if direction == "o":
            for i in route["stops_opposite"]:
                print(i[0])
        stop = input("Please choose a stop:")
        if direction == "s":
            for i in route["stops_straight"]:
                if stop == i[0]:
                    print(self.parseTime(i[1]))
        if direction == "o":
            for i in route["stops_opposite"]:
                if stop == i[0]:
                    print(self.parseTime(i[1]))

    def writeTimetable(self, file, timetable):
        update = False
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            open(file, "w").close()
            with open(file, "wb") as f:
                pickle.dump(timetable, f)
            update = True
        else:
            with open(file, "rb") as f:
                if pickle.load(f) != timetable:
                    with open(file, "wb") as f:
                        pickle.dump(timetable, f)
                    update = True
        return update
    
    def readTimetable(self, file):
        with open(file, "rb") as f:
            output = pickle.load(f)
        return output

    def checkTerminae(self, routes):
        output = io.StringIO()
        sys.stdout = output
        t = datetime.date.today()
        if t.weekday() < 5:
            days_until_saturday = 5 - t.weekday()
            date_weekend = t + timedelta(days=days_until_saturday)
        else:
            date_weekend = t
            t = t - timedelta(2)
        update = []
        for number in routes:
            route = self.getRoute(number)
            timetable_s = (self.parseTime(route["stops_straight"][0][1], t), self.parseTime(route["stops_straight"][0][1], date_weekend))
            timetable_o = (self.parseTime(route["stops_opposite"][0][1], t), self.parseTime(route["stops_opposite"][0][1], date_weekend))
            file_s = "./timetables/" + route["terminus_s"] + ".pkl"
            file_o = "./timetables/" + route["terminus_o"] + ".pkl"
            update_s = self.writeTimetable(file_s, timetable_s)
            update_o = self.writeTimetable(file_o, timetable_o)
            if update_s:
                update.append(route["number"] + " — " + route["stops_straight"][0][0])
            if update_o:
                update.append(route["number"] + " — " + route["stops_opposite"][0][0])
        if len(update) > 0:
            print("Обновлено расписание:")
            for i in update:
                print(i)
        sys.stdout = sys.__stdout__
        return output.getvalue()
        
    def showTerminae(self, routes):
        output = io.StringIO()
        sys.stdout = output
        for number in routes:
            route = self.getRoute(number)
            file_s = "./timetables/" + route["terminus_s"] + ".pkl"
            file_o = "./timetables/" + route["terminus_o"] + ".pkl"
            if not os.path.exists(file_s) or os.path.getsize(file_s) == 0:
                print("Ошибка. Нет данных для маршрута номер", number)
                break
            print("<b>Расписание маршрута ", number, "</b>")
            print("Отправления с остановки " + route["stops_straight"][0][0] + ":")
            print(' '.join(self.readTimetable(file_s)[0]))
            print("по выходным дням")
            print(' '.join(self.readTimetable(file_s)[1]))
            print("Отправления с остановки " + route["stops_opposite"][0][0] + ":")
            print(' '.join(self.readTimetable(file_o)[0]))
            print("по выходным дням:")
            print(' '.join(self.readTimetable(file_o)[1]))
            print('\n')
        sys.stdout = sys.__stdout__
        return output.getvalue()

    def listRoutes(self, type):
        output = io.StringIO()
        sys.stdout = output
        if type == "bus":
            for i in self.bus:
                print(i["number"] + " — " + i["name"])
        sys.stdout = sys.__stdout__
        return output.getvalue()

    def parseRoutes(self, url, type):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        routes = soup.find_all("a")
        output = []
        for route in routes:
            route_text = route.text.strip().split(",")
            if len(route_text) == 2:
                route_number = route_text[0]
                print(route_number)
                route_name = route_text[1]
                route_href = route.get("href")
                new_url = self.url + route_href
                stops = self.parseStops(new_url)
                route_entry = {
                    "number": route_number,
                    "name": route_name,
                    "stops_straight": stops[0],
                    "terminus_s": type + "_" + str(route_number) + "s",
                    "stops_opposite": stops[1],
                    "terminus_o": type + "_" + str(route_number) + "o"
                }
                output.append(route_entry)
        with open("./output.json", 'w') as json_file:
            json.dump(output, json_file, indent=4, ensure_ascii=False)
        

    def parseStops(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        headers = soup.find_all("h3")
        list = headers[0].find_next_sibling()
        stops_s = list.find_all("a")
        stops_straight = []
        for stop in stops_s:
            stop_name = stop.text.strip()
            stop_href = stop.get("href")
            # new_url = self.url + stop_href
            # timetable = self.parseTime(new_url)
            # timetable = [0]
            stops_straight.append([stop_name, stop_href])
        if len(headers) == 1:
            stops_opposite = []
        else:
            list = headers[1].find_next_sibling()
            stops_o = list.find_all("a")
            stops_opposite = []
            for stop in stops_o:
                stop_name = stop.text.strip()
                stop_href = stop.get("href")
                # new_url = self.url + stop_href
                # timetable = self.parseTime(new_url)
                # timetable = [0]
                stops_opposite.append([stop_name, stop_href])
        return [stops_straight, stops_opposite]
    
    def parseTime(self, url, date="today"):
        today = datetime.date.today()
        if date == today or date == "today":
            date_url = ""
        else:
            date_formatted = "{}.{}.{}".format(date.day, date.month, date.year)
            date_url = "?date=" + date_formatted
        url = self.url + url + date_url
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        time_data = soup.find_all("div")
        timetable = []
        next = True
        for time in time_data:
            time_text = time.text.strip()
            if time_text == '':
                next = True
            if next == False:
                timetable.append("{}:{}".format(hour, time_text))
            if (next == True) and (time_text != '') and (time_text.isnumeric()):
                hour = time_text
                next = False
        return timetable

if __name__ == "__main__":
    main()