from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import Flask, redirect, render_template, request
from math import sin, cos, sqrt, atan2, radians
import os, dateutil.parser, sys
from settings import APP_STATIC
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret!'
app.coord_index = 0
socketio = SocketIO(app)

def coord_distance(coord1, coord2):

    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(float(coord1[0]))
    lon1 = radians(float(coord1[1]))
    lat2 = radians(float(coord2[0]))
    lon2 = radians(float(coord2[1]))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c * 1000

    return distance


def process_coords(soup):
    co_ord_data = {}

    for datetime in list(reversed(soup.find_all('when'))):
        co_ord_split = datetime.findNext('gx:coord').string.split(' ')
        co_ord = (co_ord_split[1], co_ord_split[0])

        date_split = datetime.string.split('T')
        date = date_split[0]
        time = "%s at %s" % (date, date_split[1][0:-4])

        if date in co_ord_data:
            latest_coord = co_ord_data[date][-1][1]
            difference = coord_distance(co_ord, latest_coord)
            if difference > 100:
                co_ord_data[date].append((time, co_ord))
        else:
            co_ord_data[date] = [(time, co_ord)]
    return co_ord_data


@app.route('/')
def hello_world():
    # socketio.run(app)
    locations = open(os.path.join(APP_STATIC, 'holiday.kml'))
    soup = BeautifulSoup(locations, 'xml')
    print('Loaded file into soup...')

    app.full_data = process_coords(soup)

    # print(data)


    # print(times)
    # print('Gathered coords...')
    # app.real_coords = []
    # app.real_times = []
    # print('Converting coords...')
    # for i in range(0, len(coords)):
    #     c = coords[i]
    #     d = dateutil.parser.parse(times[i].contents[0])
    #     d = d.strftime('%d/%m/%Y %H:%M')
    #     app.real_times.append(d)
    #     split = c.contents[0].split(' ')
    #     this_coord = (float(split[1]), float(split[0]))
    #     if i == 0:
    #         app.real_coords.append(this_coord)
    #     else:
    #         if app.real_coords[-1] != this_coord:
    #             app.real_coords.append((split[1], split[0]))
    # print(len(app.real_coords))
    return render_template('index.html')

@socketio.on('data request', namespace='/test')
def test_message():
    # print(l)
    emit('data response', [
        app.current_data[app.coord_index:app.coord_index+2],
        app.current_data[app.coord_index+1]
    ])
    app.coord_index += 1
    # print('here')

@socketio.on('start', namespace='/test')
def start_map(dates):
    start_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
    end_date = datetime.strptime(dates[1], "%Y-%m-%d").date()

    app.current_data = []
    while start_date <= end_date:
        for data in app.full_data[start_date.strftime('%Y-%m-%d')]:
            app.current_data.append(data)
        start_date += timedelta(days=1)

    emit('data ready', app.current_data)

if __name__ == '__main__':
    socketio.run(app)