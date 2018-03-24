import pickle
import discord
import asyncio
import os
import time
from datetime import datetime
import blockchecker
import asyncio
import mailer

client = discord.Client()

claims = {}

alerts = [0]

email_addresses = {}

allowed_channel = "channelid"


try:
    pickle_in = open("emails.pickle","rb")
    email_addresses = pickle.load(pickle_in)
except:
    print("No stored email addresses!")

try:
    pickle_in = open("claims.pickle","rb")
    claims = pickle.load(pickle_in)
except:
    print("No previous data to load")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):

    if message.channel.id != allowed_channel:
        return

    if message.content.startswith('!help'):

        help_msg = (
            "```Commands:\n"
            "\n"
            "!claim pool.url email@address.com\n\n"
            "---------------------------------\n"
            "Claims pool.url and signs you up for getting Discord mentions whenever a problem is detected on that pool, and email alerts if email address is provided (optional).\n"
            "\n\n"
            "!unclaim pool.url\n"
            "---------------------------------\n"
            "Unregisters you from receiving notifications about pool.url.\n"
            "\n\n"
            "!listclaims\n"
            "---------------------------------\n"
            "Returns a list of claimed pools and their claimer(s).\n"
            "\n\n"
            "!heights\n"
            "---------------------------------\n"
            "Prints a list of pools and their current block height.```"
        )
        await client.send_message(message.channel, help_msg)

    if message.content.startswith('!heights'):
        heights = blockchecker.get_heights()
        heights_msg = (
            "```Current block heights:\n\n"
            "Pool                          Height    Time since update\n\n"
        )
        time_now = time.time()

        for pool in heights:
            this_height = heights[pool][0]
            this_timestamp = int( (time_now - heights[pool][1]) / 60 )

            space = (30 - len(pool) ) * " "

            heights_msg += pool + space + str(this_height) + "    " + str(this_timestamp) + "m ago" + "\n"

        heights_msg += "```"
        await client.send_message(message.channel, heights_msg)

    if message.content.startswith('!listclaims'):
        
        pools = claims.keys()
        msg = ""
        for pool in pools:

            msg += "**"+pool + ":**\n"

            for users in claims[pool]:
                msg += str(users)+"\n"

            msg += "\n"


        await client.send_message(message.channel, msg)

    if message.content.startswith('!unclaim'):

        command = message.content
        args = message.content.split( )
        pool = args[1]

        if pool not in claims:
            await client.send_message(message.channel, "There is no pool with the name \"" + pool + "\" that has been claimed")
            return

        if message.author not in claims[pool]:
            await client.send_message(message.channel, message.author.mention + " has not claimed " + pool + ".")
        else:
            claims[pool].remove(message.author)

            if len(claims[pool]) == 0:
                del claims[pool]

            await client.send_message(message.channel, message.author.mention + " has been removed from " + pool)
            pickle_out = open("claims.pickle","wb")
            pickle.dump(claims, pickle_out)

    if message.content.startswith('!claim'):

        command = message.content
        args = message.content.split( )

        available_pools = blockchecker.get_heights().keys()

        error_msg = (
            "Usage: !claim pool.url\n\n"
            "List of available pools:\n\n" 
        )
        
        for pool in available_pools:
            error_msg += pool + "\n"

        error_msg += "```"


        if len(args) != 2:
            await client.send_message(message.channel, "```Missing arguments. \n\n"+error_msg)
            return

        pool = args[1]

        if pool not in available_pools:
            await client.send_message(message.channel, "```Pool not in list. \n\n"+error_msg)
            return

        if len(args) > 2:
            email = args[2]
            email_addresses[message.author] = email
            pickle_out = open("emails.pickle","wb")
            pickle.dump(email_addresses, pickle_out)

        # If the pool has not been claimed yet we need to insert an emtpy array into that keys value
        if pool not in claims:
            claims[pool] = []
        # Add user to array in the claims dict only if it has not already been entered
        if message.author not in claims[pool]:
            claims[pool].append(message.author)
            pickle_out = open("claims.pickle","wb")
            pickle.dump(claims, pickle_out)
            await client.send_message(message.channel, message.author.mention + " has just claimed **" + pool + "**.")
        else:
            await client.send_message(message.channel, message.author.mention + " has already been added to **" + pool + "**.")




async def check_blocks():
    await client.wait_until_ready()
    while True:

         faulty_nodes = blockchecker.get_faulty_nodes()

         if any(faulty_nodes):

             for pool in faulty_nodes:

                 # Id, such as z-pool.com245204 - i.e. pool name + block where the pool is stuck
                 id = pool+str(faulty_nodes[pool])

                 if id in alerts:
                    continue

                 alerts.append(id)

                 # Handler for when the pool is behind in block height
                 if faulty_nodes[pool]['error'] == '5blocksbehind':
                     await client.send_message(client.get_channel(allowed_channel), "**"+pool+"**" + " is 5 blocks behind the network!")

                     if pool not in claims.keys():
                         continue

                     for user in claims[pool]:
                        await client.send_message(user,"**"+pool+"**" + " is 5 blocks behind the network!")

                        if user in email_addresses:
                            print("Sending email to " + email_addresses[user])
                            print(mailer.send_email(email_addresses[user],pool + " is having issues!","Hello! " + pool + " is 5 blocks behind the network!"))

                 # Handler for disconnected pools
                 if faulty_nodes[pool]['error'] == 'unresponsive':
                     await client.send_message(client.get_channel(allowed_channel), "**"+pool+"**" + " is not responsive!")

                     if pool not in claims.keys():
                         continue

                     for user in claims[pool]:
                        await client.send_message(user,"**"+pool+"**" + " is not responsive!")

                        if user in email_addresses:
                            print("Sending email to " + email_addresses[user])
                            print(mailer.send_email(email_addresses[user],pool + " is not responding!","Hello!" + pool + " has stopped responding."))

         await asyncio.sleep(60)

client.loop.create_task(check_blocks())
client.run('token')
