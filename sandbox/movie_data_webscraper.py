import requests
import time
from bs4 import BeautifulSoup
import threading


urls = [
   "https://www.csfd.cz/film/4099-co-zere-gilberta-grapea/komentare/strana-2/",
   "https://www.csfd.cz/film/4099-co-zere-gilberta-grapea/komentare/strana-3/",
   "https://www.csfd.cz/film/4099-co-zere-gilberta-grapea/komentare/strana-4/"
]
#
# urls = ["C:\czech_language_sentiment_analyzer\sandbox\csfd.cz.html",
#         "C:\czech_language_sentiment_analyzer\sandbox\csfd2.cz.html",
#         "C:\czech_language_sentiment_analyzer\sandbox\csfd3.cz.html"]
output = []


def scraper(url):
    #for url in urls:
    #with open(urls[0], encoding='UTF-8', mode='r') as csfd:
    # with open(url, encoding='UTF-8', mode='r') as csfd:
    #     r = csfd.read()
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # soup = BeautifulSoup(r, 'html.parser')
    rankings = soup.find_all('img', attrs={'class': 'rating'})
    ratings = soup.find_all('p', attrs={'class':'post'})

    for rank,rate in zip(rankings,ratings):
        if '"*"' in str(rank):
            output.append({'rank': 1, 'rate': (str(rate)[17:])[:-47]})
        elif '"**"' in str(rank):
            output.append({'rank': 2, 'rate': (str(rate)[17:])[:-47]})
        elif '"***"' in str(rank):
            output.append({'rank': 3, 'rate': (str(rate)[17:])[:-47]})
        elif '"****"' in str(rank):
            output.append({'rank': 4, 'rate': (str(rate)[17:])[:-47]})
        elif '"*****"' in str(rank):
            output.append({'rank': 5, 'rate': (str(rate)[17:])[:-47]})

    for o in output:
        print(o)


if __name__ == "__main__":
    # threads = 3   # Number of threads to create
    # Create a list of jobs and then iterate through
    # the number of threads appending each thread to
    # the job list
    jobs = []
    for url in urls:
        thread = threading.Thread(target=scraper(url))
        jobs.append(thread)

    # Start the threads (i.e. calculate the random number lists)
    for j in jobs:
        j.start()

    # Ensure all of the threads have finished
    for j in jobs:
        j.join()

    print("List processing complete.")
