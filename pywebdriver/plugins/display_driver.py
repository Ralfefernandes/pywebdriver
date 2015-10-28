# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2014-2015 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

meta = {
    'name': "POS Display",
    'description': """This plugin add the support of customer display for your
        pywebdriver""",
    'require_pip': ['pyposdisplay'],
    'require_debian': ['python-pyposdisplay'],
}

from pywebdriver import app, config, drivers
from flask_cors import cross_origin
from flask import request, jsonify, render_template
from base_driver import ThreadDriver, check
import simplejson
import time

try:
    import pyposdisplay
except:
    installed=False
else:
    AUTHOR = [
        ([u'PyWebDriver', u'By'], 2),
        ([u'Sylvain CALADOR', u'@ Akretion'], 1.5),
        ([u'Sébastien BEAU', u'@ Akretion'], 1.5),
        ([u'Sylvain LE GAL', u'@ GRAP'], 1.5),
        ([u'Status:', u'OK'], 5),
    ]
    installed=True
    class DisplayDriver(ThreadDriver, pyposdisplay.Driver):
        """ Display Driver class for pywebdriver """

        def __init__(self, *args, **kwargs):
            ThreadDriver.__init__(self)
            pyposdisplay.Driver.__init__(self, *args, **kwargs)
            # TODO FIXME (Actually hardcoded, but no possibility to know
            # the model easily
            self.vendor_product = '1504_11'

        @app.route('/display_status.html', methods=['GET'])
        @cross_origin()
        def display_status_http():
            for line, duration in AUTHOR:
                display_driver.push_task('send_text', line)
                time.sleep(duration)
            return render_template('display_status.html')

        def get_status(self):
            try:
                self.set_status('connected')
                # When I use the POS, it regularly displays
                # "PyWebDriver / PosBox Status" on the LCD !!!
                # So I comment this line -- Alexis de Lattre
                # display_driver.push_task('send_text', [_(u'PyWebDriver'), _(u'PosBox Status')])
            except Exception as e:
                pass
                # TODO Improve Me
                # For the time being, it's not possible to know if the display
                # is 'disconnected' in 'error' state
                # Maybe could be possible, improving pyposdisplay library.
            return self.status

    driver_config = {}
    if config.get('display_driver', 'device_name'):
        driver_config['customer_display_device_name'] =\
            config.get('display_driver', 'device_name')
    if config.getint('display_driver', 'device_rate'):
        driver_config['customer_display_device_rate'] =\
            config.getint('display_driver', 'device_rate')
    if config.getint('display_driver', 'device_timeout'):
        driver_config['customer_display_device_timeout'] =\
            config.getint('display_driver', 'device_timeout')

    display_driver = DisplayDriver(driver_config)
    drivers['display_driver'] = display_driver

@app.route(
    '/hw_proxy/send_text_customer_display',
    methods=['POST', 'GET', 'PUT', 'OPTIONS'])
@cross_origin(headers=['Content-Type'])
@check(installed, meta)
def send_text_customer_display():
    app.logger.debug('LCD: Call send_text')
    text_to_display = request.json['params']['text_to_display']
    lines = simplejson.loads(text_to_display)
    app.logger.debug('LCD: lines=%s', lines)
    display_driver.push_task('send_text', lines)
    return jsonify(jsonrpc='2.0', result=True)
