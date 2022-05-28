from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin

# https://www.anekdot.ru/search/?query=%D0%B6%D0%BE%D0%BF%D0%B0&ch%5Bj%5D=on&mode=any&xcnt=20&maxlen=&order=0
#url = 'https://anekdoty.ru'
url = 'https://www.anekdot.ru/'

tag = 'form'
def get_field():
	session = HTMLSession()
	response = session.get(url)
	soup = BeautifulSoup(response.text, 'lxml') #"html.parser"
	return soup.find(tag)

def get_form_detail(form):
	details = {}
	print("form", form)
	action = form.attrs.get('action').lower()
	method = form.attrs.get('method', 'get').lower()
	i = form.find('input')
	inputs = {"type": i.attrs.get('type', 'text'), 
			"name": i.attrs.get('name'), "value": i.attrs.get('value', '') }
	details['action'] = action
	details['method'] = method
	details['inputs'] = inputs
	return details

detail = get_form_detail(get_field())
print("detail\n"*5, detail)


data = {}
word = input('Слово или фраза: ')
data[detail['inputs']['name']] = word
print(detail['inputs']['name'], detail['inputs']['type'])

url = urljoin(url, detail["action"])


def next_page(num, url=url):
	url = url +'page/%s' % num
	if detail['method'] == 'post':
		res = session.post(url, data=data)
	elif detail['method'] == 'get':
		res = session.get(url, params=data)
	bites = scrap(res)
	return bites

def scrap(res):	
	soup = BeautifulSoup(res.content,'lxml' ) #"html.parser"
	bites = soup.find_all('div', class_ = "holder")
	total = soup.find('div', class_ = 'total')
	print('TOTAL %s' % (int(total.text) - len(bites)*count)) if total else print('TOTAL - 0')
	return bites


def printer(data):
	for s in data:
		yield s.text
#print('Всего %s анекдотов' % len(search))
nexter = printer(next_page(1))
count = 1
while True:
	a = input('0 - закончить: ')
	if a > '0':
		try: 
			print(next(nexter))
		except(StopIteration):
			print('Это все для этой страницы')
			count+=1
			nexter = printer(next_page(count))
			continue
	else:
		break
