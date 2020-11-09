EXEC=python

all: start

start:
	@ $(EXEC) bot.py DEFAULT 2&> log &
	@ echo "Bot running."

test:
	@ echo "Launch bot in test mode."
	@ $(EXEC) bot.py TEST

check:
	$(EXEC) --version

install:
	$(EXEC) -m pip install discord
	$(EXEC) -m pip install discord.py

update:
	$(EXEC) -m pip install --upgrade pip
	$(EXEC) -m pip install --upgrade discord
	$(EXEC) -m pip install --upgrade discord.py
