# author: Renyi Tang
# time: September 2018

import time

# different time stages
EM = 'Early Morning'
M = 'Morning'
A = 'Afternoon'
E = 'Evening'
ALL_TIME = {EM,M,A,E}

# different airlines
NA_MAJOR = {'American','United','Delta','Air Canada'}
NA = {'American','United','Delta','Air Canada','Southwest','JetBlue','Alaska',
      'Hawaiian','Spirit','Frontier'}
CN_MAJOR = {'Air China','China Eastern','China Southern','Hainan'}
CN = {'Air China','China Eastern','China Southern','Hainan','Shanghai',
         'Shenzhen','Xiamen','Shandong','Tianjin','Sichuan','Juneyao','Spring'}
MAJOR = {'American','United','Delta','Air Canada',
         'Air China','China Eastern','China Southern','Hainan'}
ALL = {'American','United','Delta','Air Canada','Southwest','JetBlue','Alaska',
      'Hawaiian','Spirit','Frontier',
      'Air China','China Eastern','China Southern','Hainan','Shanghai',
      'Shenzhen','Xiamen','Shandong','Tianjin','Sichuan','Juneyao','Spring'}



def qualify(element, price_max, stops_max, duration_max, layover_max, depart_stage, arrive_stage, alines):
    if (element['price'] > float(price_max) or
        element['stops'] > float(stops_max) or
        element['hours'] > float(duration_max) or
        element['total layover hours'] > float(layover_max)):
        return False
    if depart_stage == 'ALL_TIME':
        depart_stage = eval('ALL_TIME')
    else:
        depart_stage = {eval(x) for x in depart_stage.split(',')}
    if arrive_stage == 'ALL_TIME':
        arrive_stage = eval('ALL_TIME')
    else:
        arrive_stage = {eval(x) for x in arrive_stage.split(',')}
    if ((time_stage(element['timing'][0]['depart time']) not in depart_stage) or
        (time_stage(element['timing'][-1]['arrive time']) not in arrive_stage)):
        return False
    if (alines != 'None'):
        for airline in element['airlines']:
            if (airline not in eval(alines)):
                return False
    return True

def time_stage(time1):
    suffix = time1[-2:]
    if (suffix == 'am'):
        if (int(time1[0]) in range(1,5)) or (time1[0:2] == '12'):
            return EM
        if int(time1[0]) in range(5,12):
            return M
    if (suffix == 'pm'):
        if (int(time1[0]) in range(1,6)) or (time1[0:2] == '12'):
            return A
        if int(time1[0]) in range(6,12):
            return E
        
def my_print(lists):
    if (lists == []):
        print("No available airlines found. Please change your parameters and run the program again.")
    else:
        print("Printing all available airlines ranked by price...")
        print()
        time.sleep(1)
        for element in lists:
            print('----------------------------')
            print(element['leave on'], '|', element['return on'])
            print(element['departure'], '->', element['arrival'])
            print(element['price'])
            print(element['stops'])
            print(element['hours'], '|', element['total layover hours'])
            for airline in element['airlines']:
                print(airline, end = ' ')
            print()
            print('----------------------------')
            for journey in element['timing']:
                print(journey['flight code'])
                print(journey['depart airport'], '->',
                      journey['arrive airport'])
                print(journey['depart date'], '@',
                      journey['depart time'], '->',
                      journey['arrive date'], '@',
                      journey['arrive time'])
                print('----------------------------')
            print()
            print()
            time.sleep(0.5)
        print("End of all available airlines.")