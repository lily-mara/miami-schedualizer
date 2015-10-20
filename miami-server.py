#!/usr/bin/env python
import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask.ext.cors import CORS

import miami

app = Flask(__name__)

DEBUG = os.environ.get('MIAMI_DEBUG', 'false').lower() == 'true'
app.debug = DEBUG

if DEBUG:
	cors = CORS(app, resources={r".*": {"origins": "localhost:.*"}})
	app.logger.info('Running application in debug mode')
else:
	app.logger.info('Running application in production mode')


@app.route('/schedules', methods=['POST'])
def get_schedules_post():
	course_codes = request.get_json()['courseCodes']
	return get_schedules(course_codes)


@app.route('/schedules/<course_codes>')
def get_schedules_get(course_codes):
	course_codes = course_codes.split(',')
	return get_schedules(course_codes)


def get_schedules(course_codes):
	app.logger.debug('Fetching courses for codes ' + str(course_codes))

	start_time = datetime.now()
	courses = miami.load_courses(course_codes)
	end_time = datetime.now()

	app.logger.debug('Found {} courses for codes {} in {}'
		.format(sum(len(i) for i in courses), course_codes, end_time - start_time))

	possible = miami.possible_schedules(courses)
	app.logger.debug('Found {} possible schedules for codes {}'
		.format(len(possible), course_codes))

	json_data = miami.generate_schedule_json(possible)

	return jsonify({
		'schedules': json_data,
	})

if __name__ == '__main__':
	app.run()
