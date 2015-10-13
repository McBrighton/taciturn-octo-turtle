from urllib import request
from lxml import html
import io
import time

# constants

# предложения грузов: http://della.ua/search/a204bd204eflolh0ilk0m1.html
# предложения транспорта: http://della.ua/search/a204bd204eflolh0ilk1m1.html

# common:
della_url = "http://della.ua/search/a204bd204eflolh0ilk0m1.html"
req_interval = 5.0  # 5 seconds

# dev variants
#st_local_Della = "/mnt/Work/MyDocs/Dropbox/dev/DELLA_example.html"
st_outfile = "/mnt/Work/MyDocs/Dropbox/dev/elem0.html"

# server variants
##st_local_Della = "/media/sf_Dropbox/dev/DELLA_example.html"
##st_outfile = "/var/www/html/smartlog/elem0.html"

req_id = {}

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
                    print ("selected %d row" % (n+1))

    # return list of selected <td> html elements
    return b

def prepare_file(outfile):
    """ opens html file for writing.
        Either creates/truncates file,
        or opens it for appending to end
    """
    q = input("Use blank page? (Y/n)")
    if q in ("Y", "y"):
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
        print('<tbody>', file = f)
    else: # append mode
        f = open(outfile,
                 mode = "a", encoding = "UTF-8")
    return f

def close_file(f):
    """ adds closing tags to html file and closes it """
    print('</tbody>', file = f)
    print('</body>', file = f)
    print('</html>', file = f)
    f.close()


def add_data_to_page(page_file, b_data):
    for el in reversed(b_data):
        print ('<tr>', file = page_file)
        print(html.tostring(el, pretty_print = True, encoding = 'unicode'), file = page_file)
        print ('</tr>', file = page_file)

# limit cycle for testing
countdown = 12

f = prepare_file(st_outfile)

starttime = time.time()
while True:
    b = grab_della_snow(della_url)
    add_data_to_page(f, b)
    time.sleep(req_interval - ((time.time() - starttime) % req_interval))

    if countdown == 0:
        break
    countdown -= 1

close_file(f)


##import signal
##def tick_print(delay=0, interval=0):
##    print("tick with delay = %s and interval=%s" % (delay, interval))
##signal.setitimer(signal.ITIMER_REAL, 1, 5)
##signal.signal(signal.SIGALRM, tick_print)
##signal.alarm(0)

# Перечитывать страницу, дописывать данные
# (файл нужно открывать в другом режиме)
# сверять айди, чтобы не дописывать те же заявки
# приблизительно так:
# b[0].get('request_id')
