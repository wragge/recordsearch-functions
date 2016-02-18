# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from credentials import MONGOLAB_URL
import csv
from recordsearch_tools.utilities import convert_date_to_iso
from operator import itemgetter
import plotly.plotly as py
import plotly.graph_objs as go
import datetime


def calculate_status_totals(function):
    '''Aggregate agencies by agency status and count.'''
    dbclient = MongoClient(MONGOLAB_URL)
    db = dbclient.get_default_database()
    pipeline = [
        {"$match": {"function": function}},
        {"$unwind": "$agencies"},
        {"$group": {"_id": "$agencies.agency_status", "total": {"$sum": 1}}},
        {"$project": {"_id": 0, "agency_status": "$_id", "total": "$total"}},
        {"$sort": {"total": -1}}
    ]
    return list(db.functions.aggregate(pipeline))

def get_agencies(function, status):
    dbclient = MongoClient(MONGOLAB_URL)
    db = dbclient.get_default_database()
    pipeline = [
        {"$match": {"function": function}},
        {"$unwind": "$agencies"},
        {"$match": {"agencies.agency_status": status}},
        {"$group" : {"_id" : "$_id", "agencies" : {"$addToSet" : "$agencies" } }}
    ]
    agencies = list(db.functions.aggregate(pipeline))[0]['agencies']
    return sorted(agencies, key=itemgetter('function_start'))


def plot_agencies(function, status):
    agencies = get_agencies(function=function, status=status)
    traces = []
    annotations = []
    agency_legend = False
    function_legend = False
    showlegend = False
    for index, agency in enumerate(agencies, start=1):
        if index == 1:
            function_legend = True
        else:
            function_legend = False
        if not agency['function_end']['date']:
            agency['function_end']['date'] = datetime.datetime.now()
        if not agency['end_date']['date']:
            agency['end_date']['date'] = datetime.datetime.now()
        if agency['start_date']['date'] and (agency['start_date']['date'] < agency['function_start']['date']):
            if agency_legend is False:
                showlegend = True
                agency_legend = True
            else:
                showlegend = False
            traces.append(
                dict(
                    x=[agency['start_date']['date'], agency['function_start']['date']],
                    y=[index, index],
                    type='scatter',
                    name='Agency dates',
                    text='{}: {}'.format(agency['agency_id'], agency['title']),
                    mode='lines',
                    hoverinfo='x+text',
                    showlegend=showlegend,
                    legendgroup='agency',
                    line=dict(
                        color=('rgb(214, 214, 214)'),
                        width=12
                    )
                )
            )
        traces.append(
            dict(
                x = [agency['function_start']['date'], agency['function_end']['date']],
                y = [index, index],
                type='scatter',
                name = 'Function dates',
                text = '{}: {}'.format(agency['agency_id'], agency['title'].replace(u'\u2013', '-')),
                mode = 'lines',
                hoverinfo='x+text',
                showlegend=function_legend,
                legendgroup='function',
                line = dict(
                    color = ('rgb(124, 205, 124)'),
                    width = 12
                )
            )
        )
        annotations.append(
            dict(
                x=agency['function_start']['date'],
                y=index,
                yanchor='middle',
                xanchor='right',
                xref='x',
                yref='y',
                text='<a href="http://www.naa.gov.au/cgi-bin/Search?Number={}">{}</a>'.format(agency['agency_id'], agency['agency_id']),
                showarrow=False,
                opacity=1,
                font = dict(
                    size=10
                )
            )
        )
        if agency['end_date']['date'] < agency['function_end']['date']:
            if agency_legend == False:
                showlegend = True
                agency_legend = True
            else:
                showlegend = False
            traces.append(
                dict(
                    x = [agency['function_end']['date'], agency['end_date']['date']],
                    y = [index, index],
                    type='scatter',
                    name = 'Agency dates',
                    text = '{}: {}'.format(agency['agency_id'], agency['title'].replace(u'\u2013', '-')),
                    mode = 'lines',
                    showlegend=showlegend,
                    legendgroup='agency',
                    hoverinfo='x+text',
                    line = dict(
                        color = ('rgb(214, 214, 214)'),
                        width = 12
                    )
                )
            )
    layout = go.Layout(
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=False,
        ),
        xaxis=dict(
            hoverformat='%-d %b %Y'
        ),
        legend=dict(
            x=0.1,
            y=1
        ),
        height=800,
        width=1000,
        autosize=True,
        showlegend=True,
        hovermode='closest',
        annotations=annotations,
        title = 'Commonwealth agencies ({}) associated with the function \'{}\''.format(status, function)
    )
    fig = dict(data=traces, layout=layout)
    py.plot(fig, filename='agencies-{}-{}-{}'.format(function.lower().replace(' ', '_'), status.lower().replace(' ', '_'), datetime.date.today().isoformat()), validate=False)


