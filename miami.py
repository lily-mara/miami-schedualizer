#!/usr/bin/env python3
from datetime import datetime
from xml.etree import ElementTree
import re

import requests
import grequests

from combinatorics import explode_combos

URL = 'https://ws.muohio.edu'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'


def _parse_date(date_string):
	return datetime.strptime(date_string, DATE_FORMAT).date()


def _parse_time(time_string):
	return datetime.strptime(time_string, TIME_FORMAT).time()


def main():
	courses = load_courses(['CSE385', 'CSE262', 'CSE464', 'CSE465', 'THE123'])

	for x in possible_schedules(courses):
		print(x, schedule_is_valid(x))


def load_courses(course_codes):
	req = []

	for i in course_codes:
		t = course_code_to_tuple(i)
		req.append({
			'courseSubjectCode': t[0],
			'courseNumber': t[1],
			'campusCode': 'O'
		})

	return Course.fetch_courses('201620', req)


def generate_schedule_json(schedules):
	sched = []
	for schedule in schedules:
		s = []
		for course in schedule:
			for course_schedule in course.courseSchedules:
				s.append({
					'days': [i for i in course_schedule.days],
					'courseId': course.courseId,
					'startDate': course_schedule.startDate,
					'endDate': course_schedule.endDate,
					'startTime': course_schedule.startTime,
					'endTime': course_schedule.endTime,
					'courseCode': course.courseCode,
					'instructors': [i.nameDisplayInformal for i in
						course.instructors],
				})

		sched.append(s)

	return sched


def possible_schedules(courses):
	return [i for i in explode_combos(courses) if schedule_is_valid(i)]


def schedule_is_valid(schedule):
	for course_i in schedule:
		for course_j in [i for i in schedule if i != course_i]:
			if course_i.conflicts_with(course_j):
				return False

	return True


def course_code_to_tuple(course_code):
	if course_code[3] == '-':
		return (course_code[:3], course_code[4:])
	return (course_code[:3], course_code[3:])


class CourseSchedule(object):
	startDate = None
	endDate = None
	startTime = None
	endTime = None
	room = None
	buildingCode = None
	buildingName = None
	days = None
	scheduleTypeCode = None
	scheduleTypeDescription = None

	def __init__(self, data):
		self.__dict__.update(data)

	def _parse_dates(self):
		self.startDate = _parse_date(self.startDate)
		self.endDate = _parse_date(self.endDate)

	def _parse_times(self):
		self.startTime = _parse_time(self.startTime)
		self.endTime = _parse_time(self.endTime)

	def conflicts_with(self, other):
		"""
		Returns True if this schedule conflicts with the other schedule. I.E. Both
		of the two schedules occur at the same time.

		>>> x = {'startTime': '10:00', 'endTime': '11:00', 'days': 'M'}
		>>> A = CourseSchedule(x)
		>>> B = Course(x) # B has exactly the same schedule as A, so they conflict
		>>> A.conflicts_with(B)
		True

		>>> y = {'startTime': '10:00', 'endTime': '11:00', 'days': 'T'}
		>>> C = Course(y) # C occurs on Tuesday, not Monday, so there is no conflict
		>>> A.conflicts_with(B)
		False
		"""

		days = set(self.days + other.days)
		if len(days) == len(self.days + other.days):
			# If the two schedules don't happen on the same days, then there is
			# absolutely no risk of them conflicting with each other. I.E. if A
			# is only Mondays and B is only Wednesdays, there is no conflict.
			return False

		if self.endDate < other.startDate or other.endDate < self.startDate:
			# If the two schedules don't happen at the same time of the year,
			# then there is no risk of conflict. I.E. if A lasts the month of
			# January, and B lasts the month of August, there is no conflict.
			return False

		# At this point, the schedules are garunteed to occur on the same days,
		# so we don't need to worry about the days of the week, just the time
		# that it occurs.
		start_conflict_1 = self.startTime < other.endTime
		end_conflict_1 = self.endTime > other.startTime
		conflict_1 = start_conflict_1 and end_conflict_1

		start_conflict_2 = other.startTime < self.endTime
		end_conflict_2 = other.endTime > self.startTime
		conflict_2 = start_conflict_2 and end_conflict_2

		if conflict_1 or conflict_2:
			# If self starts before other ends and ends after other starts
			# self         |-----------|
			# other   |---------|
			#
			# Or other starts before self ends and ends after self starts
			# self       |---------|
			# other            |--------|
			#
			# There is a conflict.
			return True
		return False


class Instructor(object):
	username = None
	nameLast = None
	nameFirst = None
	nameMiddle = None
	namePrefix = None
	nameSuffix = None
	nameFirstPreferred = None
	nameDisplayInformal = None
	nameDisplayFormal = None
	nameSortedInformal = None
	nameSortedFormal = None
	personResource = None
	primaryInstructor = None

	def __init__(self, data):
		self.__dict__.update(data)

		self.primaryInstructor = self.primaryInstructor == 'true'

	def __str__(self):
		return self.nameSortedFormal

	def __repr__(self):
		return '<Instructor: {}>'.format(self.nameSortedFormal)


