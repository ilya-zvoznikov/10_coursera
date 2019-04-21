import json
from bs4 import BeautifulSoup
from datetime import datetime


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

