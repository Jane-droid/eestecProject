from bs4 import BeautifulSoup
from googlesearch import search
import requests


#to search
query="Which is the capital of Cuba"

output=''

for url in search(query, tld="co.in", num = 1, stop = 1):
    res = requests.get(url)
    if res.status_code == 200:
        html_page = res.text
        soup = BeautifulSoup(html_page, 'html.parser')
        for data in soup.find_all("p"):
            output = output + data.get_text()
        print(output)