class AcademicTerm(object):
	termId = None
	name = None
	startDate = None
	endDate = None
	displayTerm = None
	academicTermResource = None

	def __init__(self, data):
		self.termId = data.find('termId').text
		self.name = data.find('name').text
		self.startDate = data.find('startDate').text
		self.endDate = data.find('endDate').text
		self.displayTerm = data.find('displayTerm').text
		self.academicTermResource = data.find('academicTermResource').text

		self._parse_dates()

	def __repr__(self):
		return '<AcademicTerm: {}>'.format(self.termId)

	def _parse_dates(self):
		self.startDate = _parse_date(self.startDate)
		self.endDate = _parse_date(self.endDate)

	@staticmethod
	def _fetch_terms(extra_text=''):
		url = '{}/academicTerms{}'.format(URL, extra_text)
		term_xml = ElementTree.fromstring(requests.get(url).text)

		return [AcademicTerm(i) for i in term_xml.getchildren()]

	@staticmethod
	def _fetch_term(extra_text=''):
		url = '{}/academicTerms{}'.format(URL, extra_text)
		term_xml = ElementTree.fromstring(requests.get(url).text)

		return AcademicTerm(term_xml)

	@staticmethod
	def all_terms():
		return AcademicTerm._fetch_terms()

	@staticmethod
	def current_term():
		return AcademicTerm._fetch_term('/current')

	@staticmethod
	def next_term():
		return AcademicTerm._fetch_term('/next')

	@staticmethod
	def previous_term():
		return AcademicTerm._fetch_term('/previous')

	@staticmethod
	def term_from_id(term_id):
		return AcademicTerm._fetch_term('/' + term_id)

	@staticmethod
	def next_n_terms(n):
		terms = sorted(AcademicTerm._fetch_terms(), key=lambda x: x.termId)
		terms_to_return = [x for x in terms if x.startDate > datetime.today().date()][:n]

		return terms_to_return


class Course(object):
	academicTerm = None
	academicTermDesc = None
	courseId = None
	recordNumber = None
	courseCode = None
	schoolCode = None
	schoolName = None
	deptName = None
	courseTitle = None
	instructionalType = None
	instructionalTypeDescription = None
	courseSubjectCode = None
	courseSubjectDesc = None
	courseNumber = None
	courseSectionCode = None
	campusCode = None
	campusName = None
	creditHoursDesc = None
	creditHoursHigh = None
	creditHoursLow = None
	enrollmentCountMax = None
	enrollmentCountCurrent = None
	enrollmentCountAvailable = None
	partOfTermCode = None
	partOfTermName = None
	partOfTermStartDate = None
	partOfTermEndDate = None
	midtermGradeSubmissionAvailable = None
	finalGradeSubmissionAvailable = None
	gradeRequiredFinal = None
	prntInd = None
	courseSchedules = []
	instructors = []
	attributes = []
	crossListedCourses = []
	courseSectionResource = None
	enrollmentResource = None
	academicTermResource = None

	def __init__(self, data):
		self.__dict__.update(data)

		self._parse_instructors()
		self._parse_truthy_fields()
		self._parse_dates()
		self._parse_number_fields()

		sched = []
		for i in self.courseSchedules:
			sched.append(CourseSchedule(i))

		self.courseSchedules = sched

	def _parse_dates(self):
		self.partOfTermStartDate = _parse_date(self.partOfTermStartDate)
		self.partOfTermEndDate = _parse_date(self.partOfTermEndDate)

	def _parse_truthy_fields(self):
		m = self.midtermGradeSubmissionAvailable == 'Y'
		self.midtermGradeSubmissionAvailable = m

		f = self.finalGradeSubmissionAvailable == 'Y'
		self.finalGradeSubmissionAvailable = f

		self.gradeRequiredFinal = self.gradeRequiredFinal == 'true'

	def _parse_instructors(self):
		instructors = []

		for i in self.instructors:
			instructors.append(Instructor(i))

		self.instructors = instructors

	def _parse_number_fields(self):
		self._parse_number_field('creditHoursDesc')
		self._parse_number_field('creditHoursHigh')
		self._parse_number_field('creditHoursLow')
		self._parse_number_field('enrollmentCountMax')
		self._parse_number_field('enrollmentCountCurrent')
		self._parse_number_field('enrollmentCountAvailable')
		self._parse_number_field('courseId')

	def _parse_number_field(self, fieldname):
		x = self.__dict__[fieldname]
		try:
			x = int(x)
		except ValueError:
			try:
				x = float(x)
			except ValueError:
				m = re.search(r'(\d+) - (\d+)', x)
				x = (m.group(1), m.group(2))

		self.__dict__[fieldname] = x

	def __repr__(self):
		return '<Course: {}>'.format(self.courseCode)

	def __eq__(self, other):
		return self.courseId == other.courseId

	def conflicts_with(self, other_course):
		"""
		Returns True if this course conflicts with the other course. I.E. Both
		of the two courses meet at the same time.

		>>> x = {'courseSchedules': []}
		>>> x['courseSchedules'].append({'startTime': '10:00', 'endTime': '11:00'})
		>>> x['courseSchedules'][0]['days'] = 'M'
		>>> A = Course(x)
		>>> B = Course(x) # B has exactly the same schedule as A, so they conflict
		>>> A.conflicts_with(B)
		True

		>>> y = {'courseSchedules': []}
		>>> y['courseSchedules'].append({'startTime': '10:00', 'endTime': '11:00'})
		>>> y['courseSchedules'][0]['days'] = 'T'
		>>> C = Course(y) # C is different from A because it is on Tuesdays.
		>>> A.conflicts_with(C)
		False
		"""
		return any(i.conflicts_with(j) for j in self.courseSchedules for i in
			other_course.courseSchedules)

	@staticmethod
	def fetch_courses(academic_term, params=None):
		if params is None:
			params = [{}]

		if type(params) == dict:
			params = []

		if type(academic_term) == AcademicTerm:
			academic_term = academic_term.termId

		req = []
		for p in params:
			url = '{}/courseSectionV2/{}.json'.format(URL, academic_term)
			req.append(grequests.get(url, params=p))

		res = grequests.map(req)
		courses = []
		for i in res:
			courses.append([Course(j) for j in i.json()['courseSections']])

		return courses

if __name__ == '__main__':
	main()
