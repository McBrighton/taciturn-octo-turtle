from urllib import request
from lxml import html
import io
##import pickle
##
##def backup(fileName):
##    pickle.dump(globals(), open(fileName,'w'), pickle.HIGHEST_PROTOCOL)
##
##def restore(fileName):
##    globals().update(pickle.load(open(fileName,"rb")))

# предложения грузов:
# http://della.ua/search/a204bd204eflolh0ilk0m1.html
# предложения транспорта:
# http://della.ua/search/a204bd204eflolh0ilk1m1.html
##req = request.Request('http://della.ua/search/a204bd204eflolh0ilk0m1.html')
##with request.urlopen(req) as response:
##    the_page = response.read()
##
##d_page = html.fromstring(html=the_page, base_url=response.geturl())
##d_page.make_links_absolute()

### test of selecting by class
##requests = d_page.find_class("request_level_ms")
##html.tostring(requests[0], pretty_print = True, encoding = 'unicode')

# test work with saved page of Della
tree = html.parse("/mnt/Work/MyDocs/Dropbox/dev/DELLA_example.html")
f_page = tree.getroot()

## example2 has evoked form
# tree = html.parse("/mnt/Work/MyDocs/Dropbox/dev/DELLA_example2.html")
# f_page = tree.getroot()
# print(html.tostring(f_page.get_element_by_id('logForm'), pretty_print = True, encoding = 'unicode'))

# test of selecting by class ("-": includes rows with ads)
requests = f_page.find_class("request_level_ms")
print(html.tostring(requests[0], pretty_print = True, encoding = 'unicode'))

# selection of rows with requests
a = f_page.xpath('//tbody[@id="request_list_main_tbl"]/tr[@id]')

b = []
for n, el in enumerate(a):
	if el.xpath('.//img[@alt="*"]'):
		b += el.find_class("request_level_ms")
		print ("selected %d row" % (n+1))

# open file in mode 'w' - write with truncating at first
f = open("/mnt/Work/MyDocs/Dropbox/dev/elem0.html",
         mode = "w", encoding = "UTF-8")

# make some quick header (taken from Della page)
print('<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">', file = f)
print('<meta http-equiv="X-UA-Compatible" content="IE=edge">', file = f)
print('<title>Snezhynka selections</title>', file = f)
print('<meta http-equiv="Content-Language" content="ru, uk, ru-UA, uk-UA, ua">', file = f)
print('</head>', file = f)
print('', file = f)

for el in b:
    print(html.tostring(el, pretty_print = True, encoding = 'unicode'), file = f)

f.close()

# Перечитывать страницу, дописывать данные
# (файл нужно открывать в другом режиме)
# сверять айди, чтобы не дописывать те же заявки
# приблизительно так:
# b[0].get('request_id')
