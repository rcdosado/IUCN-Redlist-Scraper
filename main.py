import requests
import argparse
import datetime
from bs4 import BeautifulSoup
from random import randint
from time import sleep

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)     
    return regex.match(url)

def convert_full_url_to_map_url(url):
    return 'http://maps.iucnredlist.org/map.html?id='+url.split('/')[-2]

def match_class(target):                                                        
    def do_match(tag):                                                          
        classes = tag.get('class', [])                                          
        return all(c in classes for c in target)                                
    return do_match   

# search IUCN Redlist for specific specie, use scientific name as parameter
# returns URL on success, None Otherwise
def search_iucn(specie):
    headers = {
               'Host': 'www.iucnredlist.org',
               'Cache-Control': 'max-age=0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Origin': 'http://www.iucnredlist.org',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36',
               'Content-Type': 'application/x-www-form-urlencoded',
               'Referer': 'http://www.iucnredlist.org/',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.8',
               }
    payload = {'text':'',
               'mode':'',
               'x':'17',
               'y':'9',
               }
    
    payload['text'] = specie
    search_url = 'http://www.iucnredlist.org/search/external'
    
    # this code search the database for specific specie
    r = session.post(search_url,headers=headers,data=payload)
    
    # parse with the BS library
    soup = BeautifulSoup(r.text,'html.parser')
    
    # returns something like u'/details/178809/0'
    matches = soup.find_all(match_class(["title"]))
    
    # matches may be more than one item, better be specific in your search term
    # the code below gets the first result only
    try:
        resource_link = matches[1]['href']
    except IndexError:
        return None
        
    ### build the full URL
    return 'http://'+headers['Host']+resource_link
    
    

def scrape(url):
    header2 = {
        'Host': 'www.iucnredlist.org',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
    }

    # Request the specific page of the search result
    r = session.get(full_url, headers=header2)
    soup = BeautifulSoup(r.text,'html.parser')

    

    info_list = []
    
    current_date_time = str(datetime.datetime.now())
    
    info0 = {
        'full_url' : full_url,
        'date_added' : current_date_time,
        
        #add other metadata here
    }
    
    info_list.append(info0)
    
    # Select all tables inside data_factsheet id
    table_rows = soup.select("div#data_factsheet > table.tab_data")
    
    # Get Taxonomy
    cells = table_rows[0].findAll('td')
    
    kingdom = cells[0].text.strip()
    phylum = cells[1].text.strip()
    class_ = cells[2].text.strip()
    order = cells[3].text.strip()
    family = cells[4].text.strip()
    
    
    info1 = {
        'Kingdom': kingdom,
        'Phylum' : phylum,
        'Class' :class_,
        'Order' : order,
        'Family': family,
    }
    
    info_list.append(info1)
    
    cells = table_rows[1].findAll('td')
    
    scientific_name = cells[1].text.strip()
    species_authority = cells[3].text.strip().replace(',','-')
    
    info2 = {
        'Scientific_Name':scientific_name,
        'Species_Authority':species_authority,
    }
    
    info_list.append(info2)
    print("[+] Done processing Taxonomy")
    
 
    # Get Assessment Information
    cells = table_rows[2].findAll('td')
    
    # Do Processing here.. discard for now
    print("[+] Done processing Assessment Information")
    
    # Get Geographic Range
    cells = table_rows[3].findAll('td')
    
    range_description = cells[1].text.strip()
    countries_occurence = cells[3].text.strip()
    fao_marine_fishing_areas = cells[5].text.strip()
    additional_data = ' ' if cells[6].text.strip() == '' else cells[6].text.strip()
    range_map =  convert_full_url_to_map_url(full_url)
    print(range_map)
    info4 = {
        'Range_Description' : range_description,
        'Countries_Occurence' : countries_occurence,
        'FAO_Marine_Fishing_Areas' : fao_marine_fishing_areas,
        'Additional_Data':additional_data,
        'Range_Map' : range_map,
    }
    
    info_list.append(info4)
    
    print("[+] Done Processing Geographic Range")
    
##    # Get Population Info
    
##    cells = table_rows[4].findAll('td')
    
##    print("[+] Done Processing Population")
    
        
##    # Get Habitat and Ecology
    
##    cells = table_rows[5].findAll('td')
    
##    print("[+] Done Processing Habitat and Ecology ")
    
    
##    # Get Use and Trade Info
    
##    cells = table_rows[6].findAll('td')
    
##    print("[+] Done Processing Use and Trade Information")
    
    
##    # Get Threats information
    
##    cells = table_rows[7].findAll('td')
    
##    print("[+] Done Processing Threats Information")
    
    return info_list

def convert_specie_to_filename(specie):
    
    converted_as_filename = specie.replace(' ','_')+'.json'
    
    return converted_as_filename

def dump_dict_to_json(info_list,specie):
    import io,json
    json_format = json.dumps(info_list)
    filename = convert_specie_to_filename(specie)
    with io.open(filename, 'w', encoding='utf-8') as f:
        ret=f.write(unicode(json.dumps(info_list,indent=4, ensure_ascii=False)))
    return  ret


parser = argparse.ArgumentParser(description="Scrape Species Information in IUCN RedList")
parser.add_argument('filename', help='')
                 

args = parser.parse_args()

f = open(args.filename, "r")
scientific_names = f.readlines();
f.close()

##exit(-1)

# setup session, all HTTP request will use this variable
session = requests.Session()
specie_counter = 0

found = open("found.txt", "w")
notfound = open("notfound.txt", "w")

found_counter = 0
notfound_counter = 0

for scientific_name in scientific_names:
    specie = scientific_name.strip() 
    
    sleep(randint(1,3))
    
    full_url = search_iucn(specie)
    print("[+] finding "+specie+" on iucnredlist website")
    if full_url is None:
        notfound.write(specie+"\n")
        notfound_counter = found_counter+1
        print("[-] Cannot find this specie, continuing to next specie\n")
        continue
    print("[+] Started Scraping : "+ full_url)
    
    result = scrape(full_url)
    print("[+] Done with "+ specie +"\n\n")
    dump_dict_to_json(result, specie)
    found.write(specie+"\n")
    found_counter = found_counter+1
    specie_counter = specie_counter+1

notfound.write("\n\n "+str(found_counter - 1)+" Specie(s) not found\n")
found.write("\n\nScraped only "+str(notfound_counter - 1)+" Species\n")
found.close()
notfound.close()

print("Scraped "+str(specie_counter)+" out of "+ str(len(scientific_names))+" contents")
