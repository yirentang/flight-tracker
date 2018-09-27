# author: Renyi Tang
# time: September 2018

import requests
import json
import sched, time
import argparse
from lxml import html

import auxillary

lists = []

def retriever(round_trip, src, dst, date1, date2):
    try:
        if round_trip == 'yes':
            url = ("https://www.expedia.com/Flights-Search?trip=roundtrip&"+
                "leg1=from:{0},to:{1},departure:{2}TANYT&"+
                "leg2=from:{1},to:{0},departure:{3}TANYT&"+
                "passengers=adults%3A1%2Cchildren%3A0%2Cseniors%3A0%2Cinfantinlap%3AY&"+
                "options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com").format(src, dst, date1, date2)
        elif round_trip == 'no':
            url = ("https://www.expedia.com/Flights-Search?trip=oneway&"+
                "leg1=from:{0},to:{1},departure:{2}TANYT&"+
                "passengers=adults%3A1%2Cchildren%3A0%2Cseniors%3A0%2Cinfantinlap%3AY&"+
                "options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com").format(src, dst, date1)
        else:
            print("error: invalid input for round_trip\n You have to enter 'yes' or 'no'.")
        response = requests.get(url)
        parser = html.fromstring(response.text)
        json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
        # json_data_xpath is a list of json-structured objects
        raw_json = json.loads(json_data_xpath[0] if json_data_xpath else '')
        flight_data = json.loads(raw_json["content"])
        return flight_data
    except ValueError:
        return ("Unable to process the page. Please make sure your parameters are of the correct form.\n"+
            "Enter 'python parser.py -h' for more information.")

def parse(round_trip, src, dst, date1, date2):
    flight_data = retriever(round_trip, src, dst, date1, date2)
    flight_info = {}
    
    leave_date = date1
    if round_trip == 'yes':
        back_date = date2
    else:
        back_date = 'N/A'

    for key in flight_data['legs']:
        temp = flight_data['legs'][key]
        
        # get info about number of stops and price
        num_stops = int(temp['stops'])
        price = int(temp['price']['offerPrice'])
        
        # get info about departure
        departure_city = temp['departureLocation']['airportCity']
        departure_airport_code = temp['departureLocation']['airportCode']
        departure_info = departure_city + ", " + departure_airport_code
        
        # get info about arrival
        arrival_city = temp['arrivalLocation']['airportCity']
        arrival_airport_code = temp['arrivalLocation']['airportCode']
        arrival_info = arrival_city + ", " + arrival_airport_code
    
        # get info about duration    
        hours = temp['duration']['hours']
        minutes = temp['duration']['minutes']
        hours = float('%.1f'%(hours + minutes / 60))
        
        timing = []
        airline_names = []
        single_airline = temp['carrierSummary'].get('airlineName','')
        if single_airline != '':
            airline_names.append(single_airline)
        layover_hours = 0
        layover_minutes = 0
        
        for timeline in temp['timeline']:
            if timeline['type'] == 'Segment':
                depart_airport = timeline['departureAirport']['longName']
                depart_date = timeline['departureTime']['date']
                depart_time = timeline['departureTime']['time']
                arrive_airport = timeline['arrivalAirport']['longName']
                arrive_date = timeline['arrivalTime']['date']
                arrive_time = timeline['arrivalTime']['time']
                flight_code = (timeline['carrier']['airlineCode'] + timeline['carrier']['flightNumber'])
                flight_timing = {'depart airport':depart_airport,
                                 'depart date':depart_date,
                                 'depart time':depart_time,
                                 'arrive airport':arrive_airport,
                                 'arrive date':arrive_date,
                                 'arrive time':arrive_time,
                                 'flight code':flight_code}
                timing.append(flight_timing)
                if (single_airline == ''):
                    airline_names.append(timeline['carrier']['airlineName'])
            if timeline['type'] == 'Layover':
                layover_hours += timeline['duration']['hours']
                layover_minutes += timeline['duration']['minutes']
        layover_hours += layover_minutes / 60
        layover_minutes = layover_minutes % 60
        layover_total = float('%.1f'%(layover_hours + layover_minutes / 60))
        
        # collect information about one flight, and then add it to the list
        flight_info = {'leave on':leave_date,
                       'return on': back_date,
                       'price':price,
                       'stops':num_stops,
                       'departure':departure_info,
                       'arrival':arrival_info,
                       'hours':hours,
                       'total layover hours':layover_total,
                       'airlines':airline_names,
                       'timing':timing}

        arg_list = [] # argument list for the "qualify" function
        f = open("requirements.txt", 'r')
        for line in f:
            if (line[0:3] == '>> '):
                arg_list.append(line[3:len(line) - 1])
        price_max, stops_max, duration_max, layover_max, depart_stage, arrive_stage, alines = arg_list
        if (auxillary.qualify(flight_info, price_max, stops_max, duration_max,
                    layover_max, depart_stage, arrive_stage, alines)):
            lists.append(flight_info)
    
    lists.sort(key = lambda k: k['price'], reverse = False)
    auxillary.my_print(lists)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('round_trip', help = "'yes' for round trip, 'no' for one-way trip")
    argparser.add_argument('src', help = "Departure airport/area code (example: 'LAX' or 'lax')")
    argparser.add_argument('dst', help = 'Destination airport/area code')
    argparser.add_argument('date1', help = "Leave date: MM/DD/YYYY (make sure numbers of digits are exact)")
    argparser.add_argument('date2', help = "Back date: MM/DD/YYYY ('none' for one-way)")
    
    args = argparser.parse_args()
    round_trip = args.round_trip
    src = args.src
    dst = args.dst
    date1 = args.date1
    date2 = args.date2
    parse(round_trip, src, dst, date1, date2)

'''schedule = sched.scheduler(time.time, time.sleep)

def scheduler(round_trip,limit,src,dst,mon,date,yr,mon2=None,date2=None,yr2=None):
    time_cnt = 0;
    while (True):
        schedule.enter(time_cnt,0,parse,\
                       (round_trip,src,dst,mon,date,yr,mon2,date2,yr2))
        time_cnt += 900
        schedule.run()'''