from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from credentials import MONGOLAB_URL
import csv
from recordsearch_tools.utilities import convert_date_to_iso

def write_csv(function=None):
    dbclient = MongoClient(MONGOLAB_URL)
    db = dbclient.get_default_database()
    if function:
        query = {'function': function}
    else:
        query = {}
    functions = db.functions.find(query)
    for func in functions:
        filename = 'data/{}.csv'.format(func['function'].lower())
        with open(filename, 'wb') as functions_file:
            functions_csv = csv.writer(functions_file)
            functions_csv.writerow([
                'agency_id',
                'agency_title',
                'agency_start',
                'agency_end',
                'function_start',
                'function_end'
                ])
            for agency in func['agencies']:
                functions_csv.writerow([
                    agency['agency_id'],
                    agency['title'],
                    convert_date_to_iso(agency['start_date']),
                    convert_date_to_iso(agency['end_date']),
                    convert_date_to_iso(agency['function_start']),
                    convert_date_to_iso(agency['function_end'])
                    ])

