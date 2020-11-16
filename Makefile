EXEC=python

all: start

start:
	@ $(EXEC) bot.py DEFAULT > log 2>&1 &
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
