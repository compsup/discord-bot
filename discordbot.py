import discord
from discord.ext import commands
import asyncio
import json
global bad_words
global modules
global muted_users
muted_users = []
modules = {}
modules["swear"] = True
modules["lol"] = True

bad_words = []
users = {}
    
with open('listfile.txt', 'r') as file:
    filecontents = file.readlines()

    for line in filecontents:
        # remove linebreak which is the last character of the string
        badword = line[:-1]

        # add item to the list
        bad_words.append(badword)

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='?', intent=intents)
@bot.event
async def on_ready():
    await settings_manager("load")
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name='Messages'))
class User:
  def __init__(self, name, strikes):
    self.name = name
    self.strikes = 0
async def user_strike_manager(message, users):
    user = message.author.id
    if user not in users:
        users[user] = 1
        print("created " + str(user))
    else:
        users[user] += 1
        print("added 1 to " + str(user))
        if users[user] >= 3:
            print("User: " + str(message.author) + " has maxed there stikes!")
            member = message.author
            role = discord.utils.get(member.guild.roles, name="BAD BAD")
            await member.add_roles(role)
            await message.channel.send(str(member) + " has been muted from text and voice.")
            await asyncio.sleep(600)
            await member.remove_roles(role)
            users[user] = 0
async def settings_manager(arg):
    global modules
    if arg == "save":
        with open("settings.json", "w") as file:
            data = json.dumps(modules, indent=4)
            file.write(data)
    if arg == "load":
        try:
            with open("settings.json", "r") as file:
                data = file.read()
                modules = json.loads(data)
        except:
            with open("settings.json", "w") as file:
                data = json.dumps(modules, indent=4)
                file.write(data)

@bot.event
async def on_message(message):
    await message.guild.me.edit(nick='Doge Boy')
    if message.author in muted_users:
        print(muted_users)
        await message.delete()
    message_content = message.content.lower()
    if message_content == "":
        return
    if modules["lol"]:
        if message_content == "lol" and str(message.author.id) == "756569562677510175":
            await message.channel.send('All hail TurtleDude!')
    if message.author == bot.user:
        return

    if modules["swear"]:
        og_squad = discord.utils.get(message.guild.roles, name="OG Squad")
        bot_builder = discord.utils.get(message.guild.roles, name="Bot Builder")
        if og_squad in message.author.roles or bot_builder in message.author.roles:
            return
        message_stripped = message_content.replace(" ", "")
        for bad_word in bad_words:
            if str(message_stripped).find(bad_word) != -1:
                await message.delete()
                await user_strike_manager(message, users)
                print("Bad Word " + bad_word + " " + str(message.author) + " said " + str(message.content))
                return
    await bot.process_commands(message)
@bot.command()
async def ping(ctx):
    await ctx.send("pong!")
@bot.command()
@commands.has_any_role('Admin', 'Bot Builder')
async def stop(ctx, arg):
    global modules
    if str(arg) == "swear":
        modules["swear"] = False
        await ctx.send("Swear Module Stopped")
        await settings_manager("save")
    elif str(arg) == "lol":
        modules["lol"] = False
        await ctx.send("Lol Module Stopped")
        await settings_manager("save")
@bot.command()
@commands.has_any_role('Admin', 'Bot Builder')
async def start(ctx, arg):
    global modules
    if str(arg) == "swear":
        modules["swear"] = True
        await ctx.send("Swear Module Started")
        await settings_manager("save")
    elif str(arg) == "lol":
        modules["lol"] = True
        await ctx.send("Lol Module Started")
        await settings_manager("save")
@bot.command()
#@commands.has_permissions(manage_messages=True)
@commands.has_any_role('Admin', 'Bot Builder')
async def purge(ctx, arg):
    await ctx.channel.purge(limit=int(arg), bulk=True)
@bot.command()
#@commands.has_permissions(manage_messages=True)
@commands.has_any_role('Admin', 'Bot Builder')
async def tempmute(ctx, member : discord.Member, time):
    global muted_users
    muterole = discord.utils.get(member.guild.roles, name="BAD BAD")
    await member.add_roles(muterole)
    muted_users.append(member)
    await ctx.channel.send("@" + str(member) + " has been muted from text and voice.")
    await asyncio.sleep(int(time))
    await member.remove_roles(muterole)
    muted_users.remove(member)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("No private messages.")
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send("You don't have the permissions to do that!")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("You don't have the permissions to do that!")
    else:
        await ctx.send(error)
bot.run('NzQ1MDI3NTYyMTY1NzY0MTg3.Xzry_A.78kdjcfpxvKsbQh772OyPnFG9Kc')
