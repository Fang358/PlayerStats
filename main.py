import requests
from bs4 import BeautifulSoup
import pandas as pd
import xlsxwriter
from tkinter import *
from tkcalendar import Calendar
from datetime import datetime
 
def add_to_dict(url, df_dict, id, tourn, agents):
  result = requests.get(url)
  soup = BeautifulSoup(result.content, features="html5lib") 
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

          stat_value = int(stat_value[:-1]) / 100 if stat_value.count("%") > 0 else stat_value
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
        df_dict['KAST'].append(both_stats[6])
        df_dict['ADR'].append(both_stats[7])
        df_dict['HS'].append(both_stats[8])
        df_dict['FK'].append(both_stats[9])
        df_dict['FD'].append(both_stats[10])
        
        if agent not in agents.keys():
            agents[agent] = {
                "Maps" : 0,
                "Rounds" : 0,
                "Rounds Won" : 0,
                "Kills" : 0,
                "Deaths" : 0,
                "Assists" : 0,
                "KAST" : [],
                "ADR" : [],
                "HS" : [],
                "Rating" : [],
                "ACS" : [],
                "FK" : 0,
                "FD" : 0,
                "Maps Won" : 0
            }
        
        agents[agent]["Maps Won"] += 1 if score > enemy_score else 0
        agents[agent]["Maps"] += 1
        agents[agent]["Rounds"] += score + enemy_score
        agents[agent]["Rounds Won"] += score
        agents[agent]["Kills"] += both_stats[2]
        agents[agent]["Deaths"] += both_stats[3]
        agents[agent]["Assists"] += both_stats[4]
        agents[agent]["KAST"].append(both_stats[6])
        agents[agent]["ACS"].append(both_stats[1])
        agents[agent]["ADR"].append(both_stats[7])
        agents[agent]["HS"].append(both_stats[8])
        agents[agent]["Rating"].append(both_stats[0])
        agents[agent]["FK"] += (both_stats[9])
        agents[agent]["FD"] += (both_stats[10])
        
        print(f"{map} {agent} - {int(both_stats[2])}/{int(both_stats[3])}/{int(both_stats[4])}")
        
    except Exception as e:
      print(f"Error on {url} going to next")

  return df_dict, agents

def dfs_tabs(df_list, sheet_list, file_name):
    writer = pd.ExcelWriter(file_name,engine='xlsxwriter')
    for dataframe, sheet in zip(df_list, sheet_list):
        dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0)
    writer.close()

id = int(input("Please enter a player id: "))
games = {}
tourns = []

for page in range(int(input("How many pages do you want to do: "))):
    
    url = f"https://www.vlr.gg/player/matches/{id}/fang358/?page={page+1}"
    result = requests.get(url)
    soup = BeautifulSoup(result.content, features="html5lib") 
    
    for a in soup.find('div', {'class' : 'mod-dark'}).find_all("a"):
        #This bit is "only a little bit" scuffed 
        text = a.find('div', {'class' : 'text-of'}).get_text()
        j = 0
        q = False
        r = ""
        for i, chr in enumerate(list(text)):
            if chr != "\t" and chr != "\n":
                q = True
                r += chr
            elif q:
                break
        
        q1 = False
        r1 = ""
        for i, chr in enumerate(list(a.find('div', {'class' : 'm-item-date'}).get_text())):
            if chr != "\t" and chr != "\n":
                q1 = True
                r1 += chr
            elif q1:
                break
            
        r1 = datetime.strptime(r1, '%Y/%m/%d')    
        
        if r not in tourns:
            tourns.append(r)
        games["https://www.vlr.gg" + a['href']] = [r, r1]

def main():
    ok_tourns = []
    for i, variable in enumerate(variable_names):
        if variable_list[i].get() == 1:
            ok_tourns.append(variable)
                        
    date = datetime.strptime(cal.get_date(), "%m/%d/%y")
    
    top.destroy()
    
    agents = {}
            
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
    'KAST' : [],
    'ADR' : [],
    'HS' : [],
    'FK' : [],
    'FD' : [],
    }

    for game in games:
        if games[game][0] not in ok_tourns:
            continue
        
        if games[game][1] < date:
            continue
        
        
        df_dict, agents = add_to_dict(game, df_dict, id, games[game][0], agents)
        
    agent_dict = {
        "Agent" : [],
        "Rating" : [],
        "ACS" : [],
        "Kills" : [],
        "Deaths" : [],
        "Assists" : [],
        "KAST" : [],
        "ADR" : [],
        "HS" : [],
        "FK" : [],
        "FD" : [],
        "Maps" : [],
        "Maps Won" : [],
        "Rounds" : [],
        "Rounds Won" : []
    }
    
    for agent in agents:
        agent_dict["Agent"].append(agent)
        agent_dict["Rating"].append(sum(agents[agent]["Rating"]) / len(agents[agent]["Rating"]))
        agent_dict["ACS"].append(sum(agents[agent]["ACS"]) / len(agents[agent]["ACS"]))
        agent_dict["Kills"].append(agents[agent]["Kills"])
        agent_dict["Deaths"].append(agents[agent]["Deaths"])
        agent_dict["Assists"].append(agents[agent]["Assists"])
        agent_dict["KAST"].append(sum(agents[agent]["KAST"]) / len(agents[agent]["KAST"]))
        agent_dict["ADR"].append(sum(agents[agent]["ADR"]) / len(agents[agent]["ADR"]))
        agent_dict["HS"].append(sum(agents[agent]["HS"]) / len(agents[agent]["HS"]))
        agent_dict["FK"].append(agents[agent]["FK"])
        agent_dict["FD"].append(agents[agent]["FD"])
        agent_dict["Maps"].append(agents[agent]["Maps"])
        agent_dict["Maps Won"].append(agents[agent]["Maps Won"])
        agent_dict["Rounds"].append(agents[agent]["Rounds"])
        agent_dict["Rounds Won"].append(agents[agent]["Rounds Won"])
        
    file_name = input("File Name: ")
    dfs_tabs([pd.DataFrame(df_dict), pd.DataFrame(agent_dict)], ["Main", "Agents"], f"{file_name}.xlsx")

            
top = Tk()

top.geometry( "300x500" )

mb=  Menubutton ( top, text="Tournament List", relief=RAISED )
mb.pack()
mb.menu  =  Menu ( mb, tearoff = 0 )
mb["menu"]  =  mb.menu

variable_names = tourns
variable_list = [IntVar() for name in variable_names]



for var in variable_list:
    var.set(1)


for i, name in enumerate(variable_names):
    mb.menu.add_checkbutton(label=name, variable=variable_list[i])
    
cal = Calendar(top, selectmode = 'day',
               year = 2023, month = 6,
               day = 26)
 
cal.pack(pady = 20)

button = Button( top , text = "Start" , command = main ).pack()

mb.pack()
top.mainloop()
