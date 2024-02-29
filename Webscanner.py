#Make sure you have all necessary system dependencies in order to execute the code
#Webbkoll is an online tool that checks how a webpage is doing with regards to privacy.https://webbkoll.dataskydd.net

#Installation the local host
#Browser backend see https://codeberg.org/dataskydd.net/webbkoll-backend
"""
The browser backend is a tiny script that uses Puppeteer to control instances of Chromium.
Node 10.18.1+ required. Simply run npm install, which should install everything necessary, including a local copy of Chromium; and then "npm start" or (nodejs index.js) to start. 
Usage: http://localhost:8100/?fetch_url=http://www.example.com 
"""
#Frontend/"regular backend" see https://codeberg.org/dataskydd.net/webbkoll
"""Install Erlang (>= 24) and Elixir (>= 1.12) -- see http://elixir-lang.org/install.html.
Clone this repository, cd into it.
Install dependencies: mix deps.get
Make sure the backend is running on the host/port specified in config/dev.exs(The script listens to port 8100 by default)
Start the Phoenix endpoint with "mix phx.server" 
"""
#PrivacyScore allows you to test websites and rank them according to their security and privacy features. https://privacyscore.org/

#Installation the local host see https://github.com/privacyscore/privacyscanner#privacyscanner
"""
privacyscanner needs a Python 3 runtime. Depending on your environment you may also need the Python 3 header files in order to instal privacyscanner. For instance, on Debian and Ubuntu Linux you should be able to obtain all necessary files by executing:
you have to download the dependencies of privacyscanner. These include the MaxMind GeoIP2 database and the Easylist adblock lists
In addition, google-chrome or chromium have to be installed and available in your PATH
Usage:privacyscanner scan http://example.com/
"""
#you have to install also some Python Packages
#Selenium Python bindings provide a convenient API to access Selenium WebDrivers like Firefox, Ie, Chrome, Remote etc. The current supported Python versions are 3.5 and above.
#beautiful soup is a python library used to extract data from html and xml documents especially for web scraping
#pretty table is a python library used to create tabular representations of data
#The browser class mechanize.Browser implements the interface of urllib2.OpenerDirector, so any URL can be opened not just http
#json to accsess the scanned data file with privacyscore
#und some other libraries like os,re,requests and time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from  selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import json
import os
import re
import git
from prettytable import PrettyTable
import time
import mechanize
import requests
import socket
import shutil 
from bs4 import BeautifulSoup
from datetime import datetime
from git import Repo, InvalidGitRepositoryError

#select the the browser to use it by the extract all the data
selected_browser = input("Select Browser to use it (chrome/firefox): ").lower()

if selected_browser == 'chrome':
    # Konfigurationsoptionen für Chrome
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu') 
    
    # Webtreiber für Chrome erstellen
    driver = webdriver.Chrome(options=chrome_options)
    
elif selected_browser == 'firefox':
    # Konfigurationsoptionen für Firefox
    firefox_options = FirefoxOptions()
    firefox_options.add_argument('--headless')
    
    # Webtreiber für Firefox erstellen
    driver = webdriver.Firefox(options=firefox_options)
else:
    print("Invalid selection. Please choose 'chrome' or 'firefox'.")
    
#Entering the websites names to scan them
urls = []

while True:
    url_input = input("Enter one or more websites (or 'exit' to exit):")
    if url_input.lower() == 'exit':
        break
    
    # Check if the input is a valid URL
    if re.match(r'^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', url_input):
        urls.append(url_input)
        
    else:
        print("Invalid URL. Please enter a valid URL.")


#create Tables for both Tools
local_privacyscore_table = PrettyTable()
local_privacyscore_table.field_names=["URL","cookies","countryName","hastls","https","third"]

local_webbkoll_table=PrettyTable() 
local_webbkoll_table.field_names = ["URL","cookies", "Third", "HSTS Information", "https"]

