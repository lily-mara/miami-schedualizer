#!/usr/bin/env python
import os

from flask import Flask, jsonify, request
from flask.ext.cors import CORS

import miami

app = Flask(__name__)

DEBUG = os.environ.get('MIAMI_DEBUG', 'false').lower() == 'true'
app.debug = DEBUG

if DEBUG:
	cors = CORS(app, resources={r".*": {"origins": "localhost:.*"}})
	app.logger.debug('Running application in debug mode')
else:
	app.logger.debug('Running application in production mode')


@app.route('/schedules', methods=['POST'])
def get_schedules_post():
	course_codes = request.get_json()['courseCodes']
	return get_schedules(course_codes)


@app.route('/schedules/<course_codes>')
def get_schedules_get(course_codes):
	course_codes = course_codes.split(',')
	return get_schedules(course_codes)


def get_schedules(course_codes):
	courses = miami.load_courses(course_codes)
	possible = miami.possible_schedules(courses)
	json_data = miami.generate_schedule_json(possible)

	return jsonify({
		'schedules': json_data,
		'num_schedules': len(json_data),
	})

if __name__ == '__main__':
	app.run()
