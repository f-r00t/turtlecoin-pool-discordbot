# turtlecoin-pool-discordbot

Checks every pool in the list at https://raw.githubusercontent.com/turtlecoin/turtlecoin-pools-json/master/turtlecoin-pools.json and tells operators who have claimed their pool if the pool falls behind 5 or more blocks from the median block height.

# Usage:

git clone https://github.com/fruktstav/turtlecoin-pool-discordbot.git
cd turtlecoin-pool-discordbot/src

Change the last line in bot.py and enter your bot token from discord developers, then:

python3 bot.py
