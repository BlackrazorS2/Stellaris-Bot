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
import py7zr
# need to install and add support for watchdogs which can run commands on file update

#class metadata:
#    def __init__(self):
TOKEN = "TOKEN"
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents) # command prefix is >>
client.remove_command('help') # removes the default help command to replace it with a custom one
names = {}
discGuild = None

class saveProcessing:
    def __init__(self):
        self.saveLoc = "C:\\user\\documents\\paradox interactive\\stellaris\\save games\\savefolder"
        self.saveFile = f"{self.saveLoc}\\latest.sav"
        self.empireData = {}
        self.fedData = {}
        self.council = []
        self.lines = None
    def updateFile(self):
        # not sure if this needs to exist or what it is for
        pass
    def unzip(self, location):
        #unzips the save file and parses the contents of gamedata into lines
        save = py7zr.SevenZipFile(self.saveFile)
        save.extractall()
        save.close()
        with open("gamedata", "r") as gamedata:
            self.lines = gamedata.readlines()
        # cleaning up
        os.remove("gamedata")
        os.remove("meta")
    

    def process(self):
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
                    playerName = line.strip("\n", '"', "name=")
                    countryCode = self.lines[i+1].strip("\n", "country=")
                    self.empireData[playerName] = [countryCode]


            elif "country={" in line: # start grabbing that empire data
                # grab name, color, and number
                state = "country"
            elif "tech_status=" in line: # strop grabbing that empire data
                state = None
            
            elif state == "country":
                if "colors={" in line:
                    color = self.lines[i+1].strip("\n", '"')
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
                    countryName = self.lines[i+8].strip("\n", '"')
                    self.empireData[playerName].append(discColor)
                    self.empireData[playerName].append(countryName)


            elif "federation={" in line: # start grabbing federation data
                state = "federation"
            elif "truce={" in line: # stop grabbing federation data
                state = None

            elif state == "federation":
                if "name=" in line:
                    fedName = line.strip("\n", "name=", '"')
                elif "members={" in line:
                    memberString = line[i+1].strip("\n")
                    memberList = memberString.split() # gives list of members(if string was "10 3 4 5" it would output ['10','3','4','5'])
                    self.fedData[fedName] = memberList # this should(tm) work
    

            elif "galactic_community={" in line: # just grab the data since there are not multiple sets
                council_String = self.lines[i+5]
                council_List = council_String.split()
                self.council = council_List

saveData = saveProcessing()

@client.command()
async def iam(ctx, steamName):
    discID = ctx.message.author.id # defines the id of the sender
    names[steamName] = discID
    await ctx.send("Steam name applied!")

@client.command()
async def selectSave(ctx, directory):
    """Takes the abosulte file path to the folder containing the save files of selected stellaris game"""
    saveData.saveLoc = directory
    discGuild = ctx.guild
    await ctx.send(f"Watching directory {directory} for new saves!")

@client.command()
async def victoryScreen(ctx):
    """would just display the victory screen as an embed"""
    pass



async def assignRoles():
    for player in names.keys():
        if player in saveData.empireData:
            member = discGuild.get_member(names[player])
            roleExist = get(discGuild.roles, name=saveData.empireData[player][2])
            if roleExist:
                if roleExist in member.roles:
                    pass
                else:
                    member.add_roles(roleExist)
            else:
                role = discGuild.create_role(name=saveData.empireData[player][2], color=saveData.empireData[player][1])
                member.add_roles(role)
            for federation in saveData.fedData.keys():
                if saveData.empireData[player][0] in saveData.fedData[federation]:
                    roleExist = get(discGuild.roles, name=federation)
                    if roleExist:
                        if roleExist in member.roles:
                            pass
                        else:
                            member.add_roles(get(discGuild.roles, name=federation))
                    else:
                        role = discGuild.create_role(name=federation)
                        member.add_roles(role)
            if saveData.empireData[player][0] in saveData.council:
                roleExist = get(discGuild.roles, name="Galactic Council")
                if roleExist:
                    if roleExist in member.roles:
                        pass
                    else:
                        member.add_roles(get(discGuild.roles, name="Galactic Council"))
                else:
                    role = discGuild.create_role(name="Galactic Council")
                    member.add_roles(role)
                        
#function watcher
# when new save file
# run all the unpacking and gets
# run assignRoles



