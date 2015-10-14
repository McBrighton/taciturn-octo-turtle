from urllib import request
from lxml import html
import io
import time
import os
from os.path import exists

# constants

# предложения грузов: http://della.ua/search/a204bd204eflolh0ilk0m1.html
# предложения транспорта: http://della.ua/search/a204bd204eflolh0ilk1m1.html

# common:
della_url = "http://della.ua/search/a204bd204eflolh0ilk0m1.html"
req_interval = 5.0  # 5 seconds
st_outfile = "elem0.html"
bk_outfile1 = "elem1.html"
bk_outfile2 = "elem2.html"

# dev variants
#st_local_Della = "/mnt/Work/MyDocs/Dropbox/dev/DELLA_example.html"
site_path = "/mnt/Work/MyDocs/Dropbox/dev"

# server variants
##st_local_Della = "/media/sf_Dropbox/dev/DELLA_example.html"
##site_path = "/var/www/html/smartlog"

req_dict = {}

def grab_della_snow(della_url):
    """ extracts data from URL (1st page about Ukraine of Della) """
    req = request.Request(della_url)
    with request.urlopen(req) as response:
        the_page = response.read()

    d_page = html.fromstring(html=the_page, base_url=response.geturl())
    d_page.make_links_absolute()

    ### test of selecting by class
    ##requests = d_page.find_class("request_level_ms")
    ##html.tostring(requests[0], pretty_print = True, encoding = 'unicode')

    # test work with saved page of Della
    ##tree = html.parse(st_local_Della)
    ##f_page = tree.getroot()

    ## example2 has evoked form
    # tree = html.parse("/mnt/Work/MyDocs/Dropbox/dev/DELLA_example2.html")
    # f_page = tree.getroot()
    # print(html.tostring(f_page.get_element_by_id('logForm'), pretty_print = True, encoding = 'unicode'))

    # selection of rows with requests
    a = d_page.xpath('//tbody[@id="request_list_main_tbl"]/tr[@id]')

    b = []
    for n, el in enumerate(a):
            # search for star char as <alt> to "snezhinka" <img>
            if el.xpath('.//img[@alt="*"]'):
                    b.extend(el.find_class("request_level_ms"))
                    # for testing purposes
                    # print ("selected %d row" % (n+1))

    # return list of selected <td> html elements
    return b


def prepare_file(outfile):
    """ opens html file for writing.
        Either creates/truncates file,
        or opens it for appending to end
    """
    # open file in mode 'w' - write with truncating at first
    f = open(outfile,
             mode = "w", encoding = "UTF-8")
    # make some quick header (taken from Della page)
    print('</html>', file = f)
    print('<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">', file = f)
    print('<meta http-equiv="X-UA-Compatible" content="IE=edge">', file = f)
    print('<title>Snezhynka selections</title>', file = f)
    print('<meta http-equiv="Content-Language" content="ru, uk, ru-UA, uk-UA, ua">', file = f)
    print('</head>', file = f)
    print('<body>', file = f)
    print('<table class="" width="100%">', file = f)
    return f


def close_file(f):
    """ adds closing tags to html file and closes it """
    print('</table>', file = f)
    print('</body>', file = f)
    print('</html>', file = f)
    f.close()


def add_data_to_page(page_file, b_data):
    for el in reversed(b_data):
        print ('<tr>', file = page_file)
        print(html.tostring(el, pretty_print = True, encoding = 'unicode'), file = page_file)
        print ('</tr>', file = page_file)
        page_file.flush() # to make available for browser


def filter_data(b_data):
    """ filter data from duplicates """
    global req_dict
    filtered_b = []
    for el in b_data:
        req_id = int(el.get("request_id"))
        dateup = int(el.xpath("parent::*")[0].get("dateup"))
        if req_id not in req_dict:
            # new request
            req_dict[req_id] = dateup
            filtered_b.extend(el)
        elif dateup != req_dict[req_id]:
            # updated request
            req_dict[req_id] = dateup
            filtered_b.extend(el)

    return filtered_b


# countdown = 3 # limit cycle for testing

cur_dir = os.getcwd()
os.chdir(site_path)

f = prepare_file(st_outfile)
rotation_ready = True
starttime = time.time()

while True:
    # if countdown == 0:
    #    break
    b = grab_della_snow(della_url)
    b = filter_data(b)
    add_data_to_page(f, b)
    if time.localtime().tm_min in [0, 30]:
        if rotation_ready:
            close_file(f)
            if exists(bk_outfile1):
                os.replace(bk_outfile1, bk_outfile2)
            os.replace(st_outfile, bk_outfile1)
            rotation_ready = False
            f = prepare_file(st_outfile)
            req_dict = {}
    else:
        rotation_ready = True
    time.sleep(req_interval - ((time.time() - starttime) % req_interval))

    # countdown -= 1


close_file(f)
os.chdir(cur_dir)

##import signal
##def tick_print(delay=0, interval=0):
##    print("tick with delay = %s and interval=%s" % (delay, interval))
##signal.setitimer(signal.ITIMER_REAL, 1, 5)
##signal.signal(signal.SIGALRM, tick_print)
##signal.alarm(0)
