import pandas as pd
import bs4
import requests
from sqlalchemy import create_engine
import aiohttp
import asyncio


async def fetch(url, session):
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
        return (resp, url)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def fetchAll(urls):
    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(*[fetch(url, session) for url in urls])
    return responses

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
projectPages = []

for elem in megaDiv.children:
    if (isinstance(elem, bs4.Tag)):
        href = elem.a

        projectPages.append(BASE_URL+href.attrs['href'])

        dfDict['name'].append(href.p.getText())

        dfDict['id'].append(href.attrs['href'].split('/')[-1][:-5])
        dfDict['image'].append(href.img.attrs['src'].split('/')[-1])

        groups = elem.attrs['data-groups'][2:-2].split('\",\"')

        dfDict['group'].append(groups[0])
        dfDict['year'].append(int(groups[1]))


df = pd.DataFrame(dfDict)
df.to_csv('soc_projects.csv', index=False)

# We can further fetch the content on each project's page (href.attrs['href']), and extract mentor names, est. mentee count,
# project description, and the tentative time table
#
# This part of the program however, was not implemented fully

# engine = create_engine('sqlite:///soc_projects.db', echo=False)
# df.to_sql('projects', con=engine, index=False)

# projectPages = asyncio.run(fetchAll(projectPages[0:7]))

# mentorsDict = {
#    'project_id': [],
#    'mentors': [],
# }

# timetableDict = {
#    'project_id': [],
#    'week': [],
#   'tasks': []
# }

# for projectPage in projectPages[0:1]:
#    projectId = projectPage[1].split('/')[-1][:-5]
#    print(projectId)
#    pSoup = bs4.BeautifulSoup(projectPage[0], 'html.parser')
#
#   mentorMenteeInfo = pSoup.find(
#      "div", class_="mobile-img-soc").next_sibling.next_sibling.findAll("ul")
#
#   projectMentors = []
#  for elem in mentorMenteeInfo[1].children:
#     if (isinstance(elem, bs4.Tag)):
#        mentorsDict[projectId].append(projectId)
#        mentorsDict['mentors'].append(elem.p.text)

#  mentees = mentorMenteeInfo[2].contents[1].p.text
