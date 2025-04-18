import requests, sys, re, signal, json, time, os, platform, shutil 
from bs4 import BeautifulSoup
from termcolor import colored
from playwright.sync_api import sync_playwright
from pathlib import Path
from pwn import *

# CTRL + C Declaration
def ctrl_c(sig, frame):
	print(f"\n\n\t{colored("[!]", "red")} Quiting...\n\n")
	sys.exit(1)

# TRAP CTRL + C
signal.signal(signal.SIGINT, ctrl_c)

# Global vars 
url = "https://raw.githubusercontent.com/ShawnEdgell/skatebit/main/src/lib/data/modData.ts"
headers = { "User-Agent": "Mozilla/5.0" }
version_selected = ""
base_versions = []
versions = []
mods_to_download = []
non_downloadable_mods = []
operative_system = platform.system()

def clear_screen():
	global operative_system
	# Clear the screen based on the operating system
	if operative_system == "Windows":
		os.system("cls")
	else:
		os.system("clear")


def banner():
	print("\n\n")
	banner=r"""
   _____          __                            ._______  ___.____     
  /  _  \  __ ___/  |_  ____   _____   ____   __| _/\   \/  /|    |    
 /  /_\  \|  |  \   __\/  _ \ /     \ /  _ \ / __ |  \     / |    |    
/    |    \  |  /|  | (  <_> )  Y Y  (  <_> ) /_/ |  /     \ |    |___ 
\____|__  /____/ |__|  \____/|__|_|  /\____/\____ | /___/\  \|_______ \
        \/                         \/            \/       \_/        \/
	"""
	for line in banner.splitlines():
		if line.strip():
			print(f"\t\t{colored(line, "green", attrs=["bold"])}")
		time.sleep(0.3)
	#print(colored(banner, "green", attrs=["bold"]))
	print(f"\t\t\t\t\t\tBy {colored("dobliuw", "green", attrs=["bold", "blink"])} X {colored("Skatebit", "yellow", attrs=["bold", "blink"])} ;)\n\n")
	time.sleep(4)
	clear_screen()


def parse_array_str_to_json(array_str):
	# Delete comments
	array_str = re.sub(r"^//.*", "", array_str)
	array_str = re.sub(r'// .*', '', array_str)
	array_str = re.sub(r"^/\*.*?\*/", "", array_str, flags=re.DOTALL)

	# Keys without quotes to between quotes
	array_str = re.sub(r'(\w+):', r'"\1":', array_str)

	# Simple quotes to double quotes
	array_str = array_str.replace("'", '"')

	# Fix incorrectly escaped quotes
	array_str = array_str.replace('\\"', '"')

	# Fix duplicated double quotes at the beginning of URLs
	array_str = re.sub(r'""(https"://)', r'"\1', array_str)

	# Fix http quotes errors
	array_str = re.sub(r'"(https)":', r'"\1', array_str)
	array_str = re.sub(r'("url": )"(https)', r'\1"\2', array_str)

	# Ensure closing of list and object brackets
	array_str = re.sub(r',\s*}', '}', array_str)
	array_str = re.sub(r',\s*]', ']', array_str)

	# Clear string up the array string
	array_str = re.sub(r'"\s*,', '",', array_str)
	array_str = re.sub(r':\s*""([^\"])', r': ""\1', array_str)

	# Fix urls without ':' after https or http
	array_str = re.sub(r'"(https?)//', r'"\1://', array_str)

	# Skip inside quotes
	array_str = re.sub(r'([\"])s([^a-zA-Z])', r"'\2", array_str)  # For things like 'DawgVinci"s'
	array_str = re.sub(r'([a-zA-Z])"([a-zA-Z])', r"\1'\2", array_str)  

	array_str = "[" + array_str.strip().rstrip(",") + "]"

	return array_str


def sanitize_strings_to_filenames(string):
	# Replace invalid characters with underscores
    string = re.sub(r'[^\w\-]', '_', string)
    # Delete extra underscores
    string = re.sub(r'_+', '_', string)
	# Avoid starting and ending with underscores
    string = string.strip('_')
    return string + ".zip"

def get_versions():
	global versions
	with sync_playwright() as pwr:
		# Launch the browser and create a new context
		browser = pwr.firefox.launch(headless=True)
		context = browser.new_context()
		page = context.new_page()
		page.goto("https://skatebit.vercel.app/mods")

		# Wait to load all dynamic content
		page.wait_for_selector('text=Mods.')

		# Get the content of the page
		content = page.content()

		# Killing the browser
		browser.close()

		# Parsing the content with BeautifulSoup
		soup = BeautifulSoup(content, "html.parser")

		# Finding all the buttons with the class "btn" to get the specific version of all current mods in skatebit webpage
		for button in soup.find_all("button", class_="btn"):
			text = button.get_text(strip=True)
			if "Skater XL" in text:
				versions.append(text)


