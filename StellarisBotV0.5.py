# Script reads the decrompressed stellaris save file and updates discord roles and creates channels as federations are added
# Pseudocode:
# Decompress File
# Read empire names as they relate to steam names, use a .iam command to convert steam names to discord names
# create and assign empire roles to discord users
# read federation data
# Assign federation rolls to everyone in a federation and create text + voice channels for them
# Read Galactic council data
# Assign Roles to Galactic Council members

import json
import os
import discord
from discord.ext import commands
from discord.utils import get
import asyncio
from zipfile import ZipFile
#To do:
#
#   implement channel creation for federations


TOKEN = "TOKEN"
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents) # command prefix is >>
client.remove_command('help') # removes the default help command to replace it with a custom one
names = {}
discGuild = None


class saveProcessing:
    def __init__(self):
        self.path = None
        #self.saveFile = None#f"{self.path}/latest.sav"
        self.empireData = {}
        self.fedData = {}
        self.council = []
        self.lines = None
    async def unzip(self, location):
        #unzips the save file and parses the contents of gamedata into lines
        with ZipFile(location, "r") as zipObj:
            zipObj.extractall()
        #backPath = location[:location.rfind("/")]
        with open(f"gamestate", "r") as gamestate:
            self.lines = gamestate.readlines()
        # cleaning up
        os.remove("gamestate")
        os.remove("meta")
        return None
    

    async def process(self):
        """Simplifying having 5 million functions and iterating through it all in each of them. Only one iteration here"""
        # note that I can probably stop recording data much earlier in many of these
        # use mp metal and mp yang for testing right now
        # output should be two dictionaries and a list:
        #   empireData = {playername: [countrycode, color, countryname]}
        #   fedData = {fedname: [members]}
        #   council = [members]
        state = None
        for i, line in enumerate(self.lines):

            if "player={" in line: # start grabbing players and their respective countries
                state = "players"
            elif "tick=" in line: # stop recording players 
                state = None
            elif state == "players":
                if "name=" in line:
                    playerName = line.strip('\n\tname=')
                    playerName = playerName.strip('"')
                    #playerName = line.strip('\n')
                    #playerName = playerName.strip("\t")
                    #playerName = playerName.strip('"')
                    #playerName = playerName.strip("name=")
                    #countryCode = self.lines[i+1]
                    countryCode = self.lines[i+1].strip("\n\tcountry=")
                    #countryCode = countryCode.strip("country=")
                    #countryCode = countryCode.strip("\n")
                    #countryCode = countryCode.strip("\t")
                    self.empireData[playerName] = [countryCode]


            elif "flag={" in line: # start grabbing that empire data country={
                # grab name, color, and number
                state = "country"
            elif "tech_status=" in line: # strop grabbing that empire data
                state = None
            
            elif state == "country":
                if "colors={" in line:
                    color = self.lines[i+1].strip("\n\t")
                    color = color.strip('"')
                    #color = self.lines[i+1].strip('\t')
                    #color = color.strip('"')
                    #color = color.strip('\n')
                    #color = color.strip('"')
                    # resolve color naming to predesignated rgb values
                    # python really needs a switch case
                    if color == "dark_brown":
                        #4d3939
                        discColor = discord.Color.dark_gold()
                    elif color == "brown":
                        discColor = discord.Color.from_rgb(74, 63, 34)
                    elif color == "orange":
                        discColor = discord.Color.orange()
                    elif color == "red_orange":
                        discColor = discord.Color.gold()
                    elif color == "red":
                        discColor = discord.Color.red()
                    elif color == "burgundy":
                        discColor = discord.Color.dark_magenta()
                    elif color == "pink":
                        discColor = discord.Color.magenta()
                    elif color == "purple":
                        discColor = discord.Color.purple()
                    elif color == "dark_purple":
                        discColor = discord.Color.dark_purple()
                    elif color == "indigo":
                        discColor = discord.Color.from_rgb(41, 6, 122)
                    elif color == "dark_blue":
                        discColor = discord.Color.dark_blue()
                    elif color == "blue":
                        discColor = discord.Color.blue()
                    elif color == "turqouise":
                        discColor = discord.Color.from_rgb(66, 230, 245)
                    elif color == "teal":
                        discColor = discord.Color.teal()
                    elif color == "dark_teal":
                        discColor = discord.Color.dark_teal()
                    elif color == "green":
                        discColor = discord.Color.green()
                    elif color == "dark_green":
                        discColor = discord.Color.dark_green()
                    elif color == "grey":
                        discColor = discord.Color.light_gray()
                    elif color == "dark_grey":
                        discColor = discord.Color.dark_gray()
                    elif color == "black":
                        discColor = discord.Color.darker_grey()
                    else: # default color
                        discColor = discord.Color.greyple()
                    countryName = self.lines[i+8].strip("\n\tname=")
                    countryName = countryName.strip('"')
                    #countryName = self.lines[i+8].strip('\n')#strip("\n", '"')
                    #countryName = countryName.strip("\t")
                    #countryName = countryName.strip('"')
                    emp = self.lines[i-10].strip("\n\t={")
                    for player in self.empireData.keys():
                        if emp == self.empireData[player][0]:
                            self.empireData[player].append(discColor)
                            self.empireData[player].append(countryName)
                            break
                        else:
                            pass


            elif "federation={" in line: # start grabbing federation data
                state = "federation"
            elif "truce={" in line: # stop grabbing federation data
                state = None

            elif state == "federation":
                if "name=" in line:
                    fedName = line.strip("\n\tname=")
                    fedName = fedName.strip('"')
                    #fedName = line.strip('\t')
                    #fedName = fedName.strip('name=')#("\n", "name=", '"')
                    #fedName = fedName.strip('"')
                elif "members={" in line:
                    memberString = self.lines[i+1].strip("\n\t")
                    #memberString = self.lines[i+1].strip("\t")
                    #memberString = memberString.strip("\n")
                    memberList = memberString.split() # gives list of members(if string was "10 3 4 5" it would output ['10','3','4','5'])
                    self.fedData[fedName] = memberList # this should(tm) work
    

            elif "galactic_community={" in line: # just grab the data since there are not multiple sets
                council_String = self.lines[i+5]
                council_List = council_String.split()
                self.council = council_List
        print("done processing")



