import os
import asyncio
import sys
import json
import discord
import youtube_dl
import subprocess
import random
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

voiceChannel = None
textChannel = None
normalNext = True
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

        if current[0][:-4] != "":
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
    await addToQueue(getSong(), "None")

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

# on message do stuff
#@client.event
#async def on_message(message):
#    if message.author == message.author.bot:
#        return
#    if not message.content.startswith(PREFIX):
#        return
#
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

    await play(ctx)
    await ctx.send("Starting")

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
    global normalNext
    print(ctx.voice_client)
    again = done()

    print(again)
    if again:
        #await nextSong()
        normalNext = True
        if voiceChannel.is_playing():
            voiceChannel.stop()
        #await playSong(ctx)

    else:
        await ctx.send("Queue ended")

# sends the current song or none
@client.command()
async def cur(ctx):
    txt = "Not Playing"
    if voiceChannel.is_playing():
        txt = "Playing " + getSong()[:-4]

    await ctx.send(txt)

def makeQueueEmbed(shown):
    em = discord.Embed(title="  "*20+ "Queue:", color=9849600)
    queueView = ""
    numbers = ""

    pastlen = (shown - 1) // 2
    futurelen = (shown -1) // 2

    queue = loadQueue()
    cur = queue['cur']
    past = queue['past']
    future = queue['songs']

    pastmax = len(past) - pastlen
    futuremax = len(future) - futurelen

    if pastmax < 0:
        futurelen += abs(pastmax)

    if futuremax < 0:
        pastlen += abs(futuremax)


    length = len(past)
    if len(past) > pastlen:
        length = pastlen

    for i in range(length):
        shown -= 1
        numbers += "%d\n" % (i - length)
        queueView += "%s\n" % past[-length + i][:-4]



    shown -= 1
    numbers += "**  0**\n"
    queueView += "**" + cur[:-4] + "**\n"


    length = len(future)
    if length > futurelen:
        length = futurelen

    for i in range(length):
        shown -= 1
        numbers += "  %d\n" % (i + 1)
        queueView += "%s\n" % future[i][:-4]



    #print(msg)
    #await ctx.send(json.stringify(msg))
    header = "__Name:" + (' ' * 80) + "%d:%d__" % (-len(past), len(future))
    em.add_field(name="__ # __", value=numbers, inline=True)
    em.add_field(name=header, value=queueView, inline=True)

    return em


@client.command()
async def show(ctx):
    await ctx.send(embed=makeQueueEmbed(7))

#the queue loader
@client.command()
async def q(ctx):
    global normalNext
    queue = loadQueue()
    args = ctx.message.content.split(" ")[1:]
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

        print(json.dumps(queue, indent=4, sort_keys=True))
        writeQueue(queue)

        await show(ctx)

        normalNext = False

        voiceChannel.stop()
        await play(ctx)

    else:
        await ctx.send('You are an absolute moron')

@client.command()
async def c(ctx):
    #args = ctx.message.content.split(" ")[1:]
    await ctx.send('Literly nothing')

@client.command()
async def reset(ctx):
    global voiceChannel
    global textChannel
    voiceChannel = None
    textChannel = None

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
    await ctx.send(f'**`{ctx.author}`**: Resumed song!')

# pauses a playing song
@client.command()
async def pause(ctx):
    vc = ctx.voice_client

    if vc.is_paused():
        await ctx.send("Already paused")
        return

    vc.pause()
    await ctx.send(f'**`{ctx.author}`**: Paused song!')

# downloads a yt song, update music
@client.command()
async def add(ctx):
    print(ctx.message.author)

    args = ctx.message.content.split(" ")[1:]
    print(args)

    if len(args) < 2:
        await ctx.send("Usage: ```.add {url} {name}```")
    else:
        link = args[0]
        name = " ".join(args[1:])
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
