# AutomodXL 

-----

Welcome everyone, this is a project called **AutomodXL** and it was born with the idea (and laziness in fact) of manually downloading each mod every time I format my PC, try to find out which ones are compatible with the different possible versions and all that tedious work.

First of all, I'm from Argentina so I understand that the possible users (if anyone uses it lol) of this project will be people from the United States, Canada and those countries I guess, *so sorry* for my English and lack of context of the existing *Skater XL communities* like [Milky's](https://discord.gg/phMWJzdP), [Fro's](https://discord.gg/RZ5GY2wS), [Guru's](https://discord.gg/rrjDUXP2) and any other, I'm not very into these niches and I'm trying to do my best.

----

So the structure of this project is pretty basic...

- `requeriments.txt`: This is a file with all python modules needed to run correctly the script.
- `main.py`: The script in question, which is responsible for consulting the current Skater XL versions posted on the [Skatebit site](https://skatebit.vercel.app/mods), attempts to obtain all the mods for the version selected by the user from the Github project. Then it attempts to download each mod to save them into a new folder called "**mods**" inside this repository directory. 

It's important to keep in mind that the *Unity Mod Manager* README doesn't have information about run this software from de `CLI`, even in the "*Install mods section*" their talk about `GUI`, so you will be hands on again in this point, opening the *UMM* and selecting all mods downloaded into the **mods** folder created in this level.

Also, since this project was created for personal use, I would add an option to use "**default configurations**" (which are *Milky's stats*, *stances*, and *style*, which in my case I always used), since I never delved into configuration and customization in depth. I know a lot of people love to configure and customize their own stuff, so if you want, you can delete the default files found in the "**stats**", "**steeze**", "**fro-mod**" and "**stance**" directories and add your owns to then select the option to install the config files from the script.

- `configurations`: Directory with default configurations.
    - `fro-mod/Settings.xml`: Custom fro mod settings shared in Milky's discord.
    - `stance/stance.xml`: Milky's October 2024 stances configuration shared in his discord.
    - `stats/stats.xml`: Milky's October 2024 stats configuration shared in his discord.
    - `steeze/steeze.xml`: Milky's October 2024 steeze configuration shared in his discord.

-----
# Requirements
- Python 3.8 or higher
- [Playwright dependencies](https://playwright.dev/python/docs/intro#installation) (for browsers)
- Git (optional, for cloning repositories)
----

# Installing dependencies

This script use some python modules which are fundamentals to works, so you need just install the modules detailed in **requirements.txt** and the *browsers* for **playwright**.

1. **Clone the repository**:

```bash
git clone "https://github.com/dobliuw/automodxl"
cd automodXL
```
2. **Install the dependencies**:

```bash
pip3 install -r requeriments.txt
```
3. **Install Playwrigth browsers** (Required to get from **Skatebit webpage** the current SkaterXL versions plubished in the site):

```bash
python3 -m playwright install
```

----
# AutomodXL run

Finally you have all the necesary to run the script:

```bash
python3 main.py
```

🖥 Supported Platforms

- ✅ Windows 10/11 (OneDrive-aware)
- ✅ Linux (Steam via .steam or .local/share/Steam)
- ⚠️ macOS (experimental support, not fully tested)

