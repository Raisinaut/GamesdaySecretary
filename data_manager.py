import json
import os
import datetime, time
from replit import db
from game import game

# Set time zone to PST
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()

key = "games" # name of used database 


# Adds a game to the "games" key
# If the key doesn't exist, one is created
def add_game(title):
  newGame = game(title, False, None)        # create game object
  jsonStr = json.dumps(newGame.__dict__)    # convert to json
  if key in db.keys():                        # if database exists
    game_list = db[key]                       # read database
    game_list.insert(0, jsonStr)              # add game object to list
    db[key] = game_list                       # save to database
  else:
    db[key] = [jsonStr]        # create database with object

def get_index(title):
  data = db[key]
  for i in range(len(data)):
    game = json.loads(data[i])
    if title.lower() == game['title'].lower():
      return i
  
  # no matches were found
  return None

# Removes a game from the "games" key
def remove_game(title):
  found = False
  index = get_index(title)
  if index != None:
    data = db[key]          # copy database
    del data[index]         # remove game
    db[key] = data          # save to databse
    found = True
  return found

# Replaces a game with a copy, marked as played
# Does nothing if status is identical
def change_played_status(title, status):
  found = False
  index = get_index(title)
  
  if index != None:
    data = db[key]      # copy database

    # check if status is different
    if json.loads(data[index])['played'] != status:
      del data[index]                         # remove old game

      swap = game(title, status, get_date())  # create replacement game object
      jsonStr = json.dumps(swap.__dict__)     # convert to json format

      if status == True:
        data.append(jsonStr)                  # add to list end
      else:
        data.insert(0, jsonStr)               # add to list start

      db[key] = data                          # save to database
    found = True

  return found

# Returns an array of titles
def get_list(lists = []):
  games = []
  for data in lists:
    for i in data:
      title = json.loads(i)['title']
      games.append(title)
  return games

# Returns a string of all games
def get_list_string():
  data = db[key]
  if len(data) > 0:
    listString = ""
    # Construct line-by-line list
    for i in data:
      game = json.loads(i)
      listString += game['title'] 
      if game['played']:
        # include date finished
        listString += " (Completed: {})".format(game['dateFinished'])
      listString += "\n"
    return listString
  else:
    return ":face_with_raised_eyebrow: Looks like the game pool is empty!"

def get_weekly_game():
  return db["Weekly Game"]
def set_weekly_game(title: str):
  db["Weekly_Game"] = title

def get_date():
  t = datetime.datetime.now()
  return t.strftime("%a, %x")

def get_current_week():
  start = datetime.date(2021, 8, 25)
  today = datetime.date.today()
  delta = (today - start).days
  return int(delta / 7)