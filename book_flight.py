import requests, json, csv, argparse, datetime, time
import configparser

class Flight(object):
    def __init__(self, price, duration, booking_token):
        self.price = price
        self.duration = duration
        self.booking_token = booking_token

    def print_flight(self):
        print("Price: {0} EUR, Duration: {1}".format(self.price, time.strftime('%Hh %Mm', time.gmtime(self.duration))))

class FlightsManager(object):
    def __init__(self, flights):
        self.flights = flights

    def print_flights(self):
        for flight in self.flights:
            flight.print_flight()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Book flight')
    parser.add_argument('--from', help='Starting point')
    parser.add_argument('--to', help='Finish destination')
    parser.add_argument('--date', help='Search flights for this date')
    parser.add_argument('--one-way', action='store_true', help='Indicate one-way trip without return')
    parser.add_argument('--return', help='Book flight with passenger staying x nights in destination')
    parser.add_argument('--cheapest', action='store_true', help='Book cheapest flight')
    parser.add_argument('--shortest', action='store_true', help='Book shprtest flight')
    args = vars(parser.parse_args())

    settings = configparser.ConfigParser()
    settings.read('booking.conf')

    with open('iatacodes.csv', 'r') as f:
        reader = csv.reader(f)
        iatacodes = list(reader)

    if args['from'] not in iatacodes[0]:
        print("{0} is not valid IATA code!".format(args['from']))
        exit(1)

    if args['to'] not in iatacodes[0]:
        print("{0} is not valid IATA code!".format(args['to']))
        exit(1)

    sort='price'
    typeFlight='oneway'
    daysInDestination=''
    if args['return']:
        typeFlight='return'
        daysInDestination=args['return']

    if args['shortest'] and not args['cheapest']:
        sort='duration'
    elif args['shortest'] and args['cheapest']:
        print("Please decide if you want to book shortest or cheapest!")
        exit(1)

    flight_date = datetime.datetime.strptime(args['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
    payload = {
        'v': '3',
        'sort': sort,
        'asc': '1',
        'locale': 'us',
        'daysInDestinationFrom': daysInDestination,
        'daysInDestinationTo': daysInDestination,
        'affilid': '',
        'children': '0',
        'infants': '0',
        'flyFrom': args['from'],
        'to': args['to'],
        'featureName': 'parallelResults',
        'dateFrom': flight_date,
        'dateTo': flight_date,
        'typeFlight': typeFlight,
        'returnFrom': '',
        'returnTo': '',
        'one_per_date': '0',
        'oneforcity': '0',
        'wait_for_refresh': '1',
        'adults': '1',
        'limit': '60',
        'offset': '0'
    }

    r = requests.get(
        'https://api.skypicker.com/flights',  params=payload)

    flights = []
    for flight in r.json()["data"]:
        flights.append(Flight(int(flight["price"]), int(flight["duration"]["total"]), flight["booking_token"]))

    flights_manager = FlightsManager(flights)

    data_json = {'passengers': {"firstName": settings.get('PASSAGER', 'firstName'),
                                "lastName": settings.get('PASSAGER', 'lastName'),
                                "documentID": settings.get('PASSAGER', 'documentID'),
                                "birthday": settings.get('PASSAGER', 'birthday'),
                                "email": settings.get('PASSAGER', 'email'),
                                "title": settings.get('PASSAGER', 'title'),
                                }, "currency": settings.get('PAYMENT', 'currency'), "booking_token": flights_manager.flights[0].booking_token}

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    post_request = requests.post("http://37.139.6.125:8080/booking", data=json.dumps(data_json), headers=headers)
    print(post_request.json()["pnr"])
