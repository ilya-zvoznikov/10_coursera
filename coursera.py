import requests
from bs4 import BeautifulSoup as bs
import sys
import random
import json
from _datetime import datetime
from openpyxl import Workbook

URL = 'https://www.coursera.org/sitemap~www~courses.xml'
COURSES_AMOUNT = 20
PATH_TO_SAVE = 'courses.xlsx'


def fetch(url):
    try:
        response = requests.get(url)
        return response.content
    except requests.RequestException:
        return


def get_courses_list(url):
    content = fetch(url)
    if not content:
        return
    soup = bs(content, 'lxml')
    courses_list = []
    for course in soup.find_all('loc'):
        courses_list.append(course.string)
    return courses_list


def get_random_courses_list(courses_list, amount):
    random_courses_list = []
    for _ in range(amount):
        course = courses_list[random.randint(0, len(courses_list))]
        random_courses_list.append(course)
    return random_courses_list


def get_course_info(course_slug):
    content = fetch(course_slug)
    if not content:
        return
    soup = bs(content, 'html.parser')
    h4s = soup.find_all(
        'h4',
        class_='H4_1k76nzj-o_O-weightBold_uvlhiv-o_O-bold_1byw3y2'
    )
    script = soup.find('script', type='application/ld+json')
    json_content = json.loads(script.string)

    startdate = datetime.strptime(
        json_content['@graph'][2]['hasCourseInstance']['startDate'],
        '%Y-%m-%d',
    )
    enddate = datetime.strptime(
        json_content['@graph'][2]['hasCourseInstance']['endDate'],
        '%Y-%m-%d',
    )
    return {'title': json_content['@graph'][2]['name'],
            'language': str(h4s[-1].string),
            'startdate': startdate.date(),
            'weeks': round((enddate - startdate).days / 7),
            'rating': json_content['@graph'][1]['aggregateRating'][
                'ratingValue'],
            }


def output_courses_info_to_xlsx(courses_info_list, filepath):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Courses'

    ws.cell(row=1, column=1, value='Title')
    ws.cell(row=1, column=2, value='Language')
    ws.cell(row=1, column=3, value='Startdate')
    ws.cell(row=1, column=4, value='Weeks')
    ws.cell(row=1, column=5, value='Rating')

    row = 2
    for course in courses_info_list:
        ws.cell(row=row, column=1, value=course['title'])
        ws.cell(row=row, column=2, value=course['language'])
        ws.cell(row=row, column=3, value=course['startdate'])
        ws.cell(row=row, column=4, value=course['weeks'])
        ws.cell(row=row, column=5, value=course['rating'])
        row += 1

    wb.save(filepath)


if __name__ == '__main__':
    courses_list = get_courses_list(URL)
    if not courses_list:
        sys.exit('ERROR')
    random_courses_list = get_random_courses_list(courses_list, COURSES_AMOUNT)
    courses_info_list = []
    for course in random_courses_list:
        courses_info_list.append(get_course_info(course))
    output_courses_info_to_xlsx(courses_info_list, PATH_TO_SAVE)
    print('Courses have been safed to {}'.format(PATH_TO_SAVE))
