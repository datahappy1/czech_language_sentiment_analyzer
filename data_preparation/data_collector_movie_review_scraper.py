"""
data collector
"""
from random import randint
from time import sleep
import csv
import re
import concurrent.futures
import datetime
from bs4 import BeautifulSoup
import urllib3
import requests
from utils.utilities import ProjectCommon

OUTPUT_FILE_PATH = 'reviews_with_ranks.csv'
SCRAPER_FINAL_OUTPUT = []
MOVIE_REVIEW_URLS = []


class Anonymize:
    """
    anonymize class
    """
    def __init__(self):
        self.headers = [{'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
                                       ' AppleWebKit/537.36 (KHTML, like Gecko) '
                                       'Chrome/50.0.2661.102 Safari/537.36'},
                        {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; '
                                       'rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 '
                                       '(.NET CLR 3.5.30729)'},
                        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                       'MyAppName/1.0.0 (someone@example.com)'}]

    @staticmethod
    def sleeper():
        """
        basic sleeper function used to sleep between requests
        :return:
        """
        sleep(randint(2, 5))

    def randomize_request_headers(self):
        """
        call sleeper and randomize request headers function used for each request
        :return:
        """
        return self.headers[randint(0, len(self.headers)-1)]


def movie_review_url_collector():
    """
    function collecting urls with the movie reviews
    :return:0
    """
    start_page_urls = ['https://www.csfd.cz/zebricky/nejhorsi-filmy/?show=complete',
                       'https://www.csfd.cz/zebricky/nejlepsi-filmy/?show=complete']

    obj = Anonymize()
    for start_page in start_page_urls:
        page = requests.get(start_page, headers=Anonymize.randomize_request_headers(obj))
        soup = BeautifulSoup(page.content, 'html.parser')
        movie_review_url = soup.find_all('td', attrs={'class': 'film'})
        for url_item in movie_review_url[:300]:
            children = url_item.findChildren("a", recursive=False)
            movie_name = str(children).split("/")[2]
            for random_index in ([2, 3, 4, 5, 6, 7]):
                review_page = str(random_index)
                MOVIE_REVIEW_URLS.append('https://www.csfd.cz/film/{}/komentare/strana-{}'.
                                         format(movie_name, review_page))
    return 0


def movie_review_scraper(url_to_scrape):
    """
    function getting the url from the argument, requesting the raw html
    and scraping the movie review html code
    :param url_to_scrape: url
    :return:None
    """
    obj = Anonymize()

    print(f'{datetime.datetime.now()} started scraping {url_to_scrape}')
    try:
        Anonymize.sleeper()
        page = requests.get(url, headers=Anonymize.randomize_request_headers(obj))
        if page.status_code == 200:

            # the <li> html tag structure we're scraping in loops:
            #
            # variation #1 with star count as rank in the img alt text tag:
            #   <li id = "comment-796722" >
            #       <div class ="info" >
            #           <a href = "" > all reviewer's reviews </a>/
            #           <a href = "" > <img src = "" class ="" ></a>
            #       </div>
            #       <h5 class = "author" > <a href="" > reviewers nickname </a></h5>
            #       <img src = "" class ="rating" width="32" alt="****" / >
            #       <p class ="post" > movie review
            #       <span class ="date desc" > date of review </span></p>
            #   </li>
            #
            # variation #2 with 1 word ranking ("odpad!" translates to "junk") in the strong tag:
            #   <li id = "comment-9092651" >
            #       <div class ="info" >
            #           <a href = "" > all reviewer's reviews </a>/
            #           <a href = "" > <img src = "" class ="" ></a>
            #       </div>
            #       <h5 class ="author" > <a href="" > reviewers nickname </a></h5>
            #       <strong class ="rating" > odpad! </strong>
            #       <p class ="post" > movie review
            #       <span class ="date desc" > date of review </span></p>
            #   </li>

            soup = BeautifulSoup(page.content, 'html.parser')
            _l_substring_to_trim_to = '<p class="post">'
            _r_substring_to_trim_from = '<span class="date desc">'
            for soup_item in soup.find_all("li", {"id" : re.compile(r"comment-*")}):
                scraper_temp_output = []
                img = soup_item.findChildren("img",
                                             attrs={'class': 'rating'})
                strong = soup_item.findChildren(["strong", "p"],
                                                attrs={'class': ['rating', 'post']})

                if strong and str(strong).startswith('[<strong class="rating">odpad!</strong>'):
                    _r_trim = len(str(strong)) - str(strong).rfind(_r_substring_to_trim_from)
                    _l_trim = str(strong).rfind(_l_substring_to_trim_to) + len(_l_substring_to_trim_to)
                    scraper_temp_output.append({'rank': -2,
                                                'review': str(strong)[_l_trim:-_r_trim]})

                else:
                    _r_trim = len(str(img)) - str(img).rfind(_r_substring_to_trim_from)
                    _l_trim = str(img).rfind(_l_substring_to_trim_to) + len(_l_substring_to_trim_to)
                    if img and str(img).startswith('[<img alt="*"'):
                        scraper_temp_output.append({'rank': -2,
                                                    'review': str(img)[_l_trim:-_r_trim]})
                    elif img and str(img).startswith('[<img alt="**"'):
                        scraper_temp_output.append({'rank': -1,
                                                    'review': str(img)[_l_trim:-_r_trim]})
                    elif img and str(img).startswith('[<img alt="***"'):
                        scraper_temp_output.append({'rank': 1,
                                                    'review': str(img)[_l_trim:-_r_trim]})
                    elif img and str(img).startswith('[<img alt="****"'):
                        scraper_temp_output.append({'rank': 2,
                                                    'review': str(img)[_l_trim:-_r_trim]})
                    elif img and str(img).startswith('[<img alt="*****"'):
                        scraper_temp_output.append({'rank': 2,
                                                    'review': str(img)[_l_trim:-_r_trim]})

                for sto in scraper_temp_output:
                    i_review = sto.get('review')
                    review = ProjectCommon.replace_html(ProjectCommon.replace_non_alpha_chars(str(i_review).lower().lstrip(" ")))
                    rank = sto.get('rank')
                    SCRAPER_FINAL_OUTPUT.append((review, rank))

            print(f'{datetime.datetime.now()} finished scraping {url}')
        else:
            print(f'{datetime.datetime.now()} Invalid request status code '
                  f'{str(page.status_code)} for {url}')

    except urllib3.exceptions.ConnectionError as connerr:
        print(str(connerr))
    except Exception as exc:
        print(str(exc))

if __name__ == "__main__":
    # fill the list with urls used for movie data scraping
    movie_review_url_collector()

    # process the list items in a multi-threaded pool based
    # scraper function movie_review_scraper
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        FUTURE_TO_URL = {executor.submit(movie_review_scraper, url):
                             url for url in MOVIE_REVIEW_URLS}
        for future in concurrent.futures.as_completed(FUTURE_TO_URL):
            url = FUTURE_TO_URL[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

    # write to OUTPUT_FILE_PATH csv file the scraped movie review data
    with open(OUTPUT_FILE_PATH, 'w', encoding='utf8', newline='\n') as fw:
        writer = csv.writer(fw, escapechar='/', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(SCRAPER_FINAL_OUTPUT)

    print("Movie review data collection phase complete.")
