import argparse, requests, csv

parser = argparse.ArgumentParser(description='Update IATAcodes database')
parser.add_argument('--api_key', help='Your iatacodes API key')

args = parser.parse_args()

airports_request = requests.get(
    'https://iatacodes.org/api/v6/airports?api_key={api_key}'.format(api_key=args.api_key))
airports_codes = []
for airport in airports_request.json()["response"]:
    airports_codes.append(airport["code"])

with open("./iatacodes.csv", 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(airports_codes)