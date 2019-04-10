import requests
from bs4 import BeautifulSoup as bs
import sys
import random
import json
from _datetime import datetime

URL = 'https://www.coursera.org/sitemap~www~courses.xml'
COURSES_AMOUNT = 1


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
            'language': h4s[-1].string,
            'startdate': startdate.date(),
            'weeks': round((enddate - startdate).days / 7),
            'rating': json_content['@graph'][1]['aggregateRating'][
                'ratingValue'],
            }


def output_courses_info_to_xlsx(filepath):
    pass


if __name__ == '__main__':
    courses_list = get_courses_list(URL)
    if not courses_list:
        sys.exit('ERROR')
    random_courses_list = get_random_courses_list(courses_list, COURSES_AMOUNT)

    course_info = get_course_info(random_courses_list[0])

    for k, v in course_info.items():
        print('{}: {}'.format(k, v))
