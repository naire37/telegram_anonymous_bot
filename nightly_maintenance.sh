#!/bin/bash

#Kill all running instances.
pkill -f "bot"

cd /home/ec2-user/telegram_anonymous_bot; 

#Rename current logs for all environments (prod, offtop, dev) for both messages and users to yesterday's logs
mv -v logs/ships_DEV.log "logs/ships_dev_$(date -d "yesterday 13:00" '+%Y-%m-%d').log"
mv -v logs/ships_PROD.log "logs/ships_prod_$(date -d "yesterday 13:00" '+%Y-%m-%d').log"
mv -v logs/ships_OFFTOP.log "logs/ships_offtop_$(date -d "yesterday 13:00" '+%Y-%m-%d').log"

mv -v logs/users_DEV.log "logs/users_dev_$(date -d "yesterday 13:00" '+%Y-%m-%d').log"
mv -v logs/users_PROD.log "logs/users_prod_$(date -d "yesterday 13:00" '+%Y-%m-%d').log"
mv -v logs/users_OFFTOP.log "logs/users_offtop_$(date -d "yesterday 13:00" '+%Y-%m-%d').log"

#TODO: delete logs that are 2 months or more old

#Get the latest code
git pull; 

#Install any new packages
python3 -m pip install python-dotenv
poetry install --no-root

#Restart the bot
sh autostart_bot.sh

