import unittest
from bs4 import BeautifulSoup
from mockito import *
from iucn import IUCN_Redlist , IUCN_Result, ConservationStatus

import pagedumps
import utils


# Testing only a class 
# nosetests <PATH>/<FILENAME>:<CLASS_NAME>
# e.g nosetests tests/iucn_tests.py:Test_Species_Details
# or nosetests iucn_tests.py:Test_Species_Details

class Test_Search_IUCN(unittest.TestCase):
    
    def setUp(self):
        pass 
   
    def test_search_with_single_result_returns_one_item(self):
        iucn = IUCN_Redlist()
        result = len(iucn._get_response(pagedumps.SINGLE_RESULT_PAGE)) 
        self.assertEquals(result, 1)
        
    def test_search_with_multiple_result_returns_two_items(self):
        iucn = IUCN_Redlist()
        result = len(iucn._get_response(pagedumps.MULTIPLE_RESULTS_PAGE))
        self.assertEquals(result, 2)
        
    def test_get_search_status_one_found(self):
        iucn = IUCN_Redlist()
        soup = BeautifulSoup(pagedumps.STATUS_QUERY_ONE_FOUND,"html.parser")
        result = iucn._get_search_result(soup)
        self.assertEquals(result,1)
   
    def test_get_search_status_none_found(self):
        iucn = IUCN_Redlist()
        soup = BeautifulSoup(pagedumps.STATUS_QUERY_NOT_FOUND,"html.parser")
        result = iucn._get_search_result(soup)
        self.assertEquals(result,0)
        
    def test_get_response_when_specie_not_found(self):
        iucn = IUCN_Redlist()
        result = iucn._get_response(pagedumps.STATUS_QUERY_NOT_FOUND)
        self.assertEquals(result, None)
        self.assertEquals(iucn.search_status, 0 )
        
    def test_get_search_status_multiple_found(self):
        iucn = IUCN_Redlist()
        soup = BeautifulSoup(pagedumps.STATUS_QUERY_MULTIPLE_FOUND,"html.parser")
        result = iucn._get_search_result(soup)
        self.assertGreater(result,1)
    
    def test_search_iucn_returning_single_result(self):
        when(IUCN_Redlist)._find_and_dump('Avicennia rumphiana').thenReturn(pagedumps.SINGLE_RESULT_PAGE)
        iucn = IUCN_Redlist()
        result = iucn.search('Avicennia rumphiana')
        self.assertTrue(isinstance(result,IUCN_Result))

        
    def test_search_iucn_returning_single_result_content(self):
        when(IUCN_Redlist)._find_and_dump('Avicennia rumphiana').thenReturn(pagedumps.SINGLE_RESULT_PAGE)
        iucn = IUCN_Redlist()
        response = iucn.search('Avicennia rumphiana')
        self.assertEquals(response.count,1)
        self.assertEquals(response.search_data,[{'content': u'\n\n\nAvicennia rumphiana\n\n\n    Status:\n    Vulnerable\n\n\n    A2c\n\n    ver 3.1\n\n\n      Pop. trend: decreasing\n  ', 
                                  'map': u'http://maps.iucnredlist.org/map.html?id=178809', 
                                  'page': u'http://www.iucnredlist.org/details/178809/0'}])
        
##    TODO: answer, how to choose which to dump when there's multiple result in search?
##    def test_search_iucn_returning_multiple_result_content(self):
##        when(IUCN_Redlist)._find_and_dump('Sus barbatus').thenReturn(pagedumps.MULTIPLE_RESULTS_PAGE)
##        iucn = IUCN_Redlist()
##        response = iucn.search('Sus barbatus')
##        self.assertEquals(response.count,2)
##        self.assertEquals(response.search_data,[{'content': u'\n\n\nSus ahoenobarbus\n\n    (Palawan Bearded Pig)\n    \n\n    Status:\n    Vulnerable\n\n\n    B1ab(iii,v)\n\n    ver 3.1\n\n\n      Pop. trend: decreasing\n  ', 
##                                                 'map': u'http://maps.iucnredlist.org/map.html?id=21177', 
##                                                 'page': u'http://www.iucnredlist.org/details/21177/0'}, 
##                                                {'content': u'\n\n\nSus barbatus\n\n    (Bearded Pig)\n    \n\n    Status:\n    Vulnerable\n\n\n    A2cd\n\n    ver 3.1\n\n\n      Pop. trend: decreasing\n  ', 
##                                                 'map': u'http://maps.iucnredlist.org/map.html?id=41772', 
##                                                 'page': u'http://www.iucnredlist.org/details/41772/0'}])
        
    def tearDown(self):
        pass
    
    
class Test_Utilities(unittest.TestCase):    
    def setUp(self):
        pass
    
    # incomplete -- No test for False?
##    def test_for_internet_connection(self):
##        self.assertEquals(utils.online (), True)
    def test_get_numbers_from_string_with_spaces(self):
        input1="9 10 81 2016"
        input2="9  10 81   2016"
        
        list_numbers = utils.get_numbers_from_string_with_spaces(input1)
        self.assertEquals(list_numbers,[9,10,81,2016])
        
        list_numbers = utils.get_numbers_from_string_with_spaces(input2)        
        self.assertEquals(list_numbers,[9,10,81,2016])        
        
    def tearDown(self):
        pass
    