#Iterate over the entered Websites and extract the specific data
for url in urls:
   print(url)
   #scan the Website with Privacyscore
   command = str(f'privacyscanner scan https://{url}')
   os.system(command) 
   #scan the Website with Webbkoll
   driver.get(f"http://localhost:4000/en/results?url=http%3A%2F%2F{url}")
   time.sleep(3)
   #extract the data from the localhost site
   try:
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.summary > ul:nth-child(1) > li:nth-child(4) > strong:nth-child(2)')))
   except:
       button = driver.find_element('css selector', 'form.search-bar > button:nth-child(3)').click()
       time.sleep(5)
       WebDriverWait(driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,'.summary > ul:nth-child(1) > li:nth-child(4) > strong:nth-child(2)')))
   driver.execute_script("window.scrollTo(0,document.body.dcrollHeight);")
   webbkoll_cookies = driver.find_element('css selector','.summary > ul:nth-child(1) > li:nth-child(4) > strong:nth-child(2)')
   third = driver.find_element('css selector','.summary > ul:nth-child(1) > li:nth-child(5) > strong:nth-child(2)')
   hsts = driver.find_element('css selector','section.result:nth-child(2) > div:nth-child(2) > p:nth-child(1)')
   https = driver.find_element('css selector','#https')
   try:
     cookies_third_div = driver.find_element(By.ID, "cookies-third")
     elements = cookies_third_div.find_elements(By.CSS_SELECTOR, 'table.cookies.data tbody tr td[data-label="Domain"]')
     webbkoll_domain_cookies = [element.text.strip() for element in elements]
   except:
       webbkoll_domain_cookies  = None 
   #add the specific data to the Webbkoll Table
   local_webbkoll_table.add_row([url,int(webbkoll_cookies.text), int(third.text),hsts.text.strip(),https.text.strip()])
   time.sleep(5)

   #list the files in the current directory
   os_list = os.listdir()
   path =  ''
   #Iterate over this list and checks whether the URL entered is included in the file name
   for name in os_list:
    	if url in name:
    		path = name					
    		break
   website_scan_result=f'{path}/results.json'
   #open the corresponding json file found
   with open(website_scan_result) as f: 
       data = json.load(f) 
   #extract the data from the json file  
   try:
      domains = f'www.{url}'
      privacyscore_domain_cookies = []
   
      for cookie in data.get("cookies", []):
          if cookie.get("domain") != domains and cookie.get("domain") != f".{url}":
              privacyscore_domain_cookies.append(cookie["domain"])
      if not privacyscore_domain_cookies:
          privacyscore_domain_cookies = None
   except:
       privacyscore_domain_cookies=None
   try:
       privacyscore_cookies = len(data["cookies"]-len(privacyscore_domain_cookies))
       print(data["cookies"])
   except:
       privacyscore_cookies = None
       
   try:
       countryName = data["mail"]["certificate"]["subject"]["countryName"]
   except:
       countryName = None
   try:
       hasrequests = data["google_analytics"]["has_requests"]
   except:
       hasrequests = None
   try:
       hastls = data["https"]["has_tls"]
   except:
       hastls = None
   try:
       https = data["redirect_chain"][0].split("?")[0]
   except:
       https= None
   try:
       third=len(privacyscore_domain_cookies)
   except:
       third=None
   #add the specific data to the privacyscore Table
   local_privacyscore_table.add_row([url,privacyscore_cookies,countryName,hastls,https,third])
   
print("\n")  
#determine the time and the IP-Address
now=datetime.now()
print("Scan Time:", now)

hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)
print("Your Computer IP Address is:"+IPAddr)
print("\n")

#then add the Tables of both Tools
print("Data with local Webbkoll: ")
print(local_webbkoll_table)
table_string=str(local_webbkoll_table)
print("\n")
print("Data with local Privacyscore:")
print(local_privacyscore_table)
print("\n")

#create a table for related data from webbkoll
local_webbkoll_table_only=PrettyTable() 
local_webbkoll_table_only.field_names=["Third", "HSTS Information"]

#Iterate and search through the original table for the exclusive columns
for row in local_webbkoll_table._rows:
    Third = row[2]
    hsts = row[3]
    
    
    if Third or hsts:
        local_webbkoll_table_only.add_row([Third,hsts])
    else:
        local_webbkoll_table_only.add_row([None,None])

print("Data with local Webbkoll only: ")

print(local_webbkoll_table_only)
print("\n")

#create a table for related data from Privacyscore
local_privacyscore_table_only=PrettyTable() 
local_privacyscore_table_only.field_names = ["countryName","hastls"]

#Iterate and search through the original table for the exclusive columns
for row in local_privacyscore_table._rows:
    countryName = row[2]
    hastls=row[3]
 
    if countryName or hastls:
        local_privacyscore_table_only.add_row([countryName,hastls])
    else:
        local_privacyscore_table_only.add_row([None,None])

print("Data with local Privacyscore only:")
print(local_privacyscore_table_only)
print("\n")
# Close the browser window
driver.quit()

#create a third table for the common data from both tools
common_table = PrettyTable()
common_table.field_names = ["Tool","URL","cookies","cookies_Difference","https"]

