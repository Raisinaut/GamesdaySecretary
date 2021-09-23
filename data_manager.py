import json
import os
import datetime, time, sched
from replit import db
from game import game

# Set time zone to PST
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()

key = "games" # name of used database 

# Adds a game to the "games" key
# If the key doesn't exist, one is created
def add_game(title):
  unique = True

  for i in db[key]:
    existing_title = json.loads(i)['title']
    if title.lower() == existing_title.lower():
      unique = False
      break
      
  if unique:
    newGame = game(title, False, None)        # create game object
    jsonStr = json.dumps(newGame.__dict__)    # convert to json
    if key in db.keys():                        # if database exists
      games = db[key]                           # read database
      games.insert(0, jsonStr)                  # add game object to list
      db[key] = games                           # save to database
  return unique

# Returns the index of a given title, if found
def get_index(title):
  data = db[key]
  # search for match
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

# Replaces a game with a copy of a different 'played' status
# Does nothing if status is identical
def change_played_status(title, status):
  found = False
  index = get_index(title)
  
  if index != None:
    data = db[key]  # copy database

    # If status is different
    if json.loads(data[index])['played'] != status:
      del data[index]                         # remove old game

      swap = game(title, status, get_date())  # create replacement game object
      jsonStr = json.dumps(swap.__dict__)     # convert to json format

      if status == True:
        data.append(jsonStr)                  # add replacement to list end
      else:
        data.insert(0, jsonStr)               # add replacement to list start

      db[key] = data                          # save to database
    found = True

  return found

# Returns two lists of title (unplayed, played)
def get_list():
  data = db[key]
  unplayed_games = []
  played_games = []

  # split data into two lists
  for i in data:
    game = json.loads(i)
    if game['played'] == False:
      unplayed_games.append(game['title'])
    else:
      played_games.append(game['title'])

  return [unplayed_games, played_games]

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

# Returns the game of the week
def get_weekly_game():
  return db["Weekly_Game"]
# Sets the game of the week
def set_weekly_game(title: str):
  db["Weekly_Game"] = title

# Returns a formatted date string
def get_date():
  t = datetime.datetime.now()
  return t.strftime("%a, %x")

# Returns number of weeks since the first week
def get_current_week():
  start = datetime.datetime(2021, 8, 25, 19)
  today = datetime.datetime.today()
  delta = (today - start).days
  return int(delta / 7)

# Returns the scheduled meeting day and time
def get_schedule_string():
  # open settings file
  f = open("settings.json")
  data = json.load(f)
  f.close()

  d = data['schedule']['day']
  t = data['schedule']['time']

  return f"{d}s at {t}"