saveData = saveProcessing()

async def assignRoles():
    print(saveData.empireData)
    server = client.get_guild(discGuild)
    print(server)
    for player in names.keys():
        if player in saveData.empireData:
            print("player is in empireData")
            member = server.get_member(names[player])
            roleExist = get(server.roles, name=saveData.empireData[player][2])
            if roleExist:
                print("role already exists!")
                if roleExist in member.roles:
                    print("member has role, passing")
                    pass
                else:
                    print("member did not have role, adding")
                    await member.add_roles(roleExist)
            else:
                print("making new role")
                role = await server.create_role(name=saveData.empireData[player][2], color=saveData.empireData[player][1])
                await member.add_roles(role)
                print("role added")
            for federation in saveData.fedData.keys():
                if saveData.empireData[player][0] in saveData.fedData[federation]:
                    print("player is also in federation!")
                    roleExist = get(server.roles, name=federation)
                    if roleExist:
                        print("role already exists!")
                        if roleExist in member.roles:
                            print("member already had role, passing")
                            pass
                        else:
                            print("member did not have role, adding")
                            await member.add_roles(get(server.roles, name=federation))
                    else:
                        print("making new federation role")
                        role = await server.create_role(name=federation)
                        await member.add_roles(role)
            if saveData.empireData[player][0] in saveData.council:
                roleExist = get(server.roles, name="Galactic Council")
                if roleExist:
                    if roleExist in member.roles:
                        pass
                    else:
                        await member.add_roles(get(server.roles, name="Galactic Council"))
                else:
                    role = await server.create_role(name="Galactic Council")
                    await member.add_roles(role)

async def createChannels():

    server = client.get_guild(discGuild)
    for cat in server.categories:
        print(cat.name)
        if cat.name == "Federations":
            category = cat
            break
        else:
            category = None
    if category == None: 
        category = await server.create_category("Federations")
    # permissions for channels
    textOverwrites = {
        server.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False)
    }
    voiceOverwrites = {
        server.default_role: discord.PermissionOverwrite(view_channel=True, connect=False)
    }
    # creating text
    for federation in saveData.fedData.keys():
        role = get(server.roles, name=federation)
        if role: # see if role for federation exists, if no, then no one is in it and it doesn't 
            creation = True
            for channel in category.channels:
                if channel.name.lower() == federation.lower():
                    creation = False
                else:
                    continue
            if creation:
                textOverwrites[role] = discord.PermissionOverwrite(read_messages=True, view_channel=True, read_message_history=True, send_messages=True)
                await server.create_text_channel(federation, overwrites=textOverwrites, category=category)
                voiceOverwrites[role] = discord.PermissionOverwrite(connect=True)
                await server.create_voice_channel(federation, overwrites=voiceOverwrites, category=category)
                textOverwrites.pop(role, None)
                voiceOverwrites.pop(role, None)
            else:
                pass
        else:
            continue

async def observer():
    """looks at files in a directory and slects the latest file for parsing"""
    await client.wait_until_ready()
    while True:
        print(names)
        if saveData.path != None:
            files = os.listdir(saveData.path)
            paths = [os.path.join(saveData.path, basename) for basename in files]
            latest = max(paths, key=os.path.getctime)
            #latest.replace("\\", "/")
            print(f"\n Latest is {latest} \n")
            await saveData.unzip(latest)
            print("unzipped!")
            await saveData.process()
            print("processed")
            await assignRoles()
            print("roles assigned!")
            await createChannels()
            print("channels created!")
            await asyncio.sleep(10) # waits every 5 minutes
        else:
            print("path is currently none \n")
            await asyncio.sleep(10)

@client.command()
async def iam(ctx, steamName):
    discID = ctx.message.author.id # defines the id of the sender
    # need to check to make sure people don't screw up
    names[steamName] = discID
    await ctx.send("Steam name applied!")

@client.command()
async def selectSave(ctx, directory):
    """Takes the abosulte file path to the folder containing the save files of selected stellaris game"""
    global discGuild
    saveData.path = directory
    discGuild = ctx.guild.id
    print(discGuild)
    await ctx.send(f"Watching directory {directory} for new saves!")
    # start observer

@client.command()
async def victoryScreen(ctx):
    """would just display the victory screen as an embed"""
    pass

if __name__ == "__main__":
    client.loop.create_task(observer())
    client.run(TOKEN)


