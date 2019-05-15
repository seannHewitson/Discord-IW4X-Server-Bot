#   Import required libraries.
import discord, requests, asyncio, json

#   Version
botVersion = "1.1"
#   Create discord bot.
client = discord.Client()

#   Load names file
with open("settings.json") as f:
    setting = json.load(f)

#   Define users as open list for users to opt in an out of offline notifications.
users = []
#   Define offline as open dict used to prevent spam of offline notificatoins.
offline = {}
#   User Details.
#   Bot Game (What to say your bot is playing in discord).
#   Example:    botGame = "IW4X: Seann's Server"
botGame = ""
#   Your Server IP address (start with ).
#   Example: ip = "98.76.54.32"
ip = ""
#   An array of ports for your server(s).
#   Example: ports = ["28961", "28962", "28963"]
ports = [""]
#   Bot Token
# token = "YOUR_BOT_TOKEN"
#   Define server as dict of servers ID'd by ports.
servers = {}
#   Iterate through ports
for i in range(0, len(ports)):
    #   Set defaults for each server/port
    servers[ports[i]] = {"status": False};

def getEmbed(port):
    #   Check if server is online.
    if servers[port]["status"] == True:
        #   Create Embed with joinable title.
        embed = discord.Embed(title=servers[port]["name"], url="http://%s/redir/?ip=%s&port=%s" % (ip, ip, port), description="ONLINE", color=0x40ff40)
        #   Add Field Players.
        embed.add_field(name="Players", value="%s/%s" % (servers[port]["players"], servers[port]["maxplayers"]), inline=True)
        #   Convert console gametype name to Actual gametype name.
        if servers[port]["gametype"] in setting["gametype"]:
            servers[port]["gametype"] = setting["gametype"][servers[port]["gametype"]]
        #   Add Field Gametype.
        embed.add_field(name="Gametype", value=servers[port]["gametype"], inline=True)
        #   Convert console mapname to Actual mapname.
        if servers[port]["map"] in setting["map"]:
            #   Set Thumbnail to map if image exists.
            embed.set_thumbnail(url=setting["map"][servers[port]["map"]]["image"])
            servers[port]["map"] = setting["map"][servers[port]["map"]]["name"]
        #   Add Field Map.
        embed.add_field(name="Map", value=servers[port]["map"], inline=True)
    else:
        if "name" in servers[port]:
            #   If name exists send message "SERVERNAME" is offline.
            embed = discord.Embed(title="%s, Offline" % servers[port]["name"], color=0xff4040)
        else:
            #   Else send message "SERVERPORT" is offline.
            embed = discord.Embed(title="Server at port: %s" % port, description="Offline", color=0xff4040)
    return embed
#   Server Status Loop.
async def serverStatus():
    #   Waittill Bot is Ready before proceeding.
    await client.wait_until_ready()
    #   Continue loop until bot is closed.
    while not client.is_closed:
        #   Loop through servers by key.
        for s in servers:
            #   Try/catch exception to catch any errors and prevent bot crash.
            try:
                #   Define req as a get httpRequest, setting timeout to 1s.
                req = requests.get("http://%s:%s/info" % (ip, s), timeout=1)
                #   Check request status is 200 / Okay.
                if req.status_code == 200:
                    #   Set server status to true/online.
                    servers[s]["status"] = True
                    #   Check if server was offline.
                    if s in offline:
                        #   Delete from offline list (so messages can be sent next time it goes off).
                        del offline[s]
                    #   Define data as json conversion of html output.
                    data = req.json()
                    #   Get Server name.
                    servers[s]["name"] = data["status"]["sv_hostname"]
                    #   Remove Colour codes from server name.
                    for c in setting["color"]:
                        servers[s]["name"] = servers[s]["name"].replace("^%s" % c, "")
                    #   Get Number of players
                    servers[s]["players"] = len(data["players"])
                    #   Get Max Players
                    servers[s]["maxplayers"] = data["status"]["sv_maxclients"]
                    #   Get Server Gametype
                    servers[s]["gametype"] = data["status"]["g_gametype"]
                    #   Get mapname
                    servers[s]["map"] = data["status"]["mapname"]
                else:
                    #   Set Current Server to offline.
                    servers[s]["status"] = False
            except requests.exceptions.RequestException as e:
                #   Catch exception define as bullshit error which wont be used.
                servers[s]["status"] = False
                servers[s]["error"] = "Unhandled Exception"
            #   ping users if server is offline.
            if servers[s]["status"] == False:
                #   Loop through users who opted into for server offline notifications.
                if s not in offline:
                    for user in users:
                        #   Send message to user.
                        #   Send message to otped in users.
                        await client.send_message(user, embed=getEmbed(s))
                        offline[s] = "Sent"
        await asyncio.sleep(10)
#   Bot Start up.
@client.event
async def on_ready():
    print("Discord-IW4X Server Bot")
    print("v%s" % botVersion)
    print("Created By Seann.")
    print("Ready!")
    await client.change_presence(game=discord.Game(name=botGame))

#   Message Actions
@client.event
async def on_message(message):
    #   Check if message sender is bot.
    if message.author == client.user:
        return
    msg = message.content.lower()
    #   Server Status Command.
    if msg == "!status":
        #   Loop through servers.
        for server in servers:
            #   Privately send message to user.
            await client.send_message(message.author, embed=getEmbed(server))
    if msg == "!pingme":
        if message.author not in users:
            users.append(message.author)
            embed = discord.Embed(title="Ping Ping", description="You will be notified when a server goes down.", color=0x4040ff)
        else:
            users.pop(users.index(message.author))
            embed = discord.Embed(title="Ping Ping", description="You will be no longer be notified when a server goes down.", color=0x4040ff)
        await client.send_message(message.author, embed=embed)
#   Bot Load Looped function.
client.loop.create_task(serverStatus())
#   Run bot using bot token as argument.
client.run(token)
