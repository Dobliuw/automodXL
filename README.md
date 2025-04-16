# Dobliuw Hacking notes 

-----

Welcome everyone, this is a project called **AutomodXL** and it was born with the idea (and laziness in fact) of manually downloading each mod every time I format my PC, try to find out which ones are compatible with the different possible versions and all that tedious work.

First of all, I'm from Argentina so I understand that the possible users (if anyone uses it lol) of this project will be people from the United States, Canada and those countries I guess, *so sorry* for my English and lack of context of the existing *Skater XL communities* like [Milky's](https://discord.gg/phMWJzdP), [Fro's](https://discord.gg/RZ5GY2wS), [Guru's](https://discord.gg/rrjDUXP2) and any other, I'm not very into these niches and I'm trying to do my best.

----

So the structure of this project is pretty basic...

- `requeriments.txt`: This is a file with all python modules needed to run correctly the script.
- `main.py`: The script in question, which is responsible for consulting the current versions posted on the [Skatebit site](https://skatebit.vercel.app/mods), attempts to obtain all the mods for the version selected by the user from the Github project. Then... (This step is not yet complete, so if you're reading this, it's important to clarify that the IDEA is:) it attempts to download, depending on the selected version, the corresponding **Unity Mod Manager** along with each mod posted on the **Skatebit site** for that version. I would download them and save them in a downloads folder, then use the Unity Mod Manager to load them all for the Skater XL game (I'm still not sure if this type of functionality can be done from the console line).

Also, since this project was created for personal use, I would add an option to use "**default configurations**" (which are *Milky's stats*, *stances*, and *style*, which in my case I always used), since I never delved into configuration and customization in depth. I know a lot of people love to configure and customize their own stuff, so this step is optional, and if you don't select this option, you'd have to do it again manually.

- `configurations`: Directory with default configurations.
    - `fro-mod/Settings.xml`: Custom fro mod settings shared in Milky's discord.
    - `stance/Milky_October-2024_STANCE.xml`: Milky's October 2024 stances configuration shared in his discord.
    - `stats/Milky_October-2024_STATS.xml`: Milky's October 2024 stats configuration shared in his discord.
    - `steeze/Milky_October-2024_STEEZE.xml`: Milky's October 2024 steeze configuration shared in his discord.

-----

# Installing dependencies

A future section to install the needed dependencies walkthrough.

----
# AutomodXL run

A future section to show how the script works. 