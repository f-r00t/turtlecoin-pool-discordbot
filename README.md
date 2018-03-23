# turtlecoin-pool-discordbot

Checks every pool in the list at https://raw.githubusercontent.com/turtlecoin/turtlecoin-pools-json/master/turtlecoin-pools.json and tells operators who have claimed their pool if the pool falls behind 5 or more blocks from the median block height.

# Usage:

## Running the bot:

pip3 install discord.py

git clone https://github.com/fruktstav/turtlecoin-pool-discordbot.git

cd turtlecoin-pool-discordbot/src

Change the last line in bot.py and enter your bot token from discord developers, and the options for mailgun in mailer.py then:

python3 bot.py

## Interacting with the bot:

!claim pool.url email@address.com

Write this in any channel that the bot is online in, or in a DM to the bot and it will alert you whenever the pool you claim is down/falling behind. The e-mail parameter is optional.

!unclaim pool.url

Remove yourself from pool.url.

!listclaims

Returns a list of all claimed pools and their operators
