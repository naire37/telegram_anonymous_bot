# telegram_anonymous_bot
Anonymous bot for telegram. Quick and dirty. 

To install, run
```
brew install python3
pip install poetry
poetry install --no-root
```

To debug a dev version, run
```
python3 src/bot.py
```

If you're Dina and you have trouble tunning this on your Mac, make sure your Perl Interpreter is set up to be virtual ./.vevn thingie and reload the terminal.


To Do:
- add a test environment
- create an .env file with TG bot environments
- deployment strategy
- think about using DB

Known bugs:
- does not write the user IDs properly
