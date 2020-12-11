# BANG

![Version](https://img.shields.io/badge/version-1.0-blue)


**Bang!** is a board game by *Emiliano Sciarra*, edited by *Asmodee, Tilsit* (2003).  

Initially, only the sheriff is known. The other players play the role of deputy sheriff, outlaw or renegade, but their role is kept secret. Using cards, but also negotiations and verbal influence, the players will play cards at each other, or support each other, depending on their role and the role they perceive the other players to be playing.  
<font size=1>(source https://www.jeuxdenim.be/jeu-Wanted)</font>  
For more details, please refer to the original game.
***

<img src="https://git-scm.com/images/logos/downloads/Git-Icon-1788C.png" width="30"/>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/165px-Python-logo-notext.svg.png" width="30"/>
<img src="https://discord.com/assets/f8389ca1a741a115313bede9ac02e2c0.svg" width="35"/>

This project proposes a video game based on a copy of the original deck of cards.
It is based on *Git*, *Python* and *Makefile* technologies.  
To be able to use this project, you would need to have a [discord account](https://discord.com/login).



## Usage

### Clone repository

In order to run the project, you would need following technologies:
- *Python3*
- *make*

Just **after cloning** or downloading sources, make sure you can run *Python vesion 3* by running following command :
```
make check
```
If printed version is not *Python3*, you would have to edit `Makefile` and replace `EXEC` variable with appropriate command depending of your local installation.

If it is the **first time** you get project sources, install required libraries by running :
```
make install
```
Next time you need to update these libraries, use
```
make update
```

Finally, you need to configure your [discord bot](https://discord.com/developers/applications) .  
Refer to [discord documentation](https://discordpy.readthedocs.io/en/latest/discord.html) if you need help on bot creation.  
Create file `resources/config.ini` from template `resources/config.ini.example`.
Insert your bot token here and fill in the others parameters.

### Run

Run your bot with
```
make
```
Stop it with
`kill -9 $(pidof <your python command>)`.

The executable `bot.py` is ran with the name of configuration to use as a parameter. By default, bot runs with `DEFAULT` configuration.  
You can add several configurations in `resources/config.ini`.

For example, create an other configuration named *TEST* by copying configuration block `[DEFAULT]` and give it a new name *TEST* .  
Then run `bot.py` by passing the config block name *TEST* as argument.  
See example with :
```
make test
```

## Contribute

### Test code

Test the code you write.
If you have to create a new executable test file, add a new line in Makefile to integrate it to existing test files.
Tests are ran with command :
```
make unit-test
```

### Test resources

To check syntax of resource declarative files, use command
```
make check-resource
```
