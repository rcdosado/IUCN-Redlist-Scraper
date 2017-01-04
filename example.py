from iucn import IUCN_Redlist
import argparse

def convert_specie_to_filename(specie):
    converted_as_filename = specie.replace(' ','_')+'.json'
    return converted_as_filename

def save_to_file(info_list,specie):
    import io,json
    json_format = json.dumps(info_list)
    filename = convert_specie_to_filename(specie)
    
    with io.open(filename, 'w', encoding='utf-8') as f:
        ret=f.write(unicode(json.dumps(info_list,indent=4, ensure_ascii=False)))
    return  ret

def get_IUCN_detail(specie):
    _iucn = IUCN_Redlist()
    details = None 

    try:
        sresult = _iucn.search(specie)
        details = sresult.get_details()
    except(ValueError, TypeError):
        pass
    return details


def load_species(fn):
    contents = None
    f = open(fn, "r")
    contents = f.readlines();
    f.close()
    return contents

def random_delay():
    sleep(randint(1,5))
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape Species Information in IUCN RedList")
    parser.add_argument('filename', help='')
    
    args = parser.parse_args()
    
    species_list = load_species(args.filename)
    if species_list is None:
        raise Exception("[-] Empty File")
    
    slist = [specie.strip() for specie in species_list]
    
    for specie in slist:
        random_delay()
        detail = get_IUCN_detail(specie)
        
        if detail is None:
            print("[-] Cannot find that specie")
            continue        
        
        save_to_file(detail,specie)
        print("[+] "+ specie +" saved")
    
