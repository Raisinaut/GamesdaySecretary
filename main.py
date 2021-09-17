import os
import discord
import random
import data_manager
from replit import db
from keep_alive import keep_alive
from discord_components import ComponentsBot, Button, Select, SelectOption, ButtonStyle

selected_game     = None # used when modifying a game from selection menu
selected_status   = None # used when editing the last modify message
modify_message_id = None # used to find modify message

token = os.environ['TOKEN']
bot = ComponentsBot(command_prefix = "!")

bot.remove_command('help')

greetings = ["Hey there", "Greetings", "Konnichiwa", "What's up", "Hello", "Hey", "Hi"]
help_message = """Commands:
!hello, !hi, !hey ------- Simple greeting
!add [game] --------- Add a game to the pool
!modify --------------- Remove a game or change its played status 
!remind -------------- Show this week's game
!list ------------------- Display all games in the pool"""



########################################################################
########################## B O T   E V E N T S #########################
########################################################################

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.event
async def on_button_click(interaction):
  global selected_game
  global modify_message_id
  last_modify_msg = await interaction.channel.fetch_message(modify_message_id)
  btn = interaction.custom_id
  
  if btn == "cancel_button":
    # delete last modify message
    await last_modify_msg.delete()
    # reset modify message id
    modify_message_id = None

  # Options that require selection
  elif selected_game != None:
    print(f"Modified {selected_game}")
    if btn == "played_button":
      if data_manager.change_played_status(selected_game, True):
        await interaction.respond(content = "I've marked " + selected_game + " as played.")
      else:
        await interaction.respond(content = "That game is no longer in the pool.")

    if btn == "unplayed_button":
      if data_manager.change_played_status(selected_game, False):
        await interaction.respond(content = "I marked " + selected_game + " as unplayed.")
      else:
        await interaction.respond(content = "That game is no longer in the pool.")

    if btn == "remove_button":
      if data_manager.remove_game(selected_game):
        await interaction.channel.send(content = "I've removed " + selected_game + " from the game pool.")
        # show updated pool
      else:
        await interaction.respond(content = "That game was already deleted.")
    
    # update modify message relative to last status selection
    updated_components = construct_updated_components(selected_status)
    await last_modify_msg.edit(
      "Select a status, then choose a game to modify",
      components = updated_components
      )

  else:
    await interaction.respond(content = "Select a game first.")

@bot.event
async def on_select_option(interaction):
  global selected_game
  global selected_status
  global modify_message_id
  select_type = interaction.custom_id

  if select_type == "game_select":
    # do not respond
    await interaction.respond(type = 6)
    # save selected game
    selected_game = interaction.values[0]
    print(f"Selected {selected_game}")
    

  elif select_type == "status_select":
    selected_status = int(interaction.values[0])
    # do not respond
    await interaction.respond(type = 6)
    # find last modify message
    last_modify_msg = await interaction.channel.fetch_message(modify_message_id)
    # update modify message
    selected_status = int(interaction.values[0])
    updated_components = construct_updated_components(selected_status)
    await last_modify_msg.edit(
      "Select a status, then choose a game to modify",
      components = updated_components
      )


########################################################################
######################## B O T   C O M M A N D S #######################
########################################################################

@bot.command()
async def help(ctx):
  await ctx.channel.send(help_message)

@bot.command(description = "Basic greeting")
async def hello(ctx):
  name = str(ctx.author).split("#")[0]
  await ctx.channel.send(random.choice(greetings) + " " + name + "!")
  await ctx.channel.send("Type !actions to see what I can do you for!")

@bot.command(description = "Adds a specified game to the pool")
async def add(ctx):
  title = ctx.message.content.split("!add ",1)[1]
  if not title.isspace():
    data_manager.add_game(title)
    await ctx.channel.send(f"I've added {title} to the game pool.")
  else:
    await ctx.channel.send("Um, [spaces] isn't a game.")

@bot.command(description = "Reminds you of this week's game")
async def remind(ctx):
  embed = discord.Embed(
    title = "Week {}".format(data_manager.get_current_week()),
    description = data_manager.get_weekly_game(),
    color = discord.Color.blue()
  )
  await ctx.send(embed=embed)

@bot.command(description = "Lists all games in the pool")
async def list(ctx):
  embed = discord.Embed(
    title = "Game Pool :video_game:",
    description = data_manager.get_list_string(),
    color = discord.Color.blue()
  )
  if len(data_manager.get_list()) == 0:
    embed.set_thumbnail(url = "https://c.tenor.com/qx2ywkzWiV0AAAAd/marc-rebillet-rebillet.gif")
  await ctx.send(embed=embed)

@bot.command()
async def set(ctx):
  title = ctx.message.content.split("!set ",1)[1]
  data_manager.set_weekly_game(title)
  await ctx.channel.send("This week's game set to {}".format(title))

@bot.command()
async def modify(ctx):
  # remove user message
  await ctx.message.delete()

  # Reset selected game and status to None
  global selected_game
  global selected_status
  global modify_message_id
  selected_game = None
  selected_status = None

  # If there is another modify message, delete it first
  if modify_message_id != None:
    last_modify_msg = await ctx.channel.fetch_message(modify_message_id)
    await last_modify_msg.delete()
    modify_message_id = None

  # send modify message
  message = await ctx.send(
    "Select a status, then choose a game to modify",
    components = [
      # Row 1 - Status Selection
      Select(
        placeholder = "Select a status",
        options = [
          SelectOption(label = "Unplayed", value = 0),
          SelectOption(label = "Played", value = 1)
        ],
        custom_id = "status_select"
      )
    ],
  )
  # Save message id for later deletion
  modify_message_id = message.id


########################################################################
##################### U T I L I T Y   M E T H O D S ####################
########################################################################

# Returns updated components for use in modify messages
def construct_updated_components(status : int):
  game_select_state = False
  
  # get list of games
  game_list = data_manager.get_list()[status]

  game_options = []
  # if list contains games
  if len(game_list) > 0:
    # populate game option list
    for i in game_list:
      game_options.append(SelectOption(label = i, value = i))
  else:
    option_list = None
    game_select_state = True

  # create component array
  components = [
    # Row 1 - Status Selection
    [
      Select(
        placeholder = "Select a status",
        options = [
          SelectOption(label = "Unplayed", value = 0, default = not(bool(selected_status))),
          SelectOption(label = "Played", value = 1, default = bool(selected_status))
        ],
        custom_id = "status_select",
      )
    ],
    # Row 2 - Game selection
    [
      Select(
        placeholder ="Select a game",
        options = game_options,
        custom_id = "game_select",
        disabled = game_select_state
      ),
    ],
    # Row 3 - Modification buttons
    [
      Button(
        label = "Mark played",
        style = 3,
        custom_id = "played_button",
        disabled = bool(selected_status)
      ),
      Button(
        label = "Mark unplayed",
        style = 1,
        custom_id = "unplayed_button",
        disabled = not(bool(selected_status))
      ),
      Button(
        label = "Remove",
        style = 4,
        custom_id = "remove_button"
      ),
      Button(
        label = "Cancel",
        style = 2,
        custom_id = "cancel_button"
      )
    ]
  ]
  return components

keep_alive()
bot.run(token)