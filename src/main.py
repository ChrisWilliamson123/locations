from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import Flask, redirect, render_template, request, url_for
from math import sin, cos, sqrt, atan2, radians
import os, dateutil.parser, sys
from settings import APP_STATIC
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'src/media/kml_files'
ALLOWED_EXTENSIONS = set(['kml'])

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'secret!'
app.coord_index = 0
socketio = SocketIO(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        request_copy = request
        print(request.files)
        print('here')
        print(len(request.files))
        print(request.files)
        if 'locationsUpload' not in request.files:
            print('File not in request')
            return redirect(request.url)
        file = request.files['locationsUpload']

        if file.filename == '':
            print('No filename')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            contents = file.read()
            print('Sending data read message to ')
            socketio.emit('data read')


            # return redirect(url_for('hello_world', filename=filename))
    # locations = open(os.path.join(APP_STATIC, 'holiday.kml'))
    # soup = BeautifulSoup(locations, 'xml')
    # print('Loaded file into soup...')

    # app.full_data = process_coords(soup)

    return render_template('index.html')

# @app.route('/map', methods)

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

@socketio.on('location filename', namespace='/test')
def save_filename(filename):
    app.locations_filename = filename
    print('Saved filename: ' + filename)

@socketio.on('location raw data', namespace='/test')
def save_location_data(data):
    app.location_data = data
    print('Saved location data')

if __name__ == '__main__':
    socketio.run(app)