class Test_Species_Details(unittest.TestCase):
    
    # Avicennia rumphiana
    SAMPLE_SPECIE_URL = 'http://www.iucnredlist.org/details/178809/0'
    SAMPLE_SPECIE_SINGLE_RESULT = [{'content': u'\n\n\nAvicennia rumphiana\n\n\n    Status:\n    Vulnerable\n\n\n    A2c\n\n    ver 3.1\n\n\n      Pop. trend: decreasing\n  ', 
                                  'map': u'http://maps.iucnredlist.org/map.html?id=178809', 
                                  'page': u'http://www.iucnredlist.org/details/178809/0'}]
    info = None
    iucn = None
    
    def setUp(self):
        self.iucn = IUCN_Result(self.SAMPLE_SPECIE_SINGLE_RESULT)        
        self.info = self.iucn.get_details(pagedumps.DETAIL_PAGE_DUMP)
    
    def test_if_info_contains_search_info(self):
        self.assertEquals(self.info["search_result"],{'content': u'\n\n\nAvicennia rumphiana\n\n\n    Status:\n    Vulnerable\n\n\n    A2c\n\n    ver 3.1\n\n\n      Pop. trend: decreasing\n  ', 
                                                      'map': u'http://maps.iucnredlist.org/map.html?id=178809', 
                                                      'page': u'http://www.iucnredlist.org/details/178809/0'})
    def test_if_info_contains_header(self):
        self.assertEquals(self.info["header"]["scientific_name"],u'Avicennia rumphiana')
        self.assertEquals(self.info["header"]["doi"],u'http://dx.doi.org/10.2305/IUCN.UK.2010-2.RLTS.T178809A7613129.en') 
        self.assertEquals(self.info["header"]["location_map"],u'http://maps.iucnredlist.org/map.html?id=178809')        
        self.assertEquals(self.info["header"]["conservation_status"],'vu')
  
    def test_if_info_contains_taxonomic_data(self):
        self.assertEquals(self.info["taxonomy"]["kingdom"],u"Plantae")
        self.assertEquals(self.info["taxonomy"]["phylum"],u"Tracheophyta")        
        self.assertEquals(self.info["taxonomy"]["class"],u"Magnoliopsida")
        self.assertEquals(self.info["taxonomy"]["order"],u"Lamiales")
        self.assertEquals(self.info["taxonomy"]["family"],u"Avicenniaceae")
        self.assertEquals(self.info["taxonomy"]["scientific_name"],u"Avicennia rumphiana")
        self.assertEquals(self.info["taxonomy"]["species_authority"],u"Hallier f.")
        self.assertEquals(self.info["taxonomy"]["taxonomic_notes"],u"This species used to be considered a variety of A. marina.")
        
    def test_if_info_contains_assessment_information(self):
        self.assertEquals(self.info["assessment_information"]["red_list_category_and_criteria"],u'Vulnerable\n\n\n    A2c\n\n    ver 3.1')
        self.assertEquals(self.info["assessment_information"]["year_published"],u'2010')
        self.assertEquals(self.info["assessment_information"]["date_assessed"],u"2008-03-07")
        self.assertEquals(self.info["assessment_information"]["assessors"],u"Duke, N., Kathiresan, K., Salmo III, S.G., Fernando, E.S., Peras, J.R., Sukardjo, S. & Miyagi, T.")
        self.assertEquals(self.info["assessment_information"]["reviewers"],u"Polidoro, B.A., Livingstone, S.R. & Carpenter, K.E. (Global Marine Species Assessment Coordinating Team)")
        self.assertEquals(len(self.info["assessment_information"]["justification"]),626)
        
    def test_if_info_contains_geographic_range(self):
        self.assertEquals(self.info["geographic_range"]["range_description"],u"This species has a disjunct range, and is found in Natuna Island, the Halmahera Islands and Irian Jaya, Indonesia, Malaysia, Philippines, and Papua New Guinea.")
        self.assertEquals(self.info["geographic_range"]["countries_occurence"],u"Native:Indonesia; Malaysia; Papua New Guinea; Philippines")
        self.assertEquals(self.info["geographic_range"]["FAO_marine_fishing_areas"],u"Native:Pacific \u2013 northwest; Pacific \u2013 western central")
        self.assertEquals(self.info["geographic_range"]["additional_data"],u"")
        self.assertEquals(self.info["geographic_range"]["range_map"],u"http://maps.iucnredlist.org/map.html?id=178809")
        
    def test_if_info_contains_population_information(self):
        self.assertEquals(self.info["population"]["population"],"This species is widespread but uncommon in the Philippines. In Natuna Island and Halmahera Islands, Indonesia this is a rare species that is patchily distributed.")
        self.assertEquals(self.info["population"]["current_population_trend"],"Decreasing")
        self.assertEquals(self.info["population"]["additional_data"],u'? Population severely fragmented:No')
    
    def test_if_info_contains_habitat_and_ecology_information(self):
        self.assertEquals(len(self.info["habitat_and_ecology"]["habitat_and_ecology"]),355)
        self.assertEquals(self.info["habitat_and_ecology"]["systems"],"Terrestrial; Marine")
        self.assertEquals(self.info["habitat_and_ecology"]["generation_length"],"40")
    
    def test_if_info_contains_use_and_trade_information(self):
        self.assertEquals(self.info["use_and_trade"]["use_and_trade"],"This species is harvested for fodder, fuelwood and construction materials.")
    
    def test_if_info_contains_threats_details(self):
        self.assertEquals(len(self.info["threats"]["major_threats"]),2091)
        
    def test_if_info_contains_conservation_action_details(self):
        self.assertEquals(len(self.info["conservation_actions"]["conservation_actions"]),259)
        
    def tearDown(self):
        self.info = None
        self.iucn = None
    
if __name__ == '__main__':
    unittest.main()