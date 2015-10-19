#!/usr/bin/env python
from flask import Flask, jsonify, request

import miami

app = Flask(__name__)


@app.route('/schedules/<course_codes>')
def get_schedules(course_codes):
	course_codes = course_codes.split(',')
	courses = miami.load_courses(course_codes)
	possible = miami.possible_schedules(courses)
	json_data = miami.generate_schedule_json(possible)

	return jsonify({
		'schedules': json_data,
		'num_schedules': len(json_data),
	})

if __name__ == '__main__':
	app.debug = True
	app.run()
