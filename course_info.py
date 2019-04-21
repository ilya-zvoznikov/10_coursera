import json
from bs4 import BeautifulSoup
from datetime import datetime


def get_course_title(soup):
    try:
        h1_tag = soup.find_all('h1')[1]
        return h1_tag.text
    except AttributeError:
        return


def get_course_language(soup):
    try:
        h4_tag_list = soup.find_all('h4')
        return str(h4_tag_list[-1].string)
    except (KeyError, AttributeError):
        return


def get_course_startdate_and_weeks(info_dict):
    try:
        hci = info_dict['@graph'][2]['hasCourseInstance']
        start_datetime = datetime.strptime(hci['startDate'], '%Y-%m-%d')
        startdate = start_datetime.date()
        end_datetime = datetime.strptime(hci['endDate'], '%Y-%m-%d')
        weeks = round((end_datetime - start_datetime).days / 7)
        return [startdate, weeks]
    except (AttributeError, KeyError):
        return [None, None]


def get_course_rating(info_dict):
    try:
        rating = info_dict['@graph'][1]['aggregateRating']['ratingValue']
        return rating
    except (AttributeError, KeyError):
        return


def get_course_info(content):
    if not content:
        return
    soup = BeautifulSoup(content, 'html.parser')

    title = get_course_title(soup)
    language = get_course_language(soup)

    script_tag = soup.find('script', type='application/ld+json')
    if script_tag:
        course_info_dict = json.loads(script_tag.string)
        startdate, weeks = get_course_startdate_and_weeks(course_info_dict)
        rating = get_course_rating(course_info_dict)
    else:
        startdate = None
        weeks = None
        rating = None
    return {
        'title': title,
        'language': language,
        'startdate': startdate,
        'weeks': weeks,
        'rating': rating,
    }
