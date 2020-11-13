EXEC=python

all: start

start:
	@ $(EXEC) bot.py DEFAULT 2&> log &
	@ echo "Bot running."

test:
	@ echo "Launch bot in test mode."
	@ $(EXEC) bot.py TEST

unit-test:
	@ $(EXEC) game/test_bang.py
	echo "***********************************************************************"
	@ $(EXEC) game/test_rules.py

check:
	$(EXEC) --version

install:
	$(EXEC) -m pip install discord
	$(EXEC) -m pip install discord.py

update:
	$(EXEC) -m pip install --upgrade pip
	$(EXEC) -m pip install --upgrade discord
	$(EXEC) -m pip install --upgrade discord.py
