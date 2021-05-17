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

# Compsup 2021

# Retrive all the badwords
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

async def user_strike_manager(message, users):
    time = 600
    global muted_users
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
            muted_users.append(member)
            embed = discord.Embed(title=f"{member}", description=f"has been muted from text and voice for {time} seconds", color=0xFF5733)
            await message.channel.send(embed=embed)
            await asyncio.sleep(time)
            await member.remove_roles(role)
            muted_users.remove(member)
            embed = discord.Embed(title=f"Unmuted", description=f"You have been unmuted in {message.guild}", color=0x258E70)
            await member.send(embed=embed)
            users[user] = 0
async def settings_manager(arg):
    global modules
    if arg == "save":
        with open("settings.json", "w") as file:
            data = json.dumps(modules, indent=4)
            file.write(data)
    if arg == "load":
        # Try reading, if it fails try creating the file.
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
    if message.author in muted_users:
        print(muted_users)
        await message.delete()
    message_content = message.content.lower()
    # Ignore empty messages like photos
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
        # Exempt og_squad and bot builder
        if not og_squad in message.author.roles:
            if not bot_builder in message.author.roles:
                message_stripped = message_content.replace(" ", "")
                # loop through badword and check if any of the words appear in the message
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
async def goodboy(ctx):
    if modules["goodboy"]:
        embed = discord.Embed(title="Woof", description="Thank you!", color=0xFF5733)
        await ctx.send(embed=embed)
@bot.command()
@commands.has_any_role('Admin', 'Bot Builder')
async def stop(ctx, arg):
    arg = str(arg).lower()
    global modules
    if arg in modules:
        modules[arg] = False
        await ctx.channel.send(f"{arg} has been stopped.")
        await settings_manager("save")

@bot.command()
@commands.has_any_role('Admin', 'Bot Builder')
async def start(ctx, arg):
    arg = str(arg).lower()
    global modules
    if arg in modules:
        modules[arg] = True
        await ctx.channel.send(f"{arg} has been started.")
        await settings_manager("save")

@bot.command()
@commands.has_any_role('Admin', 'Bot Builder')
async def purge(ctx, arg):
    await ctx.channel.purge(limit=int(arg), bulk=True)

@bot.command()
@commands.has_any_role('Admin', 'Bot Builder')
async def tempmute(ctx, member : discord.Member, time):
    '''
    Tempmutes a user for the amount of time
    '''
    global muted_users
    muterole = discord.utils.get(member.guild.roles, name="BAD BAD")
    await member.add_roles(muterole)
    if member not in muted_users:
        muted_users.append(member)
    embed = discord.Embed(title=f"{member}", description=f"has been muted from text and voice for {int(time)} seconds", color=0xFF5733)
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction("🇾")
    await msg.add_reaction("🇪")
    await msg.add_reaction("🇸")
    await asyncio.sleep(int(time))
    await member.remove_roles(muterole)
    muted_users.remove(member)
@bot.command()
@commands.has_any_role('Admin', 'Bot Builder')
async def unmute(ctx, member : discord.Member):
    '''
    Unmutes a user
    '''
    global muted_users

    muterole = discord.utils.get(member.guild.roles, name="BAD BAD")
    if member in muted_users:
        muted_users.remove(member)
    await member.remove_roles(muterole)
    embed = discord.Embed(title=f"Unmuted", description=f"You have been unmuted in {ctx.guild}", color=0x258E70)
    await member.send(embed=embed)
    embed = discord.Embed(title=f"{member}", description=f"has been unmuted.", color=0x258E70)
    await ctx.channel.send(embed=embed)
@bot.event
async def on_command_error(ctx, error):
    '''
    Handle common errors
    '''
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("No private messages.")
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send("You don't have the permissions to do that!")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("You don't have the permissions to do that!")
    else:
        await ctx.send(error)
with open("token.txt", "r") as file:
    token = file.read()
bot.run(token)
