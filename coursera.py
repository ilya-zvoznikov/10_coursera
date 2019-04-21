import random
import requests
import sys
from bs4 import BeautifulSoup
from openpyxl import Workbook
from tqdm import tqdm
import argparse
from course_info import get_course_info

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


def fetch_content(url):
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


def get_random_courses_urls_list(urls_list, courses_amount):
    try:
        return random.sample(urls_list, courses_amount)
    except ValueError:
        return


def get_courses_info_list(courses_urls_list):
    courses_info_list = []
    error_courses_list = []
    progressbar = iter(tqdm(
        courses_urls_list,
        desc='Getting courses info',
        leave=False,
    ))
    try:
        for course_url in courses_urls_list:
            next(progressbar)
            content = fetch_content(course_url)
            course_info = get_course_info(content)
            if not course_info:
                error_courses_list.append(course_url)
                continue
            courses_info_list.append(course_info)
        next(progressbar)

    except StopIteration:
        pass
    return [courses_info_list, error_courses_list]


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
        ws.append([
            course['title'],
            course['language'],
            course['startdate'],
            course['weeks'],
            course['rating'],
        ])

    return wb


def save_to_excel_file(workbook, path_to_save, courses_amount):
    try:
        workbook.save(path_to_save)
        return '{} courses have been safed to {}'.format(
            courses_amount,
            path_to_save,
        )
    except FileNotFoundError:
        return 'Path to save is incorrect'


def print_errors(error_courses_list):
    print()
    if error_courses_list:
        print('ERRORS:')
        for course in error_courses_list:
            print(course)


if __name__ == '__main__':
    path_to_save, courses_amount = get_args()
    content = fetch_content(URL)
    courses_urls_list = get_courses_urls_list(content)
    if not courses_urls_list:
        sys.exit("Server doesn't response or connection error")
    random_courses_urls_list = get_random_courses_urls_list(
        courses_urls_list,
        courses_amount,
    )
    if not random_courses_urls_list:
        sys.exit("Amount of courses is incorrect")
    courses_info_list, error_courses_list = get_courses_info_list(
        random_courses_urls_list)
    if not courses_info_list:
        sys.exit("Server doesn't response or connection error")
    excel_wb = get_excel_wb(courses_info_list)
    print(save_to_excel_file(excel_wb, path_to_save, courses_amount))
    print_errors(error_courses_list)
