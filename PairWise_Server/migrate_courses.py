from requests import get
import datetime
from os import environ
from django import setup

environ.setdefault('DJANGO_SETTINGS_MODULE', 'PairWise_Server.settings')
setup()

from models import Course, Term, CourseOffering, TimeSection, CourseSection


def load_course_data():
    cbl_site = "https://cobalt.qas.im/api/1.0/courses"
    net_key = "mYsO2m1KfJYFBEd3BYVvho4bmI9PKR2x"
    start_term = "2018 Winter"
    filters = "code:\"CSC\" AND campus:\"UTSG\" AND term:>=\"{0}\"".format(start_term)
    skip_amt = 100
    params = "&limit={0}".format(skip_amt)

    request_base = "{0}/filter?key={1}&q={2}{3}".format(cbl_site, net_key, filters, params)

    passed_count = 0
    combined = []
    new_data = None
    while new_data != []:
        request = request_base + "&skip={0}".format(passed_count)
        new_data = get(request).json()
        combined.extend(new_data)
        passed_count += 100

    return combined


def _convert_term(c_code, term_str):
    if 'Summer' in term_str:
        term_code = 'S' + c_code[-1]
    else:
        term_code = c_code[-1]

    term_year = term_str[0: term_str.index(' ')]

    return term_year, term_code


def _convert_time_of_day(time_in_seconds):
    time_obj = datetime.time(hour=time_in_seconds % 3600)
    return time_obj


def _convert_weekday(weekday):
    return {
        'MONDAY': 'M',
        'TUESDAY': 'T',
        'WEDNESDAY': 'W',
        'THURSDAY': 'R',
        'FRIDAY': 'F',
        'SATURDAY': 'A',
        'SUNDAY': 'S',
    }.get(weekday, None)


def migrate():
    data = load_course_data()
    for course in data:
        # Require course code, name, term, times, section names per section
        course_code = course['code'][:-3]
        print(course_code)
        course_model = Course.objects.get_or_create(course_code=course_code)[0]
        course_model.name=course['name']
        course_model.save()

        section_year, section_term = _convert_term(course['code'], course['term'])
        this_term = Term.objects.get_or_create(year=section_year, term=section_term)[0]

        this_offering = CourseOffering.objects.get_or_create(term=this_term, course=course_model)[0]

        for section in course['meeting_sections']:
            section_code = section['code']
            new_section = CourseSection.objects.get_or_create(offering=this_offering, section_name=section_code)[0]

            for session in section['times']:
                session_day = _convert_weekday(session['day'])
                start_time = _convert_time_of_day(session['start'])
                end_time = _convert_time_of_day(session['end'])

                time_slot = TimeSection.objects.get_or_create(day=session_day, start_time=start_time, end_time=end_time)[0]
                new_section.times.add(time_slot)


if __name__ == '__main__':
    # Course.object.clear()
    migrate()
    print('Done')
