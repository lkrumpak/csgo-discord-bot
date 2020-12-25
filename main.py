import asyncio
import subprocess
import json
import discord
from discord.ext import commands, tasks
import a2s


class server_info:
    def __init__(self, config):
        self.config = config
        self.ip_address = config.get('server_ip')
        self.server_port = config.get('server_port')

    def get(self):
        try:
            server_info = a2s.info((self.ip_address, self.server_port))
            self.server_name = server_info.server_name
            self.connect_link = 'steam://connect/' + str(self.ip_address) + ':' + str(self.server_port) + '/'
            self.curr_map = server_info.map_name.split('/')[-1]
            self.players = str(server_info.player_count) + '/' + str(server_info.max_players)
            self.ping = str(int((server_info.ping * 1000))) + 'ms'
        except:
            self.server_name = '-'
            self.connect_link = 'Server is Offline :('
            self.curr_map = 'Unknown'
            self.players = '-1'
            self.playerstats = 'Unknown'
            self.ping = '-1ms'


with open("config.json") as json_file:
    config = json.load(json_file)

client = commands.Bot(command_prefix=config.get('command_prefix'))
server_info = server_info(config)
server_info.get()
reactions = ["▶️", "⏹️", "🔁"]


@client.event
async def on_ready():
    channel = client.get_channel(config.get('channel_id'))

    embed = discord.Embed(title='Counter Strike : Global Offensive',color=discord.Color.orange())
    embed.add_field(name='\u200b', value='Connecting . . .', inline=False)
    msg = await channel.send(embed=embed)
    msg_id = {"message_id": msg.id}
    config.update(msg_id)

    for reaction in reactions:
        await msg.add_reaction(reaction)

    update_status.start()


@client.event
async def on_reaction_add(reaction, user):
    if user != client.user:
        if reaction.emoji == "▶️":
            subprocess.run(["./csgoserver", "start"])
            description = 'Starting Server . . .'
        elif reaction.emoji == "⏹️":
            subprocess.run(["./csgoserver", "stop"])
            description = 'Stopping Server . . .'
        elif reaction.emoji == "🔁":
            subprocess.run(["./csgoserver", "restart"])
            description = 'Restarting Server . . .'
        else:
            await reaction.remove(user)
            return
    # todo: add a sleep to wait for server info and restart task\

        if reaction.emoji in reactions:
            color = discord.Color.orange()
            embed = discord.Embed(title='Counter Strike : Global Offensive', color=color)
            embed.add_field(name='\u200b', value=description, inline=False)
            await reaction.message.edit(embed=embed)
        await asyncio.sleep(20)
        update_status.restart()


@tasks.loop(seconds=config.get('refresh_time'))
async def update_status():
    server_info.get()

    channel = client.get_channel(config.get('channel_id'))
    msg = await channel.fetch_message(config.get('message_id'))

    if server_info.players == '-1':
        color = discord.Color.red()
        activity_status = 'Server Offline :('
    else:
        color = discord.Color.green()

        activity_status = server_info.curr_map + ' | ' + server_info.players

    embed = discord.Embed(title='Counter Strike : Global Offensive', color=color)
    embed.set_image(url=config.get('server_image'))
    embed.add_field(name=server_info.server_name, value=server_info.connect_link, inline=False)
    embed.add_field(name='Map', value=server_info.curr_map, inline=True)
    embed.add_field(name='Players', value=server_info.players, inline=True)
    embed.add_field(name='Ping', value=server_info.ping, inline=True)

    await msg.edit(embed=embed)
    update_status.change_interval(seconds=600)
    await client.change_presence(activity=discord.Game(name=activity_status))

client.run(config.get('token'))
