import requests, time, os, itertools

LEFT_NAVS = ('cat27290161','cat23470031','cat1481016','cat950002','cat14210079','cat1970012','cat13570014','cat1850055','cat1544013','cat18800001','cat160039','cat3850072','cat8750009','cat27370240','cat23480001','cat3870171','cat160045','cat14460002','cat1970012','cat13570014','cat1580117','cat8750011','cat27370241','cat23480004','cat26700014','cat16550009','cat16550010','cat16570005','cat25400088','cat7990005','cat90071','cat24690009','cat2250146','cat20033','cat1600023','cat8750013','cat28640064','cat23480014','cat16760002','cat16760003','cat20300007','cat16760005','cat780019','cat2620028','cat1535021','cat780015','cat160147','cat1580123','cat8750015','cat27160061','cat27370246','cat23490028','cat1695093','cat6330023','cat1581019','cat1657018','cat10680009','cat200032','cat490074','cat3870211','cat26020012','cat6760021','cat11690025','cat25600044','cat16590009','cat28650025','cat27370242','cat23480029','cat21330004','cat1701013','cat1701019','cat1597020','cat1598016','cat4960002','cat1701024','cat3850073','cat8750017','cat30100097','cat27370243','cat23480042','cat30100096','cat90071','cat24690009','cat2250146','cat29580407','cat28700015','cat8750021','cat27370244','cat23480038','cat16850013','cat23650004','cat16020396','cat28060004','cat27580030','cat16850025','cat27580031','cat27510001','cat3890204','cat2650129','cat8750023','cat27290169','cat23490006','cat20033','cat26600032','cat1701067','cat3880025','cat3850005','cat9780030','cat9780018','cat9780022','cat29270005','cat9000219','cat8750025')
headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}

class rh_atg_wrapper():
	def __init__(self, target = 'production') -> None:
		if target == 'production':
			self.basePath = "https://www.rh.com/rh/api"
		elif target in ('a','b','c','d'):
			self.basePath = f'https://int{target}.rhnonprod.com/rh/api'
			if requests.get(self.basePath).status_code >= 300:
				raise ConnectionError

	def image_exist(self, file):
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
			return self.image_exist(file)
		if r == None or r.status_code >200: return False
		else:
			if 'catalogRecord.exists":"1"' in r.text: return True
			else: return False

	def option_permutations(self, options):
		## create a grouping of all possible options
		avail_options = []
		for optiontype in options:
			opt = []
			for avopt in optiontype['availableOptions']:
				opt.append(avopt['id'])
			avail_options.append(opt)
		all_options = list(itertools.product(*avail_options))
		return all_options

	def get_product_options(self, productID) -> list:
		url = f"{self.basePath}/product/options/v1/{productID}"
		data = requests.get(url, headers= headers)
		if data.status_code == 200:
			data = data.json()
			return data

	def get_category_data(self, catid):
		data = requests.get(f'https://rh.com/rh/api/category/collectiongallery/v1/{catid}', headers = headers).json()
		if data['totalNumRecs']>=1:
			for collx in data['collectionGallery']:
				yield collx
				if collx['id'] == catid: continue ## this avoids infinite loop
				else: yield from self.get_category_data(collx['id'])

	def get_product_skus(self, productId):
		# to do
		skus = []
		url = f"{self.basePath}/internal/product/skus/v1/{productId}"
		res = requests.get(url, headers=headers)
		if res.status_code == 200:
			res = res.json()
		
	def get_product_info(self, id: int|str):
		url = f"{self.basePath}/product/v1/{id}"
		data = requests.get(url, headers=headers)
		if data.status_code == 200:
			return data.json()

	def get_product_images(self, productID:str, options:list) -> list:
		'''
		take a product id and option list of options and return a list of all product images
		'''
		url = f"{self.basePath}/product/image/v1/{productID}"
		opts = ",".join(options)
		url = f"{url}?optionIds={opts}"
		res = requests.get(url, headers = headers)
		if res.status_code == 200:
			return res.json()['imageurl']

	def check_product_image(self, productID:str) -> list:
		prod_data = self.get_product_info(productID)
		res = []
		if prod_data != None:
			for image in prod_data['alternateImages']:
				image['imageExists'] = self.image_exist(image['imageUrl'])
				res.append(
					image
				)
	def check_category_product_images(self, category_id:str) -> enumerate:
		prods = self.get_category_products(category_id)
		for prod in prods:
			options = self.get_product_options(prod['id'])
			opt_permutes = self.option_permutations(options)
			for configuration in opt_permutes:
				yield (prod['id'],
	   				self.image_exist(self.get_product_images(prod['id'],configuration)),
					configuration
					) 

	def get_category_products(self, category_id: str) -> list:
		# take a category_ID and return all underlying products		
		result = []
		url = f"{self.basePath}/category/productgallery/v1/{category_id}"
		res = requests.get(url,headers=headers)
		if res.status_code == 200:
			for item in res.json()['productGallery']:
				if 'type' in item and item['type'] == 'product':
					result.append(item)
		return result
	
	def product_image_check(self, parent_collection_id: str|list = LEFT_NAVS) -> None:
		if type(parent_collection_id) in (list,tuple):
			for id in parent_collection_id:
				self.product_image_check(id)
				return
		else:
			for i in self.check_category_product_images(parent_collection_id):
				with open(os.path.expanduser("~/Desktop/product_image_check.csv"),"a") as csv:
					line = f'''{i[0]},{i[1]},"{",".join(i[2])}"\n'''
					csv.write(line)


	def cg_check(self, parent_collection_id: str|int|list|tuple = LEFT_NAVS) -> None:
		'''
		function should return a path to the CSV containing he report of catIDs 
		and the existence (or non-existence) of all 'collection' cgs under 
		the provided parent_collection_id
		'''
		if type(parent_collection_id) in (list, tuple):
			for col in parent_collection_id:
				self.cg_check(col)
		for collection in self.get_category_data(parent_collection_id):
			if 'template' not in collection: continue
			if 'cgBannerTemplate' not in collection: continue
			if collection['active'] == False: continue
			id = collection['id']
			banner = collection['cgBannerImage']
			if banner not in ('',None):
				imagecheck = self.image_exist(banner)
			else:
				imagecheck = self.image_exist(id)
			with open(os.path.expanduser('~/Desktop/cg_check.csv'),'a') as cg_csv:
				banner = collection['cgBannerImage'].replace(",","\\,")
				cg_csv.write(f'''{collection['id']},{collection['type']},{collection['displayName']},"{banner}",{imagecheck}\n''')



rh = rh_atg_wrapper()
rh.cg_check()
rh.product_image_check()


# prods = rh.get_category_products(LEFT_NAVS[0])
# for i,nav in enumerate(LEFT_NAVS):
# 	if i ==0: continue
# 	print(nav)
# 	for i in rh.check_category_product_images(nav):
# 		if i[1] == False:
# 			print(i)



# check all images for product (to include colorization)
# productID = 'prod31740058'
# options = rh.get_product_options(productID)
# opt_permutes = rh.option_permutations(options)
# for o in opt_permutes:
# 	print(rh.image_exist(rh.get_product_images(productID,o)))
