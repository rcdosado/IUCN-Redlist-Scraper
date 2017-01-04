import requests
from bs4 import BeautifulSoup

import utils
from utils import online


class IUCN_Redlist:
    """
    
        An IUCN Scraper
    """
 
    
    SEARCH_PAGE = 'http://www.iucnredlist.org/search/external'
    SEARCH_RESULT_SELECTOR = '#searchResults > div > span'
        
    SEARCH_HTTP_HEADER = {
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
    
    SEARCH_PAYLOAD = {
        'text':'',
        'mode':'',
        'x':'17',
        'y':'9',
    }
    

    def __init__(self):
        self.search_status = 0
        self.session = requests.session()

        
##        if not online():
##            raise EnvironmentError("Internet Connection Error")
    
    # Search a specie from IUCN Redlist site and return a list of results, each item an URL
    # Returns None if no results
    def search(self, species):
        
        # dump raw result
        raw_page = self._find_and_dump( species.strip())
        
        # gives back a list containing dictionary about the result
        # returns len(response) > 1 if multiple results
        
        response = self._get_response( raw_page)
            
        iucn = IUCN_Result( response)
        return iucn 
    
    def _find_and_dump(self, inquiry):

        
        self.SEARCH_PAYLOAD['text'] = inquiry

        # this code search the database for specific specie
        r = self.session.post(self.SEARCH_PAGE,
                              headers=self.SEARCH_HTTP_HEADER,
                              data=self.SEARCH_PAYLOAD)

        # gives a raw dump of the page
        return r.text 
    
    def _get_response(self, result_page):
        
        # parse with the BS library
        soup = BeautifulSoup(result_page,'html.parser')
        
        # Retrieve number of results
        found = self._get_search_result(soup)
        
        self.search_status = found
        
        return self._format_response(found, soup)

    def _format_response(self, found, soup):
        if found == 0 or found == -1:
            return None
        
        # return lists of raw HTML classes
        matches = self._select_classes_with_name("desc", soup)
        
        infos = []
        
        for match in matches:
            info = self._get_match_details(match)
            infos.append(info)            
        return infos
    
    def _get_match_details(self, match):
        # get all links
        links = match.findAll('a')
        
        # assume first link is occurence map
        map_detail = links[0]['href']
        
        # grab the URL of the specie details
        species_detail = self._convert_to_url(self.SEARCH_HTTP_HEADER["Host"],
                             links[1]['href'])
        
        # the main description, needs serious parsing
        contents = match.text
        
        # dump as dict
        info = {
                
            "map":map_detail ,
            "page":species_detail,
            "content":contents
        }
        
        return info

    def _convert_to_url(self, host, res):
        return "http://" + host + res


    def _get_search_result(self, soup):
        """ 
           extracts the status of search
           ------------------------------
           soup is a BeautifulSoup instance
           based from samples, it can be:
           No entries found
           all *  (asterisk being a number of results)
        """
        NOT_FOUND = -1
        raw_status = str(soup.select(self.SEARCH_RESULT_SELECTOR)[0])

        if raw_status.find("one") != NOT_FOUND:
            self.search_result_count = 1
            
        elif raw_status.find("all") != NOT_FOUND:
            num = int(utils.get_numbers_from_html(raw_status)[0])
            self.search_result_count = num
            
        elif raw_status.find("No entries") != NOT_FOUND:
            self.search_result_count = 0
            
        else:
            self.search_result_count = NOT_FOUND
            
        return self.search_result_count
        
    def _select_classes_with_name(self, classname, soup):           
        matches = soup.find_all(utils.match_class([classname]))        
        return matches
     


   
class ConservationStatus:
    NOT_EVALUATED = 1
    DATA_DEFICIENT = 2
    LEAST_CONCERN = 3
    NEAR_THREATENED = 4
    VULNERABLE = 5
    ENDANGERED = 6
    CRITICALLY_ENDANGERED = 7
    EXTINCT_IN_THE_WILD = 8
    EXTINCT = 9
    UNKNOWN = 10
    
    
    
class IUCN_Result:
    DETAIL_HTTP_HEADER = {
        'Host': 'www.iucnredlist.org',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
    }     
    # search_result is a list of results dictionary, if length is > 1, means multiple result
    def __init__(self, search_result = None):
        
        if search_result is None:
            raise ValueError("Parameter to object invalid")
        
        if len(search_result) > 1:
            raise ValueError("Cannot handle multiple results feature yet. ")
                
        self.count = len(search_result)
        self.search_data = search_result        
        
        # open a requests session
        self.session = requests.session()  
   
    def get_details(self, raw_html=None):
        if raw_html == None and self.search_data:
            raw_html = self._fetch_page(self.search_data[0]["page"])

        self.soup = BeautifulSoup(raw_html,"html.parser")
        
        details = {}
        
        details["search_result"] = self.search_data[0]
        details["header"] = self._get_header_details(self.soup) 
        details["taxonomy"] = self._get_taxonomic_details(self.soup)
        details["assessment_information"] = self._get_assessment_details(self.soup) 
        details["geographic_range"] = self._get_geographic_range_details(self.soup)
        details["population"] = self._get_population_details(self.soup)
        details["habitat_and_ecology"] = self._get_habitat_ecology_details(self.soup)
        details["use_and_trade"]= self._get_use_and_trade_details(self.soup)
        details["threats"]= self._get_threats_details(self.soup)
        details["conservation_actions"] = self._get_conservation_actions_details(self.soup)

        return details
    
    def _get_header_details(self, soup):
        # get index detail first
        heading_info = {}
        
        try:
            heading_info["scientific_name"] = self._get_title_page(soup)        
            heading_info["doi"] = self._get_doi_url(soup)
            heading_info["location_map"] = self._get_map_url_location(soup)
            heading_info["conservation_status"] = self._get_conservation_status(soup)
        except (IndexError, TypeError): 
            pass
        
        return heading_info
    
    def _get_title_page(self, soup):
        matches = soup.find_all(utils.match_class(["sciname"]))
        return matches[0].text
    
    def _get_doi_url(self,soup):
        matches = soup.find_all(utils.match_class(["doi_link"]))         
        if not utils.is_valid_url(matches[0].text):
            matches = soup.find_all(utils.match_class(["doi_link top"]))
            return matches[0].text
        
        return matches[0].text
        
    def _get_map_url_location(self,soup):
        matches = soup.select('#leftcol > a')
        return matches[0]['href']
        
    def _get_conservation_status(self,soup):
        images = soup.select('#scale_factsheet')[0].findChildren()
             
        # enumerate all images, find who's have status on, 
        # return immediately with status when detected
        
        for img in images:
            splits = img['alt'].split('_')
            if splits[2] == 'on':
                return splits[1]
        
        # return default if anything goes wrong    
        return self.splits[1]
    #--------------------------------------------------------
    
    def _get_taxonomic_details(self, soup):
        
        taxon = self._extract_table_by_index(0,soup)
      
        data = {}

        try:
            data["kingdom"] = taxon[0].text.strip()
            data["phylum"] = taxon[1].text.strip()
            data["class"] = taxon[2].text.strip()
            data["order"] = taxon[3].text.strip()
            data["family"] = taxon[4].text.strip()
        
            taxon_other = self._extract_table_by_index(1,soup)
    
            data["scientific_name"] = taxon_other[1].text.strip()
            data["species_authority"] = taxon_other[3].text.strip()
            data["taxonomic_notes"] = taxon_other[5].text.strip()
        except (IndexError, TypeError):  
            pass
        
        return data
        
    def _get_assessment_details(self,soup):
        
        data = {}
        try:
            info = self._extract_table_by_index(2,soup)
            data["red_list_category_and_criteria"] = info[1].text.strip()
            data["year_published"] = info[3].text.strip()
            data["date_assessed"] = info[5].text.strip()
            data["assessors"] = info[7].text.strip()
            data["reviewers"] = info[9].text.strip()
            data["justification"] = info[10].text.split('\n')[2]
        except (IndexError, TypeError):  
            pass
        
        return data
        
        
    def _get_geographic_range_details(self,soup):

        data = {}
        
        try:
            info = self._extract_table_by_index(3,soup)
            data["range_description"] = info[1].text.strip()
            data["countries_occurence"] = info[3].text.strip()
            data["FAO_marine_fishing_areas"] = info[5].text.strip()
            data["additional_data"] = info[6].text.strip()
            data["range_map"] = info[8].find('a')['href']
        except (IndexError, TypeError):           
            pass
        
        return data
    
    def _get_population_details(self,soup):
        
        
        data = {}
        
        try:
            info = self._extract_table_by_index(4,soup)
            data["population"] = info[1].text.strip()
            data["current_population_trend"] = info[3].text.strip()
            data["additional_data"] = info[4].text.strip()
        except (IndexError, TypeError):  
            pass 
        
        return data
    
        
    def _get_habitat_ecology_details(self,soup):

        data = {}
        
        try:
            info = self._extract_table_by_index(5,soup)            
            data["habitat_and_ecology"] = info[1].text.strip()
            data["systems"] = info[3].text.strip()
            data["generation_length"] = info[4].text.strip()
        except (IndexError, TypeError):  
            pass 
        
        return data
    def _get_use_and_trade_details(self, soup):
        
        data = {}
        
        try:
            info = self._extract_table_by_index(6,soup)
            data["use_and_trade"] = info[1].text.strip()
        except (IndexError, TypeError):  
            pass 
        
        return data
        
    def _get_threats_details(self,soup):
        
        data = {}
        
        try:
            info = self._extract_table_by_index(7,soup)
            data["major_threats"] = info[1].text.strip()
        except (IndexError, TypeError):  
            pass
        
        return data        
    
    def _get_conservation_actions_details(self, soup):
        
        data = {}
        
        try:
            info = self._extract_table_by_index(8,soup)
            data["conservation_actions"] = info[1].text.strip()
        except (IndexError, TypeError):  
            pass
        
        return data                

    def _extract_table_by_index(self, i, soup):
        tables = self._get_all_table_groups(soup)
        info = tables[i].findAll('td')        
        return info
    
# some built in utilities -----------------------------------------------------
    def _fetch_page(self, url):
        # Request the specific page of the search result
        r = self.session.get(url, headers=self.DETAIL_HTTP_HEADER)           
        return r.text

    
    def _get_all_table_groups(self, soup):
        # Select all tables inside data_factsheet id
        table_rows = soup.select("div#data_factsheet")        
        return table_rows[0].select('table.tab_data')

    def _convert_to_status(self, status):
        if status == 'ne':
            return ConservationStatus.NOT_EVALUATED
        elif status == 'dd':
            return ConservationStatus.DATA_DEFICIENT
        elif status == 'lc':
            return ConservationStatus.LEAST_CONCERN
        elif status == 'nt':
            return ConservationStatus.NEAR_THREATENED
        elif status == 'vu':
            return ConservationStatus.VULNERABLE
        elif status == 'en':
            return ConservationStatus.ENDANGERED
        elif status == 'cr':
            return ConservationStatus.CRITICALLY_ENDANGERED
        elif status == 'ew':
            return ConservationStatus.EXTINCT_IN_THE_WILD
        elif status == 'ex':
            return ConservationStatus.EXTINCT
        else:
            return ConservationStatus.UNKNOWN
    