def write_csv(function=None):
    dbclient = MongoClient(MONGOLAB_URL)
    db = dbclient.get_default_database()
    if function:
        query = {'function': function}
    else:
        query = {}
    functions = db.functions.find(query)
    for func in functions:
        filename = 'data/{}.csv'.format(func['function'].lower().replace(' ', '_'))
        with open(filename, 'wb') as functions_file:
            functions_csv = csv.writer(functions_file)
            functions_csv.writerow([
                'agency_id',
                'agency_title',
                'agency_status',
                'location',
                'agency_start',
                'agency_end',
                'function_start',
                'function_end'
                ])
            for agency in func['agencies']:
                functions_csv.writerow([
                    agency['agency_id'],
                    agency['title'].replace(u'\u2013', '-'),
                    agency['agency_status'],
                    agency['location'],
                    convert_date_to_iso(agency['start_date']),
                    convert_date_to_iso(agency['end_date']),
                    convert_date_to_iso(agency['function_start']),
                    convert_date_to_iso(agency['function_end'])
                    ])


def write_agency_csv(function, agency):
    dbclient = MongoClient(MONGOLAB_URL)
    db = dbclient.get_default_database()
    func = db.functions.find_one({'function': function})
    for ag in func['agencies']:
        if ag['agency_id'] == agency:
            filename = 'data/{}-{}-{}-{}.csv'.format(func['function'].lower().replace(' ', '_'), agency.replace(' ', '_'), convert_date_to_iso(ag['function_start']), convert_date_to_iso(ag['function_end']))
            with open(filename, 'wb') as agency_file:
                agency_csv = csv.writer(agency_file)
                agency_csv.writerow([
                    'series_id',
                    'series_title',
                    'number_described',
                    'number_digitised'
                ])
                for series in ag['series']:
                    agency_csv.writerow([
                        series['series_id'],
                        series['title'],
                        series['items_described_in_period'],
                        series['items_digitised_in_period']
                    ])


def summarise_agency(function, agency):
    dbclient = MongoClient(MONGOLAB_URL)
    db = dbclient.get_default_database()
    func = db.functions.find_one({'function': function})
    for ag in func['agencies']:
        if ag['agency_id'] == agency:
            agency_title = ag['title']
            function_start = convert_date_to_iso(ag['function_start'])
            function_end = convert_date_to_iso(ag['function_end'])
            total_series = len(ag['series'])
            total_described = 0
            total_digitised = 0
            total_undescribed = 0
            quantity_undescribed = 0
            quantity_described = 0
            for series in ag['series']:
                total_described += series['items_described_in_period']
                total_digitised += series['items_digitised_in_period']
                se = db.series.find_one({'identifier': series['series_id']})
                quantity = 0
                if 'locations' in se:
                    for location in se['locations']:
                        if 'quantity' in location:
                            quantity += location['quantity']
                if series['items_described'] == 0:
                    total_undescribed += 1
                    quantity_undescribed += quantity
                else:
                    quantity_described += quantity
    print 'Agency: {}, {}'.format(agency, agency_title)
    print 'Function: {} from {} to {}'.format(function, function_start, function_end)
    print 'Total series: {}'.format(total_series)
    print 'Items described: {}'.format(total_described)
    print 'Items digitised: {} ({:.2f}%)'.format(total_digitised, (float(total_digitised)/total_described)*100)
    print 'Series with no items described: {} ({:.2f}%)'.format(total_undescribed, (float(total_undescribed)/total_series)*100)
    print 'Quantity undescribed: at least {} of {} metres ({:.2f}%)'.format(quantity_undescribed, quantity_described, (float(quantity_undescribed)/quantity_described)*100)
