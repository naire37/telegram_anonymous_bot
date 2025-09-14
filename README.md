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
python3 src/bot.py --env DEV
```

If you're Dina and you have trouble tunning this on your Mac, make sure your Perl Interpreter is set up to be virtual ./.vevn thingie and reload the terminal.


To Do:
- think about using DB

Features not yet supported:
- редактирование сообщений 
- удаление своих сообщений 
- ответить на сообщение
- ответить лично, в привате
- таймер антиспама
- таймер сгорания сообщений
- опция "пожаловаться"  