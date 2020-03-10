import os
import asyncio
import sys
import json
import discord
import youtube_dl
import subprocess
import random
from random import choice
from discord.ext import commands
from dotenv import load_dotenv

if not discord.opus.is_loaded():
    #discord.opus.load_opus('opus')
    pass

ytdl_format_options = {'format': 'bestaudio/best',
                       'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                       'restrictfilenames': True,
                       'noplaylist': True,
                       'nocheckcertificate': True,
                       'ignoreerrors': False,
                       'logtostderr': False,
                       'quiet': True,
                       'no_warnings': True,
                       'default_search': 'auto',
                       'source_address': '0.0.0.0'}

ffmpeg_options = {'before_options': '-nostdin', 'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

load_dotenv()
if (len(sys.argv) > 1):
    TOKEN = os.getenv('DISCORD_TOKEN_TWO')
    PREFIX  = os.getenv('PREFIX_TWO')
else:
    TOKEN = os.getenv('DISCORD_TOKEN')
    PREFIX = os.getenv('PREFIX')

GUILD = os.getenv('DISCORD_GUILD')
client = commands.Bot(command_prefix = PREFIX)

DEFAULT_VIEW = [4, 1, 4]
voiceChannel = None
textChannel = None
normalNext = True
inform = True
path = './music/'
#print(os.listdir(path))
# song = []
# for i in os.listdir(path):
#     if i[-3:] == 'mp3':
#         song.append(i)

songs = asyncio.Queue()
play_next_song = asyncio.Event()


async def audio_player_task():
    global normalNext
    global inform
    nomalNext = True

    while True:
        print('Go')
        play_next_song.clear()
        current = await songs.get()

        if current[1] == "None":
            await playSong(textChannel)
        elif current[1] == 'url':
            await textChannel.send('TODO')
            pass
        else:
            print(current)

        if current[0][:-4] != "" and inform:
            await textChannel.send('Now playing: {}'.format(current[0][:-4]))

        print('Playing and wating')
        await play_next_song.wait()
        print('Next like normal:', normalNext)

        if normalNext:
            await nextSong()

        normalNext = True


def toggle_next():
    client.loop.call_soon_threadsafe(play_next_song.set)


@client.command()
async def play(ctx):
    if voiceChannel != None:
        await updateControls(ctx, 'play')
        await addToQueue(getSong(), "None")
    else:
        await ctx.send("```Not connected```")

@client.command()
async def addToQueue(song, url):
    await songs.put([song, url])


# stream TODO Replace with stream
@client.command()
async def Play(ctx, url):
    if voiceChannel == None:
        await join(ctx)

    #player = self.players[ctx.guild.id]

   #player = await from_url(url, loop=client.loop, stream=True)
    player = await voiceChannel.create_ytdl_player(url, after=toggle_next())
    await songs.put(player)
    #source = await YTDLSource.create_source(ctx, search, loop=bot.loop, download=False)
    #await songs.queue.put(source)

# read write updating the queue
# reads the queue and returns it
def loadQueue():
    with open(path + 'queue.json', 'r') as inFile:
        queue = json.load(inFile)

    return queue

# writes to the queue.json the new queue
def writeQueue(queue):
    with open(path + 'queue.json', 'w') as outFile:
        outFile.write(json.dumps(queue, indent=4, sort_keys=True))

# runs the music logger to log the mp3 files
def loadMusic():
    subprocess.call(['python3', 'music/musicLogger.py', 'log'])

# runs the music logger to make queue
def makeQueue():
    subprocess.call(['python3', 'music/musicLogger.py', 'queue'])


# gets the cur song from queue
def getSong():
    queue = loadQueue()

    return queue['cur']

# checks if anything is left
def done():
    # TODO add a queue ended msg
    again = True

    queue = loadQueue()

    if len(queue['songs']) == 0:
        again = False

    return again


async def nextSong(add=True):
    again = done()

    queue = loadQueue()

    #print(queue)

    past = queue['past']
    cur = queue['cur']
    songs = queue['songs']

    #print(json.dumps(queue, indent=4, sort_keys=True))

    #print(songs)

    if again:
        if cur != "":
            past.append(cur)
        cur = songs[0]
        songs.pop(0)

        queue['past'] = past
        queue['cur'] = cur
        queue['songs'] = songs

        writeQueue(queue)
        #print(json.dumps(queue, indent=4, sort_keys=True))

        if add:
            await addToQueue(cur, 'None')


    return again

async def changeActivity(activity):
    sutats = discord.Status.online
    game = discord.Game(activity)
    await client.change_presence(status=sutats, activity=game)

#client = discord.Client()

# on ready
@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    sutats = discord.Status.dnd
    activity = discord.Game(" nothing")
    await client.change_presence(status=sutats, activity=activity)
    print(
        f'{client.user} has connected to Discord!\n'
        f'{guild.name}(id : {guild.id})'
    )

#@client.event
#async def on_message(message):
#    if (message.author != message.author.bot and
#        message.content.startswith(PREFIX)):
#        print(message.content)

# on message do stuff
@client.event
async def on_message(message):
    if message.author == message.author.bot:
        return
    if not message.content.startswith(PREFIX):
        return

    print(message.author, message.content)
    await client.process_commands(message)


#    msg = message.content[1:]
#    print(msg)
#
#    if msg == 'ping':
#        await message.channel.send('pong')
#    elif msg == 'kill':
#        await message.channel.send('Thou hast smote me')
#        sys.exit("I have become deaded.")

# Start controls
@client.command()
async def start(ctx):
    global voiceChannel
    global textChannel
    if voiceChannel == None:
        await join(ctx)

    if voiceChannel.is_paused():
        await ctx.send("```Resuming song!```")
        voiceChannel.resume()

    elif not voiceChannel.is_playing():
        await show(ctx)
        await play(ctx)
        #await ctx.send("Starting")
        print('Starting normally')

    else:
        await ctx.send("```Alreading Playing!```")

# reads the directory and writes the songs to json
@client.command()
async def read(ctx):
    loadMusic()

# reads song json and loads to queue json
@client.command()
async def write(ctx):
    makeQueue()

# should kill the bot
@client.command()
async def kill(ctx):
    await leave(ctx)
    await ctx.channel.send('Thou hast smote me.')
    sys.exit("I have become deaded")
    sys.exit("I should be dead rn")
    sys.exit("LIke really why is this showing")

# REMOVE, equivalent to skip
@client.command()
async def next(ctx):
    global voiceChannel
    global normalNext
    again = done()

    print(again)
    if again and voiceChannel != None:
        #await nextSong()
        normalNext = True
        print(voiceChannel)
        if voiceChannel.is_playing():
            voiceChannel.stop()
        #await playSong(ctx)

    elif not again and not voiceChannel == None:
        await ctx.send("Queue ended")

    else:
        await ctx.send("```Not Connected!```")

# sends the current song or none
@client.command()
async def cur(ctx):
    txt = "Not Playing"
    if voiceChannel.is_playing():
        txt = "Playing " + getSong()[:-4]

    await ctx.send(txt)


def makeQueueEmbed(viewPortShift, viewPort=9):
    em = discord.Embed(title="  "*20+ "Queue:", color=9849600)

    queue = loadQueue()

    past = queue['past']
    cur = queue['cur']
    futr = queue['songs']

    if viewPortShift < -(len(past) - viewPort // 2):
        viewPortShift = -(len(past) - viewPort // 2)

    if viewPortShift > len(futr) - viewPort // 2:
        viewPortShift = len(futr) - viewPort // 2

    start = len(past)
    blob = past + [cur] + futr
    #print(blob, "   ", blob[start])

    #print(blob)
    view = blob[start - viewPort // 2 + viewPortShift
        : start + 1 + viewPort // 2 + viewPortShift]
    #print(json.dumps(blob, indent=4, sort_keys=True))
    #print(json.dumps(view, indent=4, sort_keys=True))

    queueView = ""
    numbers = ""

    #print(start, viewPort // 2 + viewPortShift)
    num = start - viewPort // 2 + viewPortShift - (start + 1)
    for i in range(len(view)):
        num += 1

        if view[i] == cur:
            numbers += "**%d**\n" % num
            queueView += "**%s**\n" % view[i][:-4]

        else:
            numbers += "%d\n" % num
            queueView += "%s\n" % view[i][:-4]

    header = "__Name:" + (' ' * 80) + "%d:%d__" % (-len(past), len(futr))
    em.add_field(name="__ # __", value=numbers, inline=True)
    em.add_field(name=header, value=queueView, inline=True)

    return em



@client.command()
async def all(ctx):
    allSongs = "```"
    queue = loadQueue()
    num = 1

    for i in queue['past']:
        allSongs += '%d %s\n' % (num, i)
        num += 1

    allSongs += '**%d %s**\n' % (num, queue['cur'])
    num += 1

    for i in queue['songs']:
        allSongs += '%d %s\n' % (num, i)
        num += 1

    allSongs += "```"
    print(allSongs)
    await ctx.send(allSongs)

async def convert(ctx, arg):
    usage = 0
    viewPort = 9

    # check for no args
    if len(arg) == 0:
        ID = 0
    else:
        ID = arg[0]
        arg = list(arg[1:])

    # p show max past, f max future, c is custom
    if ID == "p":
        usage = -30
        viewPort = -30

    elif ID == "f":
        usage = 30
        viewPort = 30

    elif ID == "c":
        stop = False

        for i in range(len(arg)):
            try:
                arg[i] = int(arg[i])
            except ValueError:
                print(i, "be a string")
                stop = True

        if not stop or not len(arg) == 0:
            usage = arg[0]
            viewPort = arg[1]

        else:
            await ctx.send("Usage: ```%sshow c num num```" % PREFIX)
    # defaults to normal view try catch to make sure its a number
    else:
        try:
            usage = int(ID)

        except ValueError:
            print(ID, "be a string")
            await ctx.send("Usage: ```%sshow c num num```" % PREFIX)


    return usage, viewPort

controlID = [None, 0, "left", None]
@client.command()
async def show(ctx, *argv):
    global controlID

    move, view = await convert(ctx, argv)

    #print(move, view)
    msg = await ctx.send(embed=makeQueueEmbed(move, viewPort=view))
    controlID[0] = msg.id

    audioControlsList = ['⬅️', '➡️', '⏪', '⏩']
    for i in audioControlsList:
        await msg.add_reaction(i)

    await updateControls(ctx, controlID[2])

#the queue loader
@client.command()
async def q(ctx):
    global normalNext
    queue = loadQueue()
    args = ctx.message.content.split(" ")[1:]
    if len(args) != 0:

        selection = int(args[0])
        print(selection)

        if selection > 0:
            if selection > len(queue['songs']):
                selection = len(queue['songs'])
                print('Overload going to the end of queue')

            else:
                print('Going forward')

            for i in range(abs(selection)):
                await nextSong(add=False)

            await show(ctx)

            normalNext = False

            voiceChannel.stop()
            await play(ctx)



        elif selection < 0:
            if abs(selection) > len(queue['past']):
                selection = len(queue['past'])

            else:
                print('Going back')

            for i in range(abs(selection)):
                queue = previous(queue)

            #print(json.dumps(queue, indent=4, sort_keys=True))
            writeQueue(queue)

            await show(ctx)

            normalNext = False

            voiceChannel.stop()
            await play(ctx)

        else:
            await ctx.send('You are an absolute moron')

    else:
        print('No args: showing')
        await show(ctx)

@client.command()
async def c(ctx):
    pollEmoji = ['👍', '👎']
    audioControlsList = ['➡️', '⬅️', '▶️', '▶️']
    numberList = ['0️⃣','1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

    await show(ctx)

def getName(raw):
    queue = loadQueue()
    return('ur dumb')

@client.command()
async def rmSong(ctx, *, args: getName):
    print(args)

polls = []
@client.command()
async def poll(ctx):
    global polls
    pollEmoji = ['👍', '👎']
    user = choice(ctx.message.channel.guild.members)


    txt = 'Kill %s' % user.mention
    msg = await ctx.send('Kill %s' % user.mention)
    polls.append([msg.id, 0, 0, 3, txt])

    for i in pollEmoji:
        await msg.add_reaction(i)

@client.event
async def on_reaction_add(reaction, user):
    global polls
    if user.bot:
        return
    print('Reaction added')
    print(polls)
    for i in range(len(polls)):
        if reaction.message.id == polls[i][0] and not user.bot:
#            print(reaction, '👎', reaction.emoji == '👎')
#            print(reaction, '👍', reaction.emoji == '👍')
            if reaction.emoji == '👎':
                polls[i][2] += 1

            elif reaction.emoji == '👍':
                polls[i][1] += 1

    rmPolls = []

    for i in range(len(polls)):
        obj = polls[i]
        if obj[1] >= obj[3]:
            await reaction.message.channel.send('We shall ' + obj[4] + "!")
            rmPolls.append(i)

        elif obj[2] >= obj[3]:
            await reaction.message.channel.send("We shall not " + obj[4] + "!")
            rmPolls.append(i)

    rmPolls.sort(reverse = True)

    for i in range(len(rmPolls)):
        polls.pop(i)

    audioControlsList = ['⬅️', '➡️', '▶️', '⏸️', '⏹️', '⏪', '⏩']

    if reaction.message.id == controlID[0]:
        global inform
        if reaction.emoji == audioControlsList[0]:
            controlID[1] -= 2

        elif reaction.emoji == audioControlsList[1]:
            controlID[1] += 2

        elif reaction.emoji == audioControlsList[2]:
            await resume(controlID[3])
            inform = False
            print('resume')

        elif reaction.emoji == audioControlsList[3]:
            await pause(controlID[3])
            inform = False
            print('pause')

        elif reaction.emoji == audioControlsList[4]:
            print('start')
            inform = False
            await start(controlID[3])

        elif reaction.emoji == audioControlsList[5]:
            print('last')
            inform = False
            await last(controlID[3])
            await play(controlID[3])

        elif reaction.emoji == audioControlsList[6]:
            print('next')
            inform = False
            voiceChannel.stop()


        #print('the end is here')
        await reaction.remove(user)
        await reaction.message.edit(embed=makeQueueEmbed(controlID[1]))


    print(controlID)
    print(reaction)
    print(user)
    print(polls)

@client.event
async def on_reaction_remove(reaction, user):
    global poll
    print(poll)

async def updateControls(ctx, to):
    if controlID[0] != None:

        controlID[3] = ctx

        msg = await ctx.channel.fetch_message(controlID[0])

        for i in msg.reactions:
            print(i)

        if len(msg.reactions) != 4:
            await msg.clear_reaction(msg.reactions[4])

        pp = ['▶️', '⏸️', '⏹️']
        if to == "play":
            await msg.add_reaction(pp[1])
            controlID[2] = "pause"

        elif to == "pause":
            await msg.add_reaction(pp[0])
            controlID[2] = "play"

        elif to == "left":
            await msg.add_reaction(pp[2])
            controlID[2] = "left"




@client.command()
async def reset(ctx):
    global voiceChannel
    global textChannel
    global normalNext
    await leave(ctx)

    if ctx.voice_client != None and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        voiceChannel.stop()

    normalNext = False
    voiceChannel = None
    textChannel = None

    print('setting voice and text to null')

# joins the voice channel user is in, saves textchannel for future msgs
@client.command()
async def join(ctx):
    global voiceChannel
    global textChannel
    global normalNext
    voiceChannel = await ctx.author.voice.channel.connect()
    textChannel = ctx


# plays a song from queue
#@client.command()
async def playSong(ctx):
    if voiceChannel != None:
        source = path + getSong()
        print('::::playing: ' + source)
        source = discord.FFmpegPCMAudio(source)
        source = discord.PCMVolumeTransformer(source)
        #print(os.listdir(path))

        #voiceChannel.play(source, after=lambda e: finish(e))
        voiceChannel.play(source, after=lambda e: toggle_next())
        voiceChannel.source = discord.PCMVolumeTransformer(voiceChannel.source)
        voiceChannel.source.volume = 100000
        await changeActivity(getSong()[:-4])

    else:
        print('not connected')

# the commands that handle going back a song
# goes back a song
def previous(queue):

    cur = queue['cur']
    past = queue['past']
    songs = queue['songs']
    #print(cur)
    #print(past)
    #print(songs)

    #print(json.dumps(queue, indent=4, sort_keys=True))

    if len(past) == 0:
        print('no past')
        songs.insert(0, cur)
        queue['cur'] = ''
        queue['past'] = []

    elif cur != '':
        print("cur isn't null")
        songs.insert(0, cur)

        print(past[-1])
        queue['cur'] = past[-1]
        past.pop(-1)

    #print(json.dumps(queue, indent=4, sort_keys=True))

    return queue


@client.command()
async def last(ctx):
    global normalNext
    queue = loadQueue()

    print('going back')
    if len(queue['past']) > 0:
        queue = previous(queue)

        writeQueue(queue)

        normalNext = False
        voiceChannel.stop()
    else:
        print('trying to do the impossible')
        await ctx.send('Your at the begining')


# resumes a paused song
@client.command()
async def resume(ctx):
    vc = ctx.voice_client

    if not vc.is_paused():
        await ctx.send("Not paused")
        return

    vc.resume()
    await updateControls(ctx, 'play')

    if inform:
        await ctx.send(f'**`{ctx.author}`**: Resumed song!')

# pauses a playing song
@client.command()
async def pause(ctx):
    global inform
    print('pasusef')
    vc = ctx.voice_client

    if vc.is_paused():
        await ctx.send("Already paused")
        return

    vc.pause()
    await updateControls(ctx, 'pause')

    if inform:
        await ctx.send(f'**`{ctx.author}`**: Paused song!')

# downloads a yt song, update music
@client.command()
async def add(ctx, link, *, name=None):
    print('#' * 5, ctx.message.author)

    if name == None:
        await ctx.send("Usage: ```%sadd {url} {name}```" % PREFIX)

    elif link.find('https') == -1:
        print('forcing to next')
        queue = loadQueue()

        if queue['songs'][0] != name + '.mp3':
            queue['songs'].insert(0, name + '.mp3')

            writeQueue(queue)

    else:
        print('Name:', name)

        loggerargs = ['url', link, name]
        loggerrun = ['python3', 'music/musicLogger.py']
        exitArgs = subprocess.call(loggerrun + loggerargs)
        print('exit:', exitArgs)

        if exitArgs == 1:
            await read(ctx)
            queue = loadQueue()

            queue['songs'].insert(0, name + '.mp3')
            #print(queue['songs'])

            writeQueue(queue)

        else:
            await ctx.send('```Duplicate Found!```')


    #download a youtube link

# play yt link without downloading
@client.command()
async def stream(ctx):
    print('TODO')
    #stream a youtube link

# leave the voice channel
@client.command()
async def leave(ctx):
    global voiceChannel
    global normalNext

    normalNext = False

    await updateControls(ctx, 'left')
    await ctx.voice_client.disconnect()
    await voiceChannel.disconnect()
    voiceChannel = None
    #await ctx.voice_client.disconnect()


# shuffle the songs in the future
@client.command()
async def shuffle(ctx):
    queue = loadQueue()
    random.shuffle(queue['songs'])
    writeQueue(queue)

    await show(ctx)


# add main loop to the list thing, run bot
client.loop.create_task(audio_player_task())
client.run(TOKEN)
