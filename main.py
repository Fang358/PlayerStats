import requests
from bs4 import BeautifulSoup
import pandas as pd
import xlsxwriter
from tkinter import *
from tkcalendar import Calendar
from datetime import datetime
 
def add_to_dict(url, df_dict, id, tourn, agents, maps):
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
          
        enemy = soup.find_all("div", {"class" : "team-name"})[enemy].get_text().replace("\n", "").replace("\t", "")
        
        df_dict['Tournament'].append(tourn)
        df_dict['Opponent'].append(enemy)
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
        df_dict['KD'].append(both_stats[2] / max(1, both_stats[3]))
        df_dict['KPR'].append(both_stats[2] / (score + enemy_score))
        df_dict['APR'].append(both_stats[4] / (score + enemy_score))
        df_dict['DPR'].append(both_stats[3] / (score + enemy_score))
        df_dict['FKPR'].append(both_stats[9] / (score + enemy_score))
        df_dict['FDPR'].append(both_stats[10] / (score + enemy_score))
        
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
        
        if map not in maps.keys():
            maps[map] = {
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
        
        maps[map]["Maps Won"] += 1 if score > enemy_score else 0
        maps[map]["Maps"] += 1
        maps[map]["Rounds"] += score + enemy_score
        maps[map]["Rounds Won"] += score
        maps[map]["Kills"] += both_stats[2]
        maps[map]["Deaths"] += both_stats[3]
        maps[map]["Assists"] += both_stats[4]
        maps[map]["KAST"].append(both_stats[6])
        maps[map]["ACS"].append(both_stats[1])
        maps[map]["ADR"].append(both_stats[7])
        maps[map]["HS"].append(both_stats[8])
        maps[map]["Rating"].append(both_stats[0])
        maps[map]["FK"] += (both_stats[9])
        maps[map]["FD"] += (both_stats[10])
        
        print(f"{map} {agent} - {int(both_stats[2])}/{int(both_stats[3])}/{int(both_stats[4])}")
        
    except Exception as e:
      print(f"Error on {url} going to next")

  return df_dict, agents, maps

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
    
    maps = {}
            
    df_dict = {
    'Tournament' : [], 
    'Opponent' : [],
    'Score' : [],
    'EnemyScore' : [],
    'Map' : [],
    'Agent' : [],
    'Rating' : [],
    'KD' : [],
    'ACS' : [],
    'KAST' : [],
    'ADR' : [],
    "KPR" : [],
    "APR" : [],
    "DPR" : [],
    "FKPR" : [],
    "FDPR" : [],
    'HS' : [],
    "Kills" : [],
    'Deaths' : [],
    'Assists' : [],
    'FK' : [],
    'FD' : [],
    }
    

    for game in games:
        if games[game][0] not in ok_tourns:
            continue
        
        if games[game][1] < date:
            continue
                
        df_dict, agents, maps = add_to_dict(game, df_dict, id, games[game][0], agents, maps)
        
    agent_dict = {
        "Agent" : [],
        "Rating" : [],
        "ACS" : [],
        "KD" : [],
        "KAST" : [],
        "ADR" : [],
        'KPR' : [],
        'DPR' : [],
        'APR' : [],
        'FKPR' : [],
        'FDPR' : [],
        "HS" : [],
        "Kills" : [],
        "Deaths" : [],
        "Assists" : [],
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
        agent_dict["KD"].append(agents[agent]["Kills"] / agents[agent]["Deaths"])
        agent_dict["KPR"].append(agents[agent]["Kills"] / agents[agent]["Rounds"])
        agent_dict["APR"].append(agents[agent]["Deaths"] / agents[agent]["Rounds"])
        agent_dict["DPR"].append(agents[agent]["Assists"] / agents[agent]["Rounds"])
        agent_dict["FKPR"].append(agents[agent]["FK"] / agents[agent]["Rounds"])
        agent_dict["FDPR"].append(agents[agent]["FD"] / agents[agent]["Rounds"])
        
    maps_dict = {
        "Map Name" : [],
        "Rating" : [],
        "ACS" : [],
        'KD' : [],
        "KAST" : [],
        "ADR" : [],
        'KPR' : [],
        'APR' : [],
        'DPR' : [],
        'FKPR' : [],
        'FDPR' : [],
        "HS" : [],
        "FK" : [],
        "FD" : [],
        "Kills" : [],
        "Deaths" : [],
        "Assists" : [],
        "Maps" : [],
        "Maps Won" : [],
        "Rounds" : [],
        "Rounds Won" : [],
        
    }
    
    for map in maps:
        maps_dict["Map Name"].append(map)
        maps_dict["Rating"].append(sum(maps[map]["Rating"]) / len(maps[map]["Rating"]))
        maps_dict["ACS"].append(sum(maps[map]["ACS"]) / len(maps[map]["ACS"]))
        maps_dict["Kills"].append(maps[map]["Kills"])
        maps_dict["Deaths"].append(maps[map]["Deaths"])
        maps_dict["Assists"].append(maps[map]["Assists"])
        maps_dict["KAST"].append(sum(maps[map]["KAST"]) / len(maps[map]["KAST"]))
        maps_dict["ADR"].append(sum(maps[map]["ADR"]) / len(maps[map]["ADR"]))
        maps_dict["HS"].append(sum(maps[map]["HS"]) / len(maps[map]["HS"]))
        maps_dict["FK"].append(maps[map]["FK"])
        maps_dict["FD"].append(maps[map]["FD"])
        maps_dict["Maps"].append(maps[map]["Maps"])
        maps_dict["Maps Won"].append(maps[map]["Maps Won"])
        maps_dict["Rounds"].append(maps[map]["Rounds"])
        maps_dict["Rounds Won"].append(maps[map]["Rounds Won"])
        maps_dict["KD"].append(maps[map]["Kills"] / maps[map]["Deaths"])
        maps_dict["KPR"].append(maps[map]["Kills"] / maps[map]["Rounds"])
        maps_dict["APR"].append(maps[map]["Deaths"] / maps[map]["Rounds"])
        maps_dict["DPR"].append(maps[map]["Assists"] / maps[map]["Rounds"])
        maps_dict["FKPR"].append(maps[map]["FK"] / maps[map]["Rounds"])
        maps_dict["FDPR"].append(maps[map]["FD"] / maps[map]["Rounds"])
                
    file_name = input("File Name: ")
    dfs_tabs([pd.DataFrame(df_dict), pd.DataFrame(agent_dict), pd.DataFrame(maps_dict)], ["Main", "Agents", "Maps"], f"{file_name}.xlsx")

            
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
