#!/usr/bin/python3

from flask import Flask, request
from relaycontroller import RelayController, RelayMode
from database import Database
import traceback
import sys


# Create Flask app object to handle REST calls
app = Flask('perilex-controller')
relay_controller = RelayController()
db = Database()

mode_min = 0
mode_max = 3


@app.route('/api/mode-off', methods=['POST'])
def mode_off(tag_source='direct'):
    if mode_min <= 0 <= mode_max:
        relay_controller.mode_off()
        db.write(mode=RelayMode.OFF, tag_source=tag_source)
        return '', 200
    else:
        return '', 403


@app.route('/api/mode-1', methods=['POST'])
def mode_1(tag_source='direct'):
    if mode_min <= 1 <= mode_max:
        relay_controller.mode_1()
        db.write(mode=RelayMode.ONE, tag_source=tag_source)
        return '', 200
    else:
        return '', 403


@app.route('/api/mode-2', methods=['POST'])
def mode_2(tag_source='direct'):
    if mode_min <= 2 <= mode_max:
        relay_controller.mode_2()
        db.write(mode=RelayMode.TWO, tag_source=tag_source)
        return '', 200
    else:
        return '', 403


@app.route('/api/mode-3', methods=['POST'])
def mode_3(tag_source='direct'):
    if mode_min <= 3 <= mode_max:
        relay_controller.mode_3()
        db.write(mode=RelayMode.THREE, tag_source=tag_source)
        return '', 200
    else:
        return '', 403


@app.route('/api/mode', methods=['GET'])
def mode():
    return str(relay_controller.mode), 200


def switch_to_mode(new_mode, tag_source):
    if new_mode == 0:
        mode_off(tag_source)
    elif new_mode == 1:
        mode_1(tag_source)
    elif new_mode == 2:
        mode_2(tag_source)
    elif new_mode == 3:
        mode_3(tag_source)
    else:
        return 'Error 1', 500
    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    global mode_min
    global mode_max
    tag_source = 'manual'
    # If the form is filled in, go to the chosen mode.
    if request is not None and request.form is not None:
        if 'mode' in request.form:
            try:
                new_mode = int(request.form['mode'][-1:])
                if mode_min <= new_mode <= mode_max:
                    result = switch_to_mode(new_mode, tag_source)
                    if result is not None:
                        return result
            except:
                #exc_type, exc_value, exc_traceback = sys.exc_info()
                #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                return 'Error 2', 500
        if 'mode_min' in request.form:
            new_mode_min = int(request.form['mode_min'][-1:])
            if new_mode_min <= mode_max:
                mode_min = new_mode_min
                if int(relay_controller.mode) < mode_min:
                    result = switch_to_mode(mode_min, tag_source)
                    if result is not None:
                        return result
        if 'mode_max' in request.form:
            new_mode_max = int(request.form['mode_max'][-1:])
            if new_mode_max >= mode_min:
                mode_max = new_mode_max
                if int(relay_controller.mode) > mode_max:
                    result = switch_to_mode(mode_max, tag_source)
                    if result is not None:
                        return result

    # Return HTML page.
    page = '<html><head>' \
           '<title>Ventilatie prinsenhuis</title>' \
           '<meta name="viewport" content ="width=device-width,initial-scale=1.5,user-scalable=yes" />' \
           '</head><body>' \
           '<h3>Ventilatie prinsenhuis</h3>' \
           '<h3>Huidige stand: {}</h3><br>' \
           '<form action="/" target="_self" method="post">' \
           '<input type="submit" name="mode" value="Mode 0" {}><br><br>' \
           '<input type="submit" name="mode" value="Mode 1" {}><br><br>' \
           '<input type="submit" name="mode" value="Mode 2" {}><br><br>' \
           '<input type="submit" name="mode" value="Mode 3" {}><br><br>' \
           '</form>' \
           '<h3>Minimale stand: {}</h3><br>' \
           '<form action="/" target="_self" method="post">' \
           '<input type="submit" name="mode_min" value="Mode 0" {}><br><br>' \
           '<input type="submit" name="mode_min" value="Mode 1" {}><br><br>' \
           '<input type="submit" name="mode_min" value="Mode 2" {}><br><br>' \
           '<input type="submit" name="mode_min" value="Mode 3" {}><br><br>' \
           '</form>' \
           '<h3>Maximale stand: {}</h3><br>' \
           '<form action="/" target="_self" method="post">' \
           '<input type="submit" name="mode_max" value="Mode 0" {}><br><br>' \
           '<input type="submit" name="mode_max" value="Mode 1" {}><br><br>' \
           '<input type="submit" name="mode_max" value="Mode 2" {}><br><br>' \
           '<input type="submit" name="mode_max" value="Mode 3" {}><br><br>' \
           '</form>' \
           '</body></html>'
    page = page.format(int(relay_controller.mode), '', '', '', '', mode_min, '', '', '', '', mode_max, '', '', '', '')
    # page = page.format(int(relay_controller.mode),
    #                    'disabled' if int(relay_controller.mode) == 0 else '',
    #                    'disabled' if int(relay_controller.mode) == 1 else '',
    #                    'disabled' if int(relay_controller.mode) == 2 else '',
    #                    'disabled' if int(relay_controller.mode) == 3 else '')
    return page, 200


@app.route('/api/close', methods=['POST'])
def close():
    relay_controller.close()
    return 'Closed', 200


if __name__ == '__main__':
    # Start the API.
    app.run(host="0.0.0.0", port=8080, threaded=True)