#Extract the common columns from Privacyscore table
table1_data=[]
table2_data=[]

for row in local_privacyscore_table._rows:
    URL = row[0]
    privacyscore_cookies = row[1]
    https=row[4]
    
    if URL or privacyscore_cookies or https:
      table1_data.append(["Privacyscore",URL,privacyscore_cookies,https])
      

#Extract the common columns from Webbkoll table

for row in local_webbkoll_table._rows:
    URL = row[0]
    webbkoll_cookies = row[1]
    https=row[4]
    
   
    if URL or webbkoll_cookies or https:
      table2_data.append(["Webbkoll",URL,webbkoll_cookies,https])
#add the common colmuns  in the third table 
for data1 in table1_data:
    for data2 in table2_data:
        if data1[2] is not None and data2[2] is not None:
           diff1=data1[2]-data2[2]
           diff2=data2[2]-data1[2]
           common_table.add_row([data1[0],data1[1],data1[2],diff1,data1[3]])
           common_table.add_row([data2[0],data2[1],data2[2],diff2,data2[3]])
         
        else:
           common_table.add_row([data1[0],data1[1],data1[2],None,data1[3]])
           common_table.add_row([data2[0],data2[1],data2[2],None,data2[3]])
           
print("common data table:")
print(common_table) 

def clone_or_pull_repo(repo_url, local_folder):
    #update the DisconnectMe Trackerlist if it already exist
    try:
        repo = git.Repo(local_folder)
        origin = repo.remote(name='origin')
        origin.pull()
        print("Pulled changes from " + repo_url + " to " + local_folder)

        #if it doesnt exist, clone it from the github repo
    except InvalidGitRepositoryError:
        repo = git.Repo.clone_from(repo_url, local_folder)
        print("Cloned " + repo_url + " to " + local_folder)
def check_found_Cookies_with_DisconnectMeList(stringArray_with_cookies):

    #array which which also store information about DisconnectMe information on the cookies
    processed_stringArray_with_cookies = []


    #load TrackerList json file
    with open('DisconnectMe/services.json', 'rb') as known_tracker_list: 
        loaded_known_tracker_list = json.load(known_tracker_list)

    #iterate through cookies that we found with webkoll/privacyscore
    for cookie in stringArray_with_cookies:
	tmpSplit = cookie.split(".")    
	domain = ".".join(tmpSplit[-2:])
        #iterate through the the different Tracker categories of the DisconnectMe and check if it contains our cookie
        tracker_counter = 0
        for category in loaded_known_tracker_list["categories"]:
            for trackerlist in loaded_known_tracker_list["categories"][category]:
                trackerlist_str = str(trackerlist)
                #when we find first match:
                if (domain in trackerlist_str and tracker_counter == 0 ):
                    processed_stringArray_with_cookies.append(cookie + " found in: " + category)
                    tracker_counter = tracker_counter + 1
               #when we find the cookie in another category
                elif (domain in trackerlist_str and tracker_counter > 0 ):
                    processed_stringArray_with_cookies[-1] += ", " + category

        #when we find no hits we just add cookie to array and mention that it is not in DisconnectMeList
        if (tracker_counter == 0):
            processed_stringArray_with_cookies.append(cookie + " not found in DisconnectMe List")




    return processed_stringArray_with_cookies
repo_url = "https://github.com/disconnectme/disconnect-tracking-protection"

#create path to desired folder loaction of DisconnectMe TrackerList
parent_dir =  os.getcwd()
directory = "DisconnectMe"
path = os.path.join(parent_dir, directory)

#create Folder for DisconnectMe TrackerList if needed
try:
    os.mkdir(path)
except:
    print("Folder named Disconnect Me already exists. Will try to pull changes from remote repo.")

clone_or_pull_repo("https://github.com/disconnectme/disconnect-tracking-protection", path)
stringArray_with_cookies = ["https://www.acoustic.com/", ".bing.com","c.clarity.ms" ]
processedArray = check_found_Cookies_with_DisconnectMeList(stringArray_with_cookies)

print(stringArray_with_cookies)
print(processedArray)
print("\n")

    

