import sys, re, signal
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# CTRL + C Declaration
def ctrl_c(sig, frame):
	print("\n\n\t[!] Quiting...\n\n")
	sys.exit(1)

# TRAP CTRL + C
signal.signal(signal.SIGINT, ctrl_c)

# Global vars 
url = "https://github.com/ShawnEdgell/skatebit/blob/main/src/lib/data/modData.ts"
headers = {
	"User-Agent": "Mozilla/5.0"
}
proxy = {
	"http":"127.0.0.1:8080"
}

# Function to get the mods from the website
def get_versions_and_mods():
	with sync_playwright() as pwr:
		browser = pwr.firefox.launch(headless=True)
		context = browser.new_context()
		page = context.new_page()
		page.goto(url)
		
		# Wait to load all dynamic content
		page.wait_for_selector('text=Mods.')

		# Get the content of the page
		content = page.content()
		browser.close() 
		return content


def parse_available_versions(html):
	soup = BeautifulSoup(html, "html.parser")

	versions = []

	for button in soup.find_all("button", class_="btn"):
		text = button.get_text(strip=True)
		if "Skater XL" in text:
			versions.append(text) 

	return versions


if __name__ == "__main__":
	print("\n\t[+] Welcome to the automodedXL script by dobliuw :)\n")
	response = get_versions_and_mods()
	versions = parse_available_versions(response)
	print("[+] Found the following versions:\n")
	for index, version in versions.enumerate(versions, start=1):
		print("\t{index}) {version}\n")
	print("\t[!] Please select a version to download the mods for:\n")