import json
import random
import requests
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from openpyxl import Workbook
from tqdm import tqdm

URL = 'https://www.coursera.org/sitemap~www~courses.xml'
COURSES_AMOUNT = 20
ERROR_COURSES_LIST = []
PATH_TO_SAVE = 'courses.xlsx'


def fetch(url):
    try:
        response = requests.get(url, timeout=10)
        return response.content
    except requests.RequestException:
        return


def get_courses_list(url):
    content = fetch(url)
    if not content:
        return
    soup = BeautifulSoup(content, 'lxml')
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


def get_course_info(course_url):
    content = fetch(course_url)
    if not content:
        return
    soup = BeautifulSoup(content, 'html.parser')

    title_tag = soup.find('title')
    title = str(title_tag.string).replace(' | Coursera', '')

    h4_tag_list = soup.find_all(
        'h4',
        class_='H4_1k76nzj-o_O-weightBold_uvlhiv-o_O-bold_1byw3y2'
    )
    language = str(h4_tag_list[-1].string)

    script_tag = soup.find('script', type='application/ld+json')
    if not script_tag:
        startdate = None
        weeks = None
        rating = None
    else:
        json_content = json.loads(script_tag.string)
        graph = json_content['@graph']
        try:
            start_datetime = datetime.strptime(
                graph[2]['hasCourseInstance']['startDate'],
                '%Y-%m-%d',
            )
            startdate = start_datetime.date()

            end_datetime = datetime.strptime(
                graph[2]['hasCourseInstance']['endDate'],
                '%Y-%m-%d',
            )
            weeks = round((end_datetime - start_datetime).days / 7)
        except KeyError:
            startdate = None
            weeks = None

        try:
            rating = graph[1]['aggregateRating']['ratingValue']
        except KeyError:
            rating = None
    return {
        'title': title,
        'language': language,
        'startdate': startdate,
        'weeks': weeks,
        'rating': rating,
    }


def get_courses_info_list(courses_list):
    courses_info_list = []
    progressbar = tqdm(
        courses_list,
        desc='Getting courses info',
        leave=False,
    ).__iter__()
    try:
        for course in courses_list:
            progressbar.__next__()
            course_info = get_course_info(course)
            if not course_info:
                ERROR_COURSES_LIST.append(course)
                continue
            courses_info_list.append(course_info)
        progressbar.__next__()

    except StopIteration:
        pass
    return courses_info_list


def output_courses_info_to_xlsx(courses_info_list, filepath):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Courses'

    ws.append([
        'Title',
        'Language',
        'Start date',
        'Weeks',
        'Rating',
    ])

    for course in courses_info_list:
        ws.append([course['title'],
                   course['language'],
                   course['startdate'],
                   course['weeks'],
                   course['rating'],
                   ])

    wb.save(filepath)


if __name__ == '__main__':
    courses_list = get_courses_list(URL)
    if not courses_list:
        sys.exit("Server doesn't response or connection error")
    random_courses_list = get_random_courses_list(
        courses_list,
        COURSES_AMOUNT,
    )
    courses_info_list = get_courses_info_list(random_courses_list)
    if not courses_info_list:
        sys.exit("Server doesn't response or connection error")
    output_courses_info_to_xlsx(
        courses_info_list,
        PATH_TO_SAVE,
    )
    print('Courses have been safed to {}'.format(PATH_TO_SAVE))
    print()
    if len(ERROR_COURSES_LIST) > 0:
        print('ERRORS:')
        for course in ERROR_COURSES_LIST:
            print(course)
