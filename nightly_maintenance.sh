#!/bin/bash

#Kill them all, will get restarted by cron.
pkill -f "bot"

cd /home/ec2-user/telegram_anonymous_bot; 

#Rename current logs for all environments (prod, offtop, dev) for both messages and users to yesterday's logs
mv -v logs/ships_DEV.log "logs/ships_dev_$(date -v-1d +%F).log"
mv -v logs/ships_PROD.log "logs/ships_prod_$(date -v-1d +%F).log"
mv -v logs/ships_OFFTOP.log "logs/ships_offtop_$(date -v-1d +%F).log"

mv -v logs/users_DEV.log "logs/users_dev_$(date -v-1d +%F).log"
mv -v logs/users_PROD.log "logs/users_prod_$(date -v-1d +%F).log"
mv -v logs/users_OFFTOP.log "logs/users_offtop_$(date -v-1d +%F).log"

#git pull; 
python3 -m pip install python-dotenv
poetry install --no-root
#TODO: delete logs that are 2 months or more old ?