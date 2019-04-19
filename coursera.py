import json
import random
import requests
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from openpyxl import Workbook
from tqdm import tqdm
import argparse

URL = 'https://www.coursera.org/sitemap~www~courses.xml'


def get_args():
    parser = argparse.ArgumentParser(
        description='The app "Coursers Dump" takes 20 random courses '
                    'from Coursera.org and pushes them to Excel file.')
    parser.add_argument(
        '--path',
        '-p',
        default='courses.xlsx',
        help='path to save Excel file',
    )
    parser.add_argument(
        '--amount',
        '-a',
        type=int,
        default=20,
        help='amount of courses for loading and saving',
    )
    args = parser.parse_args()
    return [args.path, args.amount]


def fetch(url):
    try:
        response = requests.get(url, timeout=10)
        return response.content
    except requests.RequestException:
        return


def get_courses_urls_list(content):
    if not content:
        return
    soup = BeautifulSoup(content, 'lxml')
    courses_list = []
    for course in soup.find_all('loc'):
        courses_list.append(course.string)
    return courses_list


def get_course_title(soup):
    try:
        h1_tag = soup.find_all('h1')[1]
        return str(h1_tag.string)
    except AttributeError:
        return


def get_course_language(soup):
    try:
        h4_tag_list = soup.find_all('h4')
        return str(h4_tag_list[-1].string)
    except (KeyError, AttributeError):
        return


def get_course_startdate_and_weeks(soup):
    try:
        script_tag = soup.find('script', type='application/ld+json')
        json_content = json.loads(script_tag.string)
        graph = json_content['@graph']
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
        return [startdate, weeks]
    except (AttributeError, KeyError):
        return [None, None]


def get_course_rating(soup):
    try:
        script_tag = soup.find('script', type='application/ld+json')
        json_content = json.loads(script_tag.string)
        graph = json_content['@graph']

        rating = graph[1]['aggregateRating']['ratingValue']
        return rating
    except (AttributeError, KeyError):
        return


def get_course_info(content):
    if not content:
        return
    soup = BeautifulSoup(content, 'html.parser')

    title = get_course_title(soup)
    language = get_course_language(soup)
    startdate, weeks = get_course_startdate_and_weeks(soup)
    rating = get_course_rating(soup)

    return {
        'title': title,
        'language': language,
        'startdate': startdate,
        'weeks': weeks,
        'rating': rating,
    }


def get_courses_info_list(courses_urls_list):
    # ДЛЯ ПРОВЕРЯЮЩЕГО:
    # tqdm не работает с функциями iter() и next()
    # по крайней мере, у меня не получилось
    # использование __iter__() и __next__() - вынужденная мера
    courses_info_list = []
    progressbar = tqdm(
        courses_urls_list,
        desc='Getting courses info',
        leave=False,
    ).__iter__()
    try:
        for course_url in courses_urls_list:
            progressbar.__next__()
            content = fetch(course_url)
            course_info = get_course_info(content)
            if not course_info:
                error_courses_list.append(course_url)
                continue
            courses_info_list.append(course_info)
        progressbar.__next__()

    except StopIteration:
        pass
    return courses_info_list


def get_excel_wb(courses_info_list):
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

    return wb


if __name__ == '__main__':
    path_to_save, courses_amount = get_args()
    content = fetch(URL)
    courses_urls_list = get_courses_urls_list(content)
    error_courses_list = []
    if not courses_urls_list:
        sys.exit("Server doesn't response or connection error")
    try:
        random_courses_urls_list = random.sample(
            courses_urls_list,
            courses_amount,
        )
    except ValueError:
        sys.exit("Amount of courses is incorrect")
    courses_info_list = get_courses_info_list(random_courses_urls_list)
    if not courses_info_list:
        sys.exit("Server doesn't response or connection error")
    excel_wb = get_excel_wb(courses_info_list)
    try:
        excel_wb.save(path_to_save)
    except FileNotFoundError:
        sys.exit('Path to save is incorrect')
    print('{} courses have been safed to {}'.format(
        courses_amount,
        path_to_save,
    ))
    print()
    if error_courses_list:
        print('ERRORS:')
        for course in error_courses_list:
            print(course)