# Function to get the mods from the website
def get_mods(version):
	global base_versions, version_selected, mods_to_download
	try:
		response = requests.get(url)
		if response.status_code == 200:
			# Getting the typescript content
			ts_content = response.text

			match = re.search(r"export const %s = \[(.*?)\];" % (version), ts_content, re.DOTALL)

			if match:
				# Convert the array string to JSON format
				array_str = match.group(1) 
				array_str = parse_array_str_to_json(array_str)

			try:
				# Parse the JSON string into a Python object
				mods_list = json.loads(array_str)

			except json.JSONDecodeError as e:
				raise Exception(f"\n{colored("[!]", "red")} Error decoding JSON: {e}")
				
			print(f"\n{colored("[i]", "blue", attrs=["bold"])} The following mods were found availables for {colored(version_selected, "yellow")}:\n")
			for mod in mods_list:
				#  Adding the mods to the list to download
				mods_to_download.append({"name":mod['title'], "url":mod['downloadLinks'][1]['url']})

				print(f"\t+ {colored(mod['title'], "yellow")} {colored(mod['workingVersion'], "green")} (From {mod['author']}) - ({colored(mod['keybind'], "magenta")})")
				print(colored(f"\t\t- {mod['downloadLinks'][0]['url']}\n", "blue", attrs=["underline", "bold"]))
				time.sleep(0.7)
				
			time.sleep(4)
			clear_screen()

		else:
			raise Exception(f"Failed to fetch data, status code: {response.status_code}")

	except Exception as e:
		# Print the error message and exit the script
		print(f"\n{colored("[!]", "red")} Error fetching data: {e}")
		sys.exit(1)

def download_mods(mods):
	global non_downloadable_mods

	print(f"\n{colored('[i]', 'blue', attrs=['bold'])} Downloading mods...\n")
	#download_pb = log.progress(f"{"[i]"} Downloading mods...")
	time.sleep(2)
	clear_screen()

	# Create the directory if it doesn't exist
	if not os.path.exists("mods"):
		os.makedirs("mods")

	for mod in mods:
		try:
			# Get the mod name and download link (Shared in skatebit web)
			mod_name = mod['name']
			mod_link = mod['url']

			# Parse the mod name to a valid filename
			filename = sanitize_strings_to_filenames(mod_name)
			
			# Check if the file already exists in the mods directory
			if os.path.exists(f"mods/{filename}"):	
				# If the file already exists, skip the download and update the progress bar
				print(f"\t{colored('[i]', 'blue', attrs=["bold"])} Mod {colored(mod_name, 'yellow', attrs=['bold'])} already downloaded in mod folder, skipping download.")
				time.sleep(0.5)
				continue # Skip the download if the file already exists

			# Download the mod
			print(f"\t{colored('[+]', 'green')} Downloading {colored(mod_name, "yellow", attrs=["bold"])} Mod...")
			response = requests.get(mod_link, headers=headers)
			
			#  Check if the server responded with a 200 status code
			if response.status_code == 200:
				# Save the mod to the mods directory
				with open(f"mods/{filename}", "wb") as file:
					file.write(response.content)

			else:
				# If the server responded with a diferent 200 status code, it means the mod is not available for download
				download_pb.failure(f"Mod {mod_name} failed to download.")
				print(f"mod {mod_name} failed to download.")
				# Track the non-downloable mod
				non_downloadable_mods.append({"name": mod_name, "url": mod_link})
			time.sleep(0.5)

		except Exception as e:
			# If an error occurs during the download, print the error message and track the non-downloadable mod
			print(f"{colored("[!]", "red")} Mod {mod_name} failed to download.")
			# Track the non-downloable mod
			non_downloadable_mods.append({"name": mod_name, "url": mod_link})
			print(f"\n{colored('[!]', 'red')} Error downloading {mod_name}: {e}")
			time.sleep(0.5)
			continue


def save_configs():
	global operative_system

	# clear the screen
	clear_screen()

	print(f"\n\t{colored("[i]", "blue")} Saving configs...\n")
	time.sleep(2)
	# If the user is using Windows, get the possible OneDrive path from the environment variable
	onedrive_path = os.environ.get("OneDrive")

	# Trying to get the Skater XL path to save the configs
	if onedrive_path:
		skaterxl_path = Path(onedrive_path) / "Documents" / "SkaterXL"
		# If the path doesn't exist, try the "Documentos" folder (Spanish version of Documents)
		if not os.path.exists(skaterxl_path):
			skaterxl_path = Path(onedrive_path) / "Documentos" / "SkaterXL"
	else:
		skaterxl_path = Path.home() / "Documents" / "SkaterXL"
		# If the path doesn't exist, try the "Documentos" folder (Spanish version of Documents)
		if not os.path.exists(skaterxl_path):
			skaterxl_path = Path.home() / "Documentos" / "SkaterXL"

	if os.path.exists(skaterxl_path):
		print(f"\n{colored('[+]', 'green')} Saving configs to {colored(skaterxl_path, 'yellow', attrs=['bold'])}...\n")
	else:
		# If the path doesn't exist, ask the user to insert it manually
		path = input(f"\n{colored('[!]', 'red')} Skater XL path not found. Please insert your path manually if you known it (Ex. C:\\Users\\dobliuw\\Documents\\SkaterXL\\): .\n")
		if os.path.exists(path):
			skaterxl_path = Path(path)
		else:
			print(f"\n{colored('[!]', 'red')} Skater XL path inserted not found, please check it.\n")
			sys.exit(1)

	# Set the destination 
	src_path = Path.cwd() / "configurations"
	dst_path = skaterxl_path / "XXLMod3"

	# Create the destination directory if it doesn't exist
	(dst_path / "StatsCollections").mkdir(parents=True, exist_ok=True)
	(dst_path / "StanceCollections").mkdir(parents=True, exist_ok=True)
	(dst_path / "SteezeCollections").mkdir(parents=True, exist_ok=True)

	print(f"\t{colored("[i]", "blue", attrs=["bold"])} Trying to leave config files into {colored(dst_path, "yellow", attrs=["bold"])}...")
	time.sleep(1)

	# Check if the source files exist before moving them
	if not (src_path  / "stats" / "stats.xml").exists():
		print(f"\n\n\t{colored('[!]', 'red')} Missing config file in mod folder. {colored(src_path  / "stats" / "stats.xml", "red")}\n")
		sys.exit(1)
	elif not (src_path / "stance" / "stance.xml").exists():
		print(f"\n\n\t{colored('[!]', 'red')} Missing config file in mod folder. {colored(src_path  / "stance" / "stance.xml", "red")}\n")
		sys.exit(1)
	elif not (src_path / "steeze" / "steeze.xml").exists():
		print(f"\n\n\t{colored('[!]', 'red')} Missing config file in mod folder. {colored(src_path  / "steeze" / "steeze.xml", "red")}\n")
		sys.exit(1)
	
	# Move the files to the destination directory if they don't exist
	if not (dst_path / "StatsCollections" / "stats.xml").exists():
		# Move the stats.xml file to the destination directory if it doesn't exist
		shutil.move(str(src_path / "stats" / "stats.xml"), str(dst_path / "StatsCollections" / "stats.xml"))
		print(f"\t{colored('[+]', 'green')} Config file {colored('stats.xml', 'yellow', attrs=['bold'])} moved to {colored(dst_path / 'StatsCollections', 'yellow', attrs=['bold'])}...\n")
	
	elif (dst_path / "StanceCollections" / "stance.xml").exists():
		# Move the stance.xml file to the destination directory if it doesn't exist
		shutil.move(str(src_path / "stance" / "stance.xml"), str(dst_path / "StanceCollections" / "stance.xml"))
		print(f"\t{colored('[+]', 'green')} Config file {colored('stance.xml', 'yellow', attrs=['bold'])} moved to {colored(dst_path / 'StanceCollections', 'yellow', attrs=['bold'])}...\n")
	
	elif (dst_path / "SteezeCollections" / "steeze.xml").exists():
		# Move the steeze.xml file to the destination directory if it doesn't exist
		shutil.copy(str(src_path / "steeze" / "steeze.xml"), str(dst_path / "SteezeCollections" / "steeze.xml"))
		print(f"\t{colored('[+]', 'green')} Config file {colored('steeze.xml', 'yellow', attrs=['bold'])} moved to {colored(dst_path / 'SteezeCollections', 'yellow', attrs=['bold'])}...\n")
	else:
		print(f"\n\n\t{colored('[i]', 'blue', attrs=["bold"])} Config files for stats, stance and steeze already found in {colored(dst_path, 'yellow', attrs=["bold"])}\n")
	
	# Set the destination 
	src_path = Path.cwd() / "configurations"	
	dst_path = Path("")
	
	# Try to detect the steamapps path to move the settings.xml file
	if operative_system == "Windows":
		dst_path = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam" / "steamapps" / "common" / "SkaterXL" / "Mods" / "fro-mod"
		if not dst_path.exists():
			dst_path = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam" / "steamapps" / "common" / "Skater XL" / "Mods" / "fro-mod"
	else:
		# If the user is using Linux, get the possible Steam path from the environment variable
		dst_path = Path.home() / ".steam" / "steam" 
		# If the path doesn't exist, try another possible path
		if not dst_path.exists():
			dst_path = Path.home() / ".local" / "share" / "Steam" / "steamapps" / "common" / "SkaterXL" / "Mods" / "fro-mod"
			if not dst_path.exists():
				dst_path = Path.home() / ".local" / "share" / "Steam" / "steamapps" / "common" / "Skater XL" / "Mods" / "fro-mod"
	
	default_steam_path = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam" 
	# Declare the libraryfolders.vdf path (File that contains the paths of all the libraries)
	library_vdf = default_steam_path / "steamapps" / "libraryfolders.vdf"

	# Open the libraryfolders.vdf file to get the possible paths
	with open(library_vdf, encoding="utf-8") as f:
		content = f.read()

	# Find all the paths in the libraryfolders.vdf file
	paths = re.findall(r'"\d+"\s*\{\s*"path"\s*"([^"]+)"', content)
	possible_paths = [Path(path.strip().replace("\\\\", "\\")) / "steamapps" / "common" / "SkaterXL" for path in paths]
	possible_paths += [Path(path.strip().replace("\\\\", "\\")) / "steamapps" / "common" / "Skater XL" for path in paths]

	# add the default steam path to the possible paths
	if (default_steam_path / "steamapps" / "common" / "SkaterXL") not in possible_paths:
		possible_paths.insert(0, default_steam_path / "steamapps" / "common" / "SkaterXL")
	if (default_steam_path / "steamapps" / "common" / "Skater XL") not in possible_paths:
		possible_paths.insert(0, default_steam_path / "steamapps" / "common" / "Skater XL")

	# Check if the path exists and set the destination path
	for path in possible_paths:
		if path.exists():
			dst_path = path / "Mods" / "fro-mod"
			break

	print(f"\n\t{colored("[i]", "blue", attrs=["bold"])} Trying to leave fro-mod config files into {colored(dst_path, "yellow", attrs=["bold"])}...")
	time.sleep(1)
	 
	if not (dst_path / "Settings.xml").exists():
		# Create the destination directory if it doesn't exist
		(dst_path).mkdir(parents=True, exist_ok=True)
		# Move the settings.xml file to the destination directory if it exists
		shutil.copy(str(src_path / "fro-mod" / "Settings.xml"), str(dst_path / "Settings.xml"))
		print(f"\t{colored('[+]', 'green')} Config file {colored('Settings.xml', 'yellow', attrs=['bold'])} moved to {colored(dst_path, 'yellow', attrs=['bold'])}...\n")
	else:
		print(f"\n\n\t{colored('[i]', 'blue', attrs=["bold"])} Config file already found in {colored(src_path  / 'fro-mod/Settings.xml', 'yellow', attrs=["bold"])}\n")


