from bs4 import BeautifulSoup
import requests
import json
import os

def main():
    parser = PTParser()
    # parser.update()
    parser.getTimetable(14)

class PTParser:
    def __init__(self):
        self.url = "https://m.bus-transport.ru/"
        if (os.path.isfile("parser/output.json") and os.path.getsize("parser/output.json")) > 0:
            with open("parser/output.json", 'r') as json_file:
                self.bus = json.load(json_file)

    def update(self):
        url_buses = "https://m.bus-transport.ru/addresses/2/routes-list/0/"
        url_trams = "https://m.bus-transport.ru/addresses/2/routes-list/2/"
        self.bus = self.parseRoutes(url_buses)

    def getRoute(self, number):
        output = [item for item in self.bus if item["number"] == str(number)]
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

    
    def parseRoutes(self, url):
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
                    "stops_opposite": stops[1]
                }
                output.append(route_entry)
        with open("parser/output.json", 'w') as json_file:
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
            new_url = self.url + stop_href
            # timetable = self.parseTime(new_url)
            timetable = [0]
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
                new_url = self.url + stop_href
                # timetable = self.parseTime(new_url)
                timetable = [0]
                stops_opposite.append([stop_name, stop_href])
        return [stops_straight, stops_opposite]
    
    def parseTime(self, url):
        url = self.url + url
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