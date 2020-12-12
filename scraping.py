from bs4 import BeautifulSoup
import traceback
import requests

def return_scrape(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        title = soup.find('title')
        if "TwitLonger" in title.text:
            result = soup.find(id="posttext")
            return result.text
        else:
            return "Not a TwitLonger link. Please make sure that the root parent tweet contains a valid twitlonger tweet"
    except:
        print(traceback.print_exc())
        pass

# url = "http://tl.gd/n_1srgisl"
# print(return_scrape(url))