def create_scan_results_folder(website_name, webbkoll_cookies,privacyscore_cookies):
    folder_path="/home/drivingswarm/Desktop"
    folder_name = "Scan Results For " + website_name
    full_path = os.path.join(folder_path, folder_name)
    cookies_folder=os.path.join(full_path,"Cookies_Folder")
    # make a Folder for the scan Results and zip it
    try:
        os.makedirs(full_path)
        # make a Folder for the cookies lists in the Folder of scan Results
        os.makedirs(cookies_folder)
        shutil.make_archive(full_path, 'zip',full_path)
        print("Scan Results Folder created")

    except FileExistsError:
        print("Scan Results Folder already exists.")

    #create a text file for each cookies list
    webbkoll_cookies_file=os.path.join(cookies_folder, "Webbkoll-" + website_name + ".txt")
    privacyscore_cookies_file=os.path.join(cookies_folder, "PrivacyScore-"  + website_name + ".txt")
    
    #If no list was found, write it to the related text file
    if webbkoll_cookies is None:
       with open(webbkoll_cookies_file,'w') as file:
            file.write("No Third party Cookies found by Webbkoll"+'\n')
    if privacyscore_cookies is None:
       with open(privacyscore_cookies_file,'w') as file:
            file.write("No Third party Cookies found by Privacyscore"+'\n')
    write_list_to_file(webbkoll_cookies_file, webbkoll_cookies)
    write_list_to_file(privacyscore_cookies_file, privacyscore_cookies)
    
    #create a text file for the intersecton between the both cookies lists
    intersection_path = os.path.join(cookies_folder, "Intersection-" + website_name + ".txt")
    write_intersection_to_file(intersection_path, webbkoll_cookies, privacyscore_cookies)
    
    #take a copy of the related json file in the scan results Folder
    shutil.copy(website_scan_result, full_path)
    
    #create a text file for the Report and write this data in it
    Report_path=os.path.join(full_path,'Report.txt')
    with open(Report_path, 'w') as file:
       file.write("Metadata:"+'\n\n')
       file.write("Your Computer IP Address is:" + IPAddr + '\n\n')
       file.write("Scan Time:"+ str(now)+ '\n\n')
       file.write("Scan Results:"+'\n\n')
       file.write("Data with local Webbkoll: \n" +str(local_webbkoll_table) + '\n\n')
       file.write("Data with local Privacyscore:\n" + str(local_privacyscore_table) + '\n\n')
       file.write("Data with local Webbkoll only: \n" + str(local_webbkoll_table_only) + '\n\n')
       file.write("Data with local Privacyscore only:\n" + str(local_privacyscore_table_only) + '\n\n')
       file.write("Common data table:\n" + str(common_table) + '\n')


def write_list_to_file(file_path, data_list):

    #check whether the cookies lists were found
    if data_list is None:
        print("One or both of the tools don't have a cookies list")
    else:
        with open(file_path, 'w') as file:
        #writes each element in a new line of the document
            for item in data_list:
            
                file.write(str(item) + '\n')
                
def write_intersection_to_file(file_path, list1, list2):

    #check whether the both cookies lists were found
    if list1 is None or list2 is None:
        print("Both lists are required to find the intersection.")
    else:
        intersection = list(set(list1).intersection(list2))
        with open(file_path, 'w') as file:
            for item in intersection:
                file.write(str(item) + '\n')

def main():
  
    create_scan_results_folder(url,webbkoll_domain_cookies,privacyscore_domain_cookies)

if __name__ == "__main__":
    main()
 
 
 
 
