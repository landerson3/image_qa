import requests, time, datetime

parents = ('cat13570014','cat14210079','cat1481016','cat1544013','cat160039','cat1850055','cat18800001','cat1970012','cat23470031','cat3850072','cat8750009','cat950002','cat13570014','cat14460002','cat1580117','cat160045','cat1970012','cat23480001','cat3870171','cat8750009','cat1600023','cat16550009','cat16550010','cat16570005','cat20033','cat2250146','cat23480004','cat24690009','cat25400088','cat26700014','cat7990005','cat8750009','cat90071','cat1535021','cat1580123','cat160147','cat16760002','cat16760003','cat16760005','cat20300007','cat23480014','cat2620028','cat780015','cat780019','cat8670004','cat8750009','cat16020396','cat16850013','cat16850025','cat23480038','cat23650004','cat2650129','cat27510001','cat27580030','cat27580031','cat3890204','cat8750009','cat1701067','cat20033','cat23490006','cat26600032','cat3850005','cat3880025','cat8750009','cat9000219','cat9780018','cat9780022','cat14950026','cat1535021','cat2250146','cat23480042','cat24690009','cat3510047','cat8750009','cat90071','cat9780018','cat9780022','cat9780030','cat1701013','cat1701019','cat1597020','cat1598016','cat4960002','cat1701024','cat25900016','cat1695139','cat16250001','cat3090004','cat14650097','cat1695091','cat6610131','cat10880022','cat11110001','cat16250029','cat16260007','cat2340002','cat6330111','cat26920009','rhbc_cat467001','rhbc_cat202002')
parent_catid = 'cat950002'
headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}

def image_exist(file):
	if file[:2] == '//':
		url = f"https:{file}&req=exists,json"
		if "?" not in url:
			url = url.replace("&req=exists,json", "?req=exists,json")
	else:
		url = f"https://media.restorationhardware.com/is/image/rhis/{file}?req=exists,json"
	try:
		r = requests.get(url)
	except ConnectionError:
		time.sleep(2)
		return image_exist(file)
	if r == None or r.status_code >200: return False
	else:
		if 'catalogRecord.exists":"1"' in r.text: return True
		else: return False



def get_category_data(catid):
	data = requests.get(f'https://rh.com/rh/api/category/collectiongallery/v1/{catid}', headers = headers).json()
	if data['totalNumRecs']>=1:
		for collx in data['collectionGallery']:
			yield collx
			if collx['id'] == catid: continue ## this avoids infinite loop
			else: yield from get_category_data(collx['id'])


for parent in parents:
	continue
	for collection in get_category_data(parent):
		if 'template' not in collection: continue
		id = collection['id']
		banner = collection['cgBannerImage']
		if banner not in ('',None):
			imagecheck = image_exist(banner)
		else:
			imagecheck = image_exist(id)
		if imagecheck == False:
			pass
			print(collection['displayName'],collection['id'], collection['cgBannerImage'], imagecheck)
print(datetime.datetime.now())