if __name__ == "__main__":
	clear_screen()
	banner()
	get_versions()
	print(f"{colored("[+]", "green")} The following versions of Skater XL were found:\n")
	
	# Print the versions found in the webpage
	for index, version in enumerate(versions):
		number_version = version.split(" ")[2]
		number_version += " " + version.split(" ")[3]
		print(f"\t{colored(str(index+1)+")", "magenta")} Skater XL {colored(number_version, "yellow")}.")
	
	# Ask to the user to select a version
	try:
		selection = int(input(f"\n{colored("[o]", "yellow")} Select a option to download the mods ({colored("1", "magenta")}, {colored("2", "magenta")}, Etc.): "))
	except ValueError:
		print(f"\n{colored("[!]", "red")} Invalid input. Please enter a number.")
		sys.exit(1)

	if selection < 1 or selection > len(versions):
		print(f"\n{colored("[!]", "red")} Invalid selection. Please select a valid option.")
		sys.exit(1)
	else:
		version_selected = versions[selection-1]
		print(f"\n{colored("[i]", "blue", attrs=["bold"])} You selected: {colored(version_selected, "yellow", attrs=["bold"])}.")
		print(f"\n\t{colored("[+]", "green")} Now we will fetch the mods from the website...\n")

	# Get the clean base version name like in the typescript file
	base_version = f"{version_selected.split(' ')[-1].replace('(', '').replace(')', '').lower()}Mods"

	get_mods(base_version)
	download_mods(mods_to_download)
	save_configs()
	
	print (f"\n\t{colored('[+]', 'green')} All mods downloaded and configs saved successfully!")
	time.sleep(2)
	print (f"\tIf you have any problem, please open an issue in the GitHub repository.")
	time.sleep(2)
	print (f"\tAlso if you want to contribute, please open a pull request.")
	time.sleep(4)
	print(f"\n\t{colored('[i]', 'blue', attrs=['bold'])} Thanks for using {colored('AutomodXL', 'yellow', attrs=['bold'])}!\n")