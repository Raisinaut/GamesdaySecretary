import os
import discord
import random
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
!list ------------------- Display all games in the pool"""

########################################################################
######################### F U N C T I O N S ############################
########################################################################
def add_game(title):
  new_game = title        # create game object

  if key in db.keys():          # if database exists
    game_list = db[key]         # read database
    game_list.append(new_game)  # add game object to list
    db[key] = game_list         # save to database
  else:
    db[key] = [new_game]        # create database with given argument

def get_index(title):
  games = db[key]
  length = len(games)
  i = 0
  while i < length:
    if title.lower() == games[i].lower():
      return i
    i += 1
  # no matches were found
  return None

def remove_game(title):
  found = False
  index = get_index(title)
  if index != None:
    games = db[key]
    del games[index]
    db[key] = games
    found = True
  return found

def change_played_status(title, status = True):
  found = False
  index = get_index(title)
  if index:
    db[key][index].played = status
    found = True
  return found

def get_list(_list):
  list_string = ""
  # Check for existence
  if _list in db.keys():
    L = db[_list]
    length = len(L)

    # Construct grammatically correct list
    if length > 0:
      # First element
      list_string += L[0]
      # Subsequent elements
      if length > 1:
        i = 1
        while i < length:
          list_string += ", " + L[i]
          i += 1
    else:
      list_string = ":face_with_raised_eyebrow: Looks like the game pool is empty!"
  # No such list found
  else:
    list_string = _list + " list not found."
  return list_string

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
    if key in db.keys():
      title = msg.split("!remove ",1)[1]
      if remove_game(title) == True:
        await message.channel.send("I removed " + title + " from game pool.")
      else:
        await message.channel.send("I couldn't find " + title + " in the game pool.")
  
  if msg.startswith('!list'):
    await message.channel.send(get_list(key))

  if msg.startswith ('!help'):
    await message.channel.send(help_message)

keep_alive()
client.run(token)