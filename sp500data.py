#code to get latest equities from the sp500
#scrapes date from wikipedia

from bs4 import BeautifulSoup
from requests import get
import numpy as np


url ="https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
response = get(url)

html_soup = BeautifulSoup(response.text, 'html.parser')

sp500_table = html_soup.find('table', id="constituents")
table_row = sp500_table.find_all('tr')
del table_row[0] #since first row is just table headers we delete them
symbols = np.array([])
for i in table_row:
    sym = i.find('td').a.text
    symbols = np.append(symbols,[sym])
print(len(symbols))

symbols.tofile("sp500.csv", sep=",") #can add \n if we need a new line


