from bs4 import BeautifulSoup
from googlesearch import search
import requests

def google_search(query):
    output=''
    
    for url in search(query, tld="co.in", num = 2, stop = 2):
        res = requests.get(url)
        if res.status_code == 200:
            html_page = res.text
            soup = BeautifulSoup(html_page, 'html.parser')
            for data in soup.find_all("p"):
                output = output + data.get_text()
            return output

#print(google_search("Which ocean is Bermuda in?"))

