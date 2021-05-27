import discord
from discord.ext import commands
import asyncio
import json
import re
import logging
global modules
modules = {}
modules["swear"] = True
modules["lol"] = True

bad_words = []
users = {}
# Compsup 2021
logging.basicConfig(filename="logfile.log", format='%(asctime)s %(message)s', filemode='a')
logger=logging.getLogger()
logger.setLevel(logging.WARN)
# Retrive all the badwords
with open('listfile.txt', 'r') as file:
    filecontents = file.readlines()

    for line in filecontents:
        # remove linebreak which is the last character of the string
        badword = line[:-1]

        # add item to the list
        bad_words.append(badword)

intents = discord.Intents().all()
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix='?', intents=intents)
@bot.event
async def on_ready():
    await settings_manager("load")

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name='Messages'))
    logger.debug("Ready!")

async def user_strike_manager(message, users):
    time = 600
    user = message.author.id
    if user not in users:
        users[user] = 1
    else:
        users[user] += 1
        if users[user] >= 3:
            logger.debug("User: " + str(message.author) + " has been muted due to maxing strikes")
            print("User: " + str(message.author) + " has maxed there strikes!")
            member = message.author
            role = discord.utils.get(member.guild.roles, name="BAD BAD")
            await member.add_roles(role)
            embed = discord.Embed(title=f"{member}", description=f"has been muted from text and voice for {time} seconds", color=0xFF5733)
            await message.channel.send(embed=embed)
            await asyncio.sleep(time)
            await member.remove_roles(role)
            embed = discord.Embed(title=f"Unmuted", description=f"You have been unmuted in {message.guild}", color=0x258E70)
            await member.send(embed=embed)
            users[user] = 0
            logger.debug("User: " + str(message.author) + " has been unmuted.")
async def settings_manager(arg):
    global modules
    if arg == "save":
        logger.debug("Saving Settings")
        with open("settings.json", "w") as file:
            data = json.dumps(modules, indent=4)
            file.write(data)
    if arg == "load":
        # Try reading, if it fails try creating the file.
        try:
            with open("settings.json", "r") as file:
                data = file.read()
                modules = json.loads(data)
                logger.debug("Loaded Settings")
        except:
            logger.warn("Reading failed, trying to create settings.json.")
            with open("settings.json", "w") as file:
                data = json.dumps(modules, indent=4)
                file.write(data)
                logger.debug("Created settings.json and saved.")

@bot.event
async def on_message(message):
    message_content = message.content.lower()
    # Ignore empty messages like photos
    if message_content == "":
        return
    if modules["lol"]:
        if message_content == "lol" and str(message.author.id) == "756569562677510175":
            await message.channel.send('All hail TurtleDude!')
            logger.debug(f"Lol triggered")
    if message.author == bot.user:
        return
    if str(message.channel.id) == "766025171038896128":
        if message.content.isnumeric():
            counting = {
                "last_user": "",
                "current_num": 0,
            }
            with open("counting.json", "r") as f:
                try:
                    counting = json.load(f)
                except:
                    with open("counting.json", "w") as f:
                        json.dump(counting, f)
            counting["current_num"] += 1
            if str(message.content) == str(counting["current_num"]) and str(message.author) != counting["last_user"]:
                await message.add_reaction("✅")
                counting["last_user"] = str(message.author)
                with open("counting.json", "w") as f:
                    json.dump(counting, f)
            elif str(message.author) == counting["last_user"]:
                await message.add_reaction("❌")
                await message.channel.send(f'{message.author.mention} counted twice!')
                with open("counting.json", "w") as f:
                    counting["current_num"] = 0
                    counting["last_user"] = ""
                    json.dump(counting, f)
                    logger.debug("Counting reset to 0")
            else:
                await message.add_reaction("❌")
                await message.channel.send(f'{message.author.mention} put in a wrong number! The next number was {counting["current_num"]}')
                with open("counting.json", "w") as f:
                    counting["current_num"] = 0
                    counting["last_user"] = ""
                    json.dump(counting, f)
                    logger.debug("Counting reset to 0")

    if modules["swear"]:
        logger.debug("Swear triggered")
        Admin = discord.utils.get(message.guild.roles, name="Admin")
        bot_builder = discord.utils.get(message.guild.roles, name="Bot Builder")
        # Exempt og_squad and bot builder
        if not Admin in message.author.roles:
            if not bot_builder in message.author.roles:
                # loop through badword and check if any of the words appear in the message
                message_content = re.sub('[-?!*.,@#]', '', message_content)
                message_content = message_content.split(" ")
                for word in message_content:
                    if word in bad_words:
                        await message.delete()
                        await user_strike_manager(message, users)
                        print("Bad Word " + word + " " + str(message.author) + " said " + str(message.content))
                        logger.debug("Bad Word " + word + " " + str(message.author) + " said " + str(message.content))
                        return
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")
@bot.command()
async def pog(ctx):
    not_pog = discord.utils.get(ctx.guild.roles, name="Not Poggers")
    pog = discord.utils.get(ctx.guild.roles, name="POGGERS")
    kinda_pog = discord.utils.get(ctx.guild.roles, name="Kinda Pog")
    if pog in ctx.author.roles:
        await ctx.send("Your very pog!")
    elif not_pog in ctx.author.roles:
        await ctx.send("Doesn't look like your very pog.")
    elif kinda_pog in ctx.author.roles:
        await ctx.send("Your kinda pog")
    
@bot.command()
async def poll(ctx, seconds: int, *, question: str):
    poll_upthumb = 0
    poll_downthumb = 0
    await ctx.message.delete()
    embed = discord.Embed(title=f'Poll - {ctx.author}', description=f"{question}\n\n Yes/No({str(seconds)}seconds)", color=0xC9DEF2)
    msg = await ctx.send(embed=embed)
    messageid = msg.id
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')
    await asyncio.sleep(seconds)
    message = await ctx.fetch_message(messageid)
    for emoji in message.reactions:
        if str(emoji) == "👍":
            poll_upthumb = emoji.count
        elif str(emoji) == "👎":
            poll_downthumb = emoji.count
    poll_upthumb -= 1
    poll_downthumb -= 1
    embed = discord.Embed(title=f'Poll Results', description=f"{question}\n\nYes: {poll_upthumb}\n No: {poll_downthumb}", color=0x002abf)
    await ctx.send(embed=embed)

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
    muterole = discord.utils.get(member.guild.roles, name="BAD BAD")
    await member.add_roles(muterole)
    embed = discord.Embed(title=f"{member}", description=f"has been muted from text and voice for {int(time)} seconds", color=0xFF5733)
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction("🇾")
    await msg.add_reaction("🇪")
    await msg.add_reaction("🇸")
    await asyncio.sleep(int(time))
    await member.remove_roles(muterole)
@bot.command()
@commands.has_any_role('Admin', 'Bot Builder')
async def unmute(ctx, member : discord.Member):
    '''
    Unmutes a user
    '''
    muterole = discord.utils.get(member.guild.roles, name="BAD BAD")
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
