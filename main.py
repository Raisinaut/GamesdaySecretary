import os
import discord
import random
import data_manager
from replit import db
from keep_alive import keep_alive
from discord_components import ComponentsBot, Button, Select, SelectOption, ButtonStyle

selected_game = None # used when modifying a game from selection menu
modify_message_id = None # used to delete old message for refresh

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
  btn = interaction.custom_id
  
  if btn == "cancel_button":
    # delete last modify message
    last_modify_msg = await interaction.channel.fetch_message(modify_message_id)
    await last_modify_msg.delete()
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
        embed = discord.Embed(
          title = "Remaining Games :video_game:",
          description = data_manager.get_list_string(),
          color = discord.Color.blue()
        )
        await interaction.channel.send(embed=embed)
      else:
        await interaction.respond(content = "That game was already deleted.")

  else:
    await interaction.respond(content = "Select a game first.")

@bot.event
async def on_select_option(interaction):
  global selected_game
  selected_game = interaction.values[0]
  print(f"Selected {selected_game}")
  await interaction.respond(content = " ")
  #await interaction.respond(content=f"{selected_game} selected.", )


########################################################################
######################## B O T   C O M M A N D S #######################
########################################################################

#@bot.command()
#async def actions(ctx):
#  await ctx.channel.send(help_message)

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
  if len(data_manager.get_list([db["games"]])) == 0:
    embed.set_thumbnail(url = "https://c.tenor.com/qx2ywkzWiV0AAAAd/marc-rebillet-rebillet.gif")
  await ctx.send(embed=embed)

@bot.command()
async def set(ctx):
  title = ctx.message.content.split("!set ",1)[1]
  data_manager.set_weekly_game(title)
  await ctx.channel.send("This week's game set to {}".format(db["Weekly Game"]))

@bot.command()
async def modify(ctx):
  await ctx.message.delete()
  # Reset selected game to None
  global selected_game
  global modify_message_id
  selected_game = None

  game_list = data_manager.get_list([db["games"]])

  # If there is another modify message, delete it first
  if modify_message_id != None:
    last_modify_msg = await ctx.channel.fetch_message(modify_message_id)
    await last_modify_msg.delete()
    modify_message_id = None

  # Exit if list is empty
  if len(game_list) == 0:
    await ctx.send("There are no games to modify.")
    return

  # Construct list of options
  option_list = []
  for i in game_list:
    option_list.append(SelectOption(label = i, value = i))

  message = await ctx.send(
    "Select a game to modify",
    components = [
      # Row 1
      [
        Select(
          placeholder ="Select a game",
          options = option_list,
          custom_id = "select"
        ),
      ],
      # Row 2
      [
        Button(
          label = "Mark played",
          style = 3,
          custom_id = "played_button"
        ),
        Button(
          label = "Mark unplayed",
          style = 1,
          custom_id = "unplayed_button"
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
      ],
    ],
  )
  # Save message id for later deletion
  modify_message_id = message.id

keep_alive()
bot.run(token)