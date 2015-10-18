#!/usr/bin/env python
from unittest import TestCase, main

from miami import CourseSchedule

BASE_SCHEDULE = {
	'days': 'M',
	'startDate': '2015-10-01',
	'endDate': '2015-11-01',
	'startTime': '10:00',
	'endTime': '11:00',
}


class TestScheduleConflicts(TestCase):
	def test_no_conflict_at_all(self):
		x = dict(BASE_SCHEDULE)
		y = dict(BASE_SCHEDULE)

		y['days'] = 'T'
		y['startDate'] = '2015-06-01'
		y['endDate'] = '2016-07-01'
		y['startTime'] = '13:00'
		y['endTime'] = '14:00'

		X = CourseSchedule(x)
		Y = CourseSchedule(y)

		self.assertFalse(X.conflicts_with(Y))

	def test_same_schedule_has_conflict(self):
		X = CourseSchedule(BASE_SCHEDULE)

		self.assertTrue(X.conflicts_with(X))

	def test_no_conflict_days(self):
		x = dict(BASE_SCHEDULE)
		y = dict(BASE_SCHEDULE)

		y['days'] = 'T'

		X = CourseSchedule(x)
		Y = CourseSchedule(y)

		self.assertFalse(X.conflicts_with(Y))

	def test_no_conflict_touching_dates(self):
		x = dict(BASE_SCHEDULE)
		y = dict(BASE_SCHEDULE)

		y['startDate'] = '2015-11-02'
		y['endDate'] = '2015-12-01'

		X = CourseSchedule(x)
		Y = CourseSchedule(y)

		self.assertFalse(X.conflicts_with(Y))

	def test_no_conflict_separated_dates(self):
		x = dict(BASE_SCHEDULE)
		y = dict(BASE_SCHEDULE)

		y['startDate'] = '2015-06-01'
		y['endDate'] = '2015-07-01'

		X = CourseSchedule(x)
		Y = CourseSchedule(y)

		self.assertFalse(X.conflicts_with(Y))

	def test_no_conflict_separated_times(self):
		x = dict(BASE_SCHEDULE)
		y = dict(BASE_SCHEDULE)

		y['startTime'] = '12:00'
		y['endTime'] = '13:00'

		X = CourseSchedule(x)
		Y = CourseSchedule(y)

		self.assertFalse(X.conflicts_with(Y))

	def test_no_conflict_touching_times(self):
		x = dict(BASE_SCHEDULE)
		y = dict(BASE_SCHEDULE)

		y['startTime'] = '11:00'
		y['endTime'] = '12:00'

		X = CourseSchedule(x)
		Y = CourseSchedule(y)

		self.assertFalse(X.conflicts_with(Y))

	def test_conflict_self_starts_first(self):
		x = dict(BASE_SCHEDULE)
		y = dict(BASE_SCHEDULE)

		y['startTime'] = '10:30'
		y['endTime'] = '12:00'

		X = CourseSchedule(x)
		Y = CourseSchedule(y)

		self.assertTrue(X.conflicts_with(Y))

	def test_conflict_other_starts_first(self):
		x = dict(BASE_SCHEDULE)
		y = dict(BASE_SCHEDULE)

		y['startTime'] = '10:30'
		y['endTime'] = '12:00'

		X = CourseSchedule(x)
		Y = CourseSchedule(y)

		self.assertTrue(Y.conflicts_with(X))


if __name__ == '__main__':
	main()
