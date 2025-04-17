import requests, sys, re, signal, json, time, os, platform
from bs4 import BeautifulSoup
from termcolor import colored
from playwright.sync_api import sync_playwright
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
	time.sleep(3)
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
    return string

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
				
			time.sleep(2)
			clear_screen()

		else:
			raise Exception(f"Failed to fetch data, status code: {response.status_code}")

	except Exception as e:
		# Print the error message and exit the script
		print(f"\n{colored("[!]", "red")} Error fetching data: {e}")
		sys.exit(1)


def download_mods(mods):
	global non_downloadable_mods
	download_pb = log.progress(f"{colored("[i]", "blue", attrs=["bold"])} Downloading mods...")
	time.sleep(2)
	for mod in mods:
		try:
			# Get the mod name and download link (Shared in skatebit web)
			mod_name = mod['name']
			mod_link = mod['url']
			# Update the progress bar with the mod name
			download_pb.status(f"{colored(mod_name, 'yellow')}")
			time.sleep(0.5)
			# Parse the mod name to a valid filename
			filename = sanitize_strings_to_filenames(mod_name) + ".zip"
			# Create the directory if it doesn't exist
			if not os.path.exists("mods"):
				os.makedirs("mods")
			# Download the mod
			response = requests.get(mod_link, headers=headers)
			#  Check if the server responded with a 200 status code
			if response.status_code == 200:
				# Save the mod to the mods directory
				with open(f"mods/{filename}", "wb") as file:
					file.write(response.content)
				# Update the progress bar with a success message
				download_pb.success(f"Mod {colored(mod_name, 'yellow')} downloaded successfully.")
			else:
				# If the server responded with a diferent 200 status code, it means the mod is not available for download
				download_pb.failure(f"Mod {colored(mod_name, 'yellow')} failed to download.")
				# Track the non-downloable mod
				non_downloadable_mods.append({"name": mod_name, "url": mod_link})
			time.sleep(0.5)

		except Exception as e:
			# If an error occurs, update the progress bar with a failure message.
			download_pb.failure(f"Mod {colored(mod_name, 'yellow')} failed to download.")
			# Track the non-downloable mod
			non_downloadable_mods.append({"name": mod_name, "url": mod_link})
			print(f"\n{colored('[!]', 'red')} Error downloading {mod_name}: {e}")
			time.sleep(0.5)
			continue


if __name__ == "__main__":
	clear_screen()
	banner()
	get_versions()
	print(f"{colored("[+]", "green")} The following versions of Skater XL were found\n")
	
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