import datetime
import requests
import urllib3
import concurrent.futures
from bs4 import BeautifulSoup
from random import randint
from time import sleep

scraper_temp_output = []
scraper_final_output = []
movie_review_urls = []


class Anonymize:
    def __init__(self):
        self.headers = [{'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'},
                        {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)'},
                        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) MyAppName/1.0.0 (someone@example.com)'}]

    @staticmethod
    def sleeper():
        """
        basic sleeper function used to sleep between requests
        :return:
        """
        sleep(randint(1, 3))

    def randomize_request_headers(self):
        """
        call sleeper and randomize request headers function used for each request
        :return:
        """
        return self.headers[randint(0,len(self.headers)-1)]


def movie_review_url_collector():
    """
    function putting to the queue urls with the movie reviews
    based on 100 of the best 300 and 100 of the worst 300 movies in the movie review database
    :return:0
    """
    start_page_urls = ['https://www.csfd.cz/zebricky/nejhorsi-filmy/?show=complete',
                       'https://www.csfd.cz/zebricky/nejlepsi-filmy/?show=complete']

    obj = Anonymize()
    for start_page in start_page_urls:
        page = requests.get(start_page, headers=Anonymize.randomize_request_headers(obj))
        soup = BeautifulSoup(page.content, 'html.parser')
        url = soup.find_all('td', attrs={'class': 'film'})
        for url_item in url[:100]:
            children = url_item.findChildren("a", recursive=False)
            movie_name = str(children).split("/")[2]
            for random_index in ([2,3,4,5]):
                review_page = str(random_index)
                movie_review_urls.append('https://www.csfd.cz/film/{}/komentare/strana-{}'.
                                         format(movie_name,review_page))
    return 0


def movie_review_scraper(url):
    """
    function getting the url from the argument, requesting the raw html
    and scraping the movie review html code
    :param url: url
    :return:None
    """
    obj = Anonymize()

    print(f'{datetime.datetime.now()} started scraping {url}')
    try:
        Anonymize.sleeper()
        page = requests.get(url, headers=Anonymize.randomize_request_headers(obj))
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            rankings = soup.find_all('img', attrs={'class': 'rating'})
            ratings = soup.find_all('p', attrs={'class': 'post'})

            for rank, rate in zip(rankings, ratings):
                if '"*"' in str(rank):
                    scraper_temp_output.append({'rank': -2, 'words': ((str(rate)[17:])[:-47]).split()})
                elif '"**"' in str(rank):
                    scraper_temp_output.append({'rank': -1, 'words': ((str(rate)[17:])[:-47]).split()})
                elif '"***"' in str(rank):
                    scraper_temp_output.append({'rank': 0, 'words': ((str(rate)[17:])[:-47]).split()})
                elif '"****"' in str(rank):
                    scraper_temp_output.append({'rank': 1, 'words': ((str(rate)[17:])[:-47]).split()})
                elif '"*****"' in str(rank):
                    scraper_temp_output.append({'rank': 2, 'words': ((str(rate)[17:])[:-47]).split()})

                for o in scraper_temp_output:
                    for i_word in o.get('words'):
                        word = str(i_word).lower().replace('.','')
                        rank = str(o.get('rank'))
                        scraper_final_output.append(word + ' ' + rank)

            print(f'{datetime.datetime.now()} finished scraping {url}')
        else:
            print(f'{datetime.datetime.now()} Invalid request status code {str(page.status_code)} for {url}')

    except urllib3.exceptions.ConnectionError as CE:
        print(str(CE))

    except Exception as E:
        print(str(E))


if __name__ == "__main__":
    # fill the list with urls used for movie data scraping
    movie_review_url_collector()

    # process the list items in a multi-threaded pool based scraper function movie_review_scraper
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(movie_review_scraper, url): url for url in movie_review_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

    # write to temp_file.txt the scraped movie review data
    with open('./data_temp/temp_file.txt', 'w', encoding='utf8') as fw:
        for item in scraper_final_output:
            fw.write(item + '\n')

    print("Movie review data collection phase complete.")
