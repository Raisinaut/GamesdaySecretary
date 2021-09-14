import os
import discord
import random
import json
import datetime
from replit import db
from keep_alive import keep_alive
from game import game

client = discord.Client()
token = os.environ['TOKEN']

## DATABASE VARIABLES ##
key = "games" # name of destination database 

## BOT VARIABLES ##
greetings = ["Hey there", "Greetings", "Konnichiwa", "What's up", "Hello", "Hey"]
help_message = """!hello, !hi, !hey ------- Simple greeting
!add [game] --------- Add a game to the pool
!remove [game] ----- Remove a game from the pool
!played [game] ------ Mark a game as played
!unplayed [game] --- Mark a game as unplayed
!remind [game] ----- Show this week's game
!list ------------------- Display all games in the pool"""

########################################################################
######################### F U N C T I O N S ############################
########################################################################
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

def remove_game(title):
  found = False
  index = get_index(title)
  if index != None:
    data = db[key]          # copy database
    del data[index]         # remove game
    db[key] = data          # save to databse
    found = True
  return found

def change_played_status(title, status):
  found = False
  index = get_index(title)
  
  if index != None:
    data = db[key]      # copy database

    # check if status is different
    if json.loads(data[index])['played'] != status:
      del data[index]

      swap = game(title, status, get_date())  # create game object
      jsonStr = json.dumps(swap.__dict__)     # convert to json format

      if status == True:
        data.append(jsonStr)                  # add to list end
      else:
        data.insert(0, jsonStr)               # add to list start

      db[key] = data                          # save to database
    found = True

  return found

def get_list():
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

def get_date():
  t = datetime.datetime.now()
  return t.strftime("%a, %x")

def get_current_week():
  start = datetime.date(2021, 8, 25)
  today = datetime.date.today()
  delta = (today - start).days
  return int(delta / 7)

########################################################################
#################### D I S C O R D   E V E N T S #######################
########################################################################
@client.event
async def on_ready():
  print('Bot logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  # Exit if message was from self
  if message.author == client.user:
    return
  
  msg = message.content
  
  # Basic greeting responses
  if msg.startswith('!hello') or msg.startswith('!hi') or msg.startswith('!hey'):
    name = str(message.author).split("#")[0]
    await message.channel.send(random.choice(greetings) + ", " + name + "!")
    await message.channel.send("Type !help to see what I can do you for!")

  if msg.startswith('!add '):
    title = msg.split("!add ",1)[1]
    if not title.isspace():
      add_game(title)
      await message.channel.send("I added " + title + " to game pool.")
    else:
      await message.channel.send("I don't think [spaces] is a game.")

  if msg.startswith('!remove '):
    title = msg.split("!remove ",1)[1]
    if remove_game(title):
      await message.channel.send("I removed " + title + " from game pool.")
    else:
      await message.channel.send("I couldn't find " + title + " in the game pool.")

  if msg.startswith('!played '):
    title = msg.split("!played ",1)[1]
    if change_played_status(title, True):
      await message.channel.send("I marked " + title + " as played.")
    else:
      await message.channel.send("I couldn't find " + title + " in the game pool.")

  if msg.startswith('!unplayed '):
    title = msg.split("!unplayed ",1)[1]
    if change_played_status(title, False):
      await message.channel.send("I marked " + title + " as unplayed.")
    else:
      await message.channel.send("I couldn't find " + title + " in the game pool.")
  
  if msg.startswith ('!remind'):
    await message.channel.send("Week {}: ".format(get_current_week())) ## FIXME: include game
  
  if msg.startswith('!list'):
    await message.channel.send(get_list())
  
  if msg.startswith ('!help'):
    await message.channel.send(help_message)

  
keep_alive()
client.run(token)