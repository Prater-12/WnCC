import pandas as pd
import bs4
import requests

BASE_URL = 'https://itc.gymkhana.iitb.ac.in'
SOC_URL = BASE_URL+'/wncc/soc/'

res = requests.get(SOC_URL)

soup = bs4.BeautifulSoup(res.content, 'html.parser')
megaDiv = soup.find('div', class_='row row-eq-height shuffle-wrapper')

dfDict = {'id': [],
          'name': [],
          'image': [],
          'group': [],
          'year': [],
          }

for elem in megaDiv.children:
    if (isinstance(elem, bs4.Tag)):
        href = elem.a

        dfDict['name'].append(href.p.getText())

        dfDict['id'].append(href.attrs['href'].split('/')[5][:-5])
        dfDict['image'].append(href.img.attrs['src'].split('/')[6])

        groups = elem.attrs['data-groups'][2:-2].split('\',\'')

        dfDict['group'].append(groups[0])
        dfDict['year'].append(int(groups[1]))


df = pd.DataFrame(dfDict)
df.to_csv('soc_projects.csv')