"""
#create table for online webbkoll
online_webbkoll_table = PrettyTable()

def extract_webbkoll_data(urls, keys_to_find):
    # Create a table with column headings
   
    online_webbkoll_table.field_names = ['URL'] + keys_to_find  # Include the keys in the table headers
    
    # Create mechanize browser object
    br = mechanize.Browser()
    
    # Iterate over each URL
    for url in urls:
        # Open website and select form
        br.open("https://webbkoll.dataskydd.net/en/")
        br.select_form(nr=0)
        
        # Enter URL in form
        br.form['url'] = url

        # Submit form and get response
        response = br.submit()
        
        # Parse response with BeautifulSoup
        soup = BeautifulSoup(br.response().read(), 'html.parser')
        
        # Initialize a dictionary to store the extracted data
        try:
            cookies = soup.find_all("strong")[0]
            third = soup.find_all("strong")[1]
            # Get text for HTTPS and HSTS information
            https=soup.find_all("h3")[0]
            hsts = soup.find_all("p")[8]
            #IP=soup.find_all("p")[8]

            # Add a row to the table
            online_webbkoll_table.add_row([url, int(cookies.text),
             int(third.text),hsts.text.strip(),https.text.strip()])
        except:
            print(f'{url} error')

    # Print the table
    print("\n")
    print("Data with online Webbkoll: ")
    print(online_webbkoll_table)
    
   
online_privacyscore_table = PrettyTable()
def extract_privacyscore_data(urls,keys_to_find):

	# Create a dictionary to store the counts of each rating
    rating_counts = {'❗': 0, '⨂': 0, '❓': 0}
	# Create mechanize browser object
    br = mechanize.Browser()
	 
    
    # Create a table with column headings 
    online_privacyscore_table.field_names=["URL"]+["cookies"]+keys_to_find[1:]
    for url in urls:
    	# Open website and select form
    	br.open("https://privacyscore.org")
    	br.select_form(nr = 2)

    	br.form['url'] = url
    	# Submit form and get response
    	response = br.submit()
    	current_url = br.geturl()
    	if 'created' in current_url:
        	current_url = current_url.replace('created','')
    	parse = requests.get(f'{current_url}',timeout=60)
    	# Parse HTML content
    	soup = BeautifulSoup(parse.content, 'html.parser')	 
    	div = soup.find('div', class_='text-center')
    	icon = div.find('i').get('class')[2]
    	if icon == 'fa-exclamation-circle':
        	overall_rating = '❗'
    	elif icon == 'fa-times-circle':
        	overall_rating = '⨂'
    	elif icon == 'fa-question-circle':
        	overall_rating = '❓'
    	parse = requests.get(f'{current_url}json')
    	data={}
    	# Parse HTML content
    	soup = BeautifulSoup(parse.content, 'html.parser')
    	# Find all span elements
    	spans = soup.find_all('span')
    	# Initialize variables to store extracted data
    	span_text = [spans[i].text for i in range(8,len(spans)-1)]
    	json_string = ''.join(span_text)
    	data = json.loads(json_string)
    	
    	#Extract data based on keys_to_find
    	row_data=[url]
    	for key in keys_to_find:
    	    value=data.get(key)
    	    if isinstance(value,bool):
    	       value='✔️' if value else '❌'
    	    row_data.append(value)
    	# Add a row to the table
    	online_privacyscore_table.add_row(row_data)
    	
    	# Increment the count for the overall rating
    	rating_counts[overall_rating] += 1
	# Print the table
    print("\n")
    print("Data with online Privacyscore: ")
    print(online_privacyscore_table)
    print("\n")





def compare_both_tools(tables):
   

    # Initialisiere common_columns als leere Liste
    common_columns = []

    # iterate the column names of the first table
    for column1 in tables[0].field_names:
    # Assumption: The column is common in all tables until proven otherwise
        is_common = True
    # iterate through the other tables and check if the column exists
        for table in tables[1:]:
            if column1 not in table.field_names:
               is_common = False
               break
     #If the column exists in all tables, add it to common_columns
        if is_common:
           common_columns.append(column1)

     # Check if common columns were found
    if common_columns:
       print("Common columns in the tables:", common_columns,"\n")
    else:
       print("The tables have different column name")
    #Compare the entries in the common columns
    for column in common_columns:
        if column=="URL":
            continue
        index1 = tables[0].field_names.index(column)
        index2 = tables[1].field_names.index(column)
        values1 = [row[index1] for row in tables[0]._rows]
        values2 = [row[index2] for row in tables[1]._rows]
     # Compare the values ​​in the columns
        for value1, value2 in zip(values1, values2):
            if value1 == value2 or value1=="✅ HTTPS by default 🔗":
            
                 print(f"The values ​​in column'{column}' are equal: {value1}")
                 
            else:
                 print(f"The values ​​in column '{column}' are different: {value1} vs {value2}")
                 
        print("\n")
"""
 # Main function to run web scraper and show compare results

#def main():
    # List of URLs to scrape
    #urls_list = urls
    #tables of both tools
    #privacyscore_tables = [local_privacyscore_table, online_privacyscore_table]
    #webbkoll_tables=[local_webbkoll_table,online_webbkoll_table]
    
    #lists to find keys of both tables
    #Webbkoll_keys_to_find = ["Cookies", "Third", "HSTS Information","HTTPS Information"]
    #Privacyscore_keys_to_find=["cookies_count","https","reachable", "web_has_protocol_tls1_2","web_has_protocol_tls1","mx_locations","a_locations"]
    
    #Extract data from URLs
    #extract_webbkoll_data(urls_list,Webbkoll_keys_to_find)  
    #extract_privacyscore_data(urls_list,Privacyscore_keys_to_find) 
    
    #compare tables of both tools
    #print("Results fo comparing PrivacyScore:\n")
    #compare_both_tools(privacyscore_tables)
    #print("Results of compaing Webbkoll:\n")
    #compare_both_tools(webbkoll_tables)

#if __name__ == "__main__":
 #   main()
 


