import pickle
import discord
import asyncio
import os
import time
import blockchecker
import asyncio
import mailer

client = discord.Client()

claims = {}

alerts = [0]

email_addresses = {}

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
        pool = args[1]

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
                 for user in claims[pool]:
                     
                     if faulty_nodes[pool]['error'] == '5blocksbehind':
                         await client.send_message(user,"**"+pool+"**" + " is 5 blocks behind the network!")
                         print("Telling" + str(user) + " that " + pool + " is down")
                         if user in email_addresses:
                             print("Sending email to " + email_addresses[user])
                             print(mailer.send_email(email_addresses[user],pool + "'s block height is below the median","Hello! \n \n " + pool + " is 5 blocks behind the network!") )
                     if faulty_nodes[pool]['error'] == 'unresponsive':
                         await client.send_message(user,"**"+pool+"**" + " is not responsive!")
                         print("Telling" + str(user) + " that " + pool + " is down")
                         if user in email_addresses:
                             print("Sending email to " + email_addresses[user])
                             print(mailer.send_email(email_addresses[user],pool + " is not responding!","Hello! \n \n " + pool + " has stopped responding.") 
)
                     
         await asyncio.sleep(60)

client.loop.create_task(check_blocks())
client.run('token')
