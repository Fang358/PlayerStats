import requests
from bs4 import BeautifulSoup
import pandas as pd
import xlsxwriter

def add_to_dict(url, df_dict, id, tourn):
  result = requests.get(url)
  soup = BeautifulSoup(result.content) 
  games = soup.find('div', {'class' : "vm-stats"}).find_all('div', {'class' : 'vm-stats-game'})
  for game in games:
    try:
      if game['data-game-id'] == 'all':
        continue

      team = 1
      enemy = 0

      for player in game.find('tbody').find_all('a'):
        if int(player['href'].split('/')[2]) == id:
          team = 0
          enemy = 1

      score = int(game.find_all('div', {'class' : 'score'})[team].get_text())
      enemy_score = int(game.find_all('div', {'class' : 'score'})[enemy].get_text())

      map = (game.find('div', {'class' : 'map'}).find('span').get_text().replace("PICK", "").replace("\n", "").replace("\t", ""))

      for player in game.find_all('tbody')[team].find_all('tr'):
        if int(player.find('a')['href'].split('/')[2]) != id:
          continue


        agent = player.find('img')['title']

        both_stats = []

        for stat in player.find_all('td')[2:]:
          stat_value = (stat.find('span', {'class' : 'mod-both'}).get_text())

          stat_value = stat_value[:-1] if stat_value.count("%") > 0 else stat_value
          both_stats.append(float(stat_value))

        df_dict['Tournament'].append(tourn)
        df_dict['Score'].append(score)
        df_dict['EnemyScore'].append(enemy_score)
        df_dict['Map'].append(map)
        df_dict['Agent'].append(agent)
        df_dict['Rating'].append(both_stats[0])
        df_dict['ACS'].append(both_stats[1])
        df_dict['Kills'].append(both_stats[2])
        df_dict['Deaths'].append(both_stats[3])
        df_dict['Assists'].append(both_stats[4])
        df_dict['K+/-'].append(both_stats[5])
        df_dict['KAST'].append(both_stats[6])
        df_dict['ADR'].append(both_stats[7])
        df_dict['HS'].append(both_stats[8])
        df_dict['FK'].append(both_stats[9])
        df_dict['FD'].append(both_stats[10])
        df_dict['FK+/-'].append(both_stats[11])
    except:
      print(f"Error on {url} going to next")

  return df_dict

def dfs_tabs(df_list, sheet_list, file_name):
    writer = pd.ExcelWriter(file_name,engine='xlsxwriter')
    for dataframe, sheet in zip(df_list, sheet_list):
        dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0)
    writer.save()

url = "https://www.vlr.gg/player/matches/3063/mel/?page=4"
result = requests.get(url)
id = 3063
soup = BeautifulSoup(result.content)
games = {}
for a in soup.find('div', {'class' : 'mod-dark'}).find_all("a"):
  #Don't know why this works but it does so :D
  text = a.find('div', {'class' : 'text-of'}).get_text()
  j = 0
  for i, chr in enumerate(list(text)):
    if chr == "\t":
      j += 1
    if j == 7:
      break 
  games["https://www.vlr.gg" + a['href']] = a.find('div', {'class' : 'text-of'}).get_text()[6:i-2]

df_dict = {
   'Tournament' : [], 
   'Score' : [],
   'EnemyScore' : [],
   'Map' : [],
   'Agent' : [],
   'Rating' : [],
   'ACS' : [],
   "Kills" : [],
   'Deaths' : [],
   'Assists' : [],
   'K+/-' : [],
   'KAST' : [],
   'ADR' : [],
   'HS' : [],
   'FK' : [],
   'FD' : [],
   'FK+/-' : []
  }

for game in games:
  df_dict = add_to_dict(game, df_dict, id, games[game])

dfs_tabs([pd.DataFrame(df_dict)], ["Main"], "Testing.xlsx")

