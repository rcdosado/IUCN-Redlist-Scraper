import re
import socket

# given a string with numeric characters, extract and put in a list
def get_numbers_from_string_with_spaces(input_string):
    return [int(s) for s in input_string.split() if s.isdigit()]    

def get_numbers_from_html(inputstr):
    results = re.findall(r'\d+',inputstr)
    return results    


def match_class(target):                                                        
    def do_match(tag):                                                          
        classes = tag.get('class', [])                                          
        return all(c in classes for c in target)                                
    return do_match


# http://stackoverflow.com/questions/20913411/test-if-an-internet-connection-is-present-in-python
REMOTE_SERVER = "www.google.com"
def online ():
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)     
    return regex.match(url)

