import requests, time, os, itertools, re, threading
import logging
logging.basicConfig(filename="image_qa.log", level = logging.DEBUG)

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
		self.invalid_image =  requests.get('https://media.restorationhardware.com/is/image/rhis/notarealimage__?wid=100').content

	def image_exist(self, file):
		if type(file) == dict:
			if 'imageUrl' in file:
				file = file['imageUrl']

		if file[:2] == '//':
			url = f"https:{file}&req=exists,json"
			if "?" not in url:
				url = url.replace("&req=exists,json", "?req=exists,json")
		else:
			url = f"https://media.restorationhardware.com/is/image/rhis/{file}?req=exists,json"
		
		if "rhir" in url:
			url = re.sub(r'\?wid=\d+','',url)
			url = re.sub('&req=exists,json','',url)
			if '?' in url:
				url = url + '&wid=100'	
			else:
				url = url + '?wid=100'
			try:
				im_content = requests.get(url).content
			except:
				time.sleep(.1)
				im_content = requests.get(url).content
			if  im_content == self.invalid_image:
				return False
			else:
				return True
		try:
			r = requests.get(url)
		except:
			time.sleep(2)
			return self.image_exist(file)
		if r == None or r.status_code>200: return False
		else:
			if 'catalogRecord.exists":"1"' in r.text: return True
			else: return False

	def get_product_options(self, productID) -> list:
		url = f"{self.basePath}/product/swatch/v1/{productID}"
		data = requests.get(url, headers= headers)
		if data.status_code == 200:
			option_groups = []
			data = data.json()
			for swatch_group in data['swatchData']['swatch_groups']:
				for item in (swatch_group['stockedSwatches'],swatch_group['customSwatches'],swatch_group['customFabricSwatch']):
					if item is None: continue
					for swatch in item:
						opt = []
						for option in swatch['options']:
							opt.append(option['id'])
						option_groups.append(tuple(opt))
			return option_groups

	def get_category_data(self, catid):
		data = requests.get(f'https://rh.com/rh/api/category/collectiongallery/v1/{catid}', headers = headers).json()
		if 'totalNumRecs' not in data:
			yield None
		elif data['totalNumRecs']>=1:
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

	def get_product_images(self, productID:str, options:list|tuple) -> list:
		'''
		take a product id and option list of options and return a list of all product images
		'''
		url = f"{self.basePath}/product/image/v1/{productID}"
		opts = ",".join(options)
		url = f"{url}?optionIds={opts}"
		try:
			res = requests.get(url, headers = headers)
		except:
			return self.get_product_images(productID, options)
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
		return res

	def check_category_product_images(self, category_id:str):
		prods = self.get_category_products(category_id)
		for prod in prods:
			alt_images = self.check_product_image(prod['id'])
			for image in alt_images:
				yield (prod['id'],('unconfigured',),image['imageUrl'], image['imageExists'])
			if self.get_product_info(prod['id'])['colorizeInfo']['colorizable'] == False:
				continue
			options = self.get_product_options(prod['id'])
			# opt_permutes = self.option_permutations(options)
			for configuration in options:
				image = self.get_product_images(prod['id'],configuration)
				yield (prod['id'],
		   			configuration,
		   			image,
	   				self.image_exist(image)
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
	
	def product_image_check(self, parent_collection_id: str|list=LEFT_NAVS, is_child = False) -> None:
		## get all of the product IDs, then get all of the option permutes, then get the images w/ threading
		if not hasattr(self, 'products'):
			self.products = [] # set a container for the total list of products
		if type(parent_collection_id) in (list,tuple):
			for id in parent_collection_id:
				self.product_image_check(id, is_child=True)
		else:
			# get a list of all of the product ids;
			# then make a list of all of the options; remove dupes; 
			for i in self.get_category_products(parent_collection_id):
				id = i['id']
				## how can I leverage this return down further to populate static imagery?
				static_images = [image['imageUrl'] for image in i['altImages']]
				if id in self.products: continue
				self.products.append(
					{
						'id':id,
						'images': static_images
					}
				)
		if not is_child:
			# get the options for the products
			for prod in self.products:
				# while threading.active_count() > 5: continue
				# threading.Thread(target = self._thread_prod_image_check, args = (prod,parent_collection_id)).start()
				self._thread_prod_image_check(prod, colx_for_write=parent_collection_id)

	def _thread_prod_image_check(self,prod, colx_for_write = ''):
		options = self.get_product_options(prod['id'])
		prod_threads = []
		if 'images' not in prod:
			prod['images'] = []
		for option in options:
			prod_threads.append(
				threading.Thread(target = self._populate_product_option_images, args = (prod,option))
				)
		for thd in prod_threads:
			thd.start()	
		for thd in prod_threads:
			thd.join()
		prod_threads = []
		for image in prod['images']:
			while threading.active_count() > 100: continue
			prod_threads.append(
				threading.Thread(target = self.write_image_data, args = (prod,image, colx_for_write)).start()
			)
		for thd in prod_threads: 
			if thd == None: continue
			thd.join()

	def _populate_product_option_images(self,prod:dict,option:list|tuple):
		# allow for threading and populating of product images via options
		# takes a dict and appends the 
		if 'image_options' not in prod:
			prod['image_options'] = {}
		prod['images'].append(self.get_product_images(prod['id'],option))
		if option in ((),[],''):
			option = 'unconfigured'
		prod['image_options'][prod['images'][-1]]=option
		

	def write_image_data(self, prod, image, collection = ''):
		with open(os.path.expanduser(f"~/Desktop/product_image_check_{collection}.csv"),"a") as csv:
			_id = prod['id']
			if type(image) == dict:
				_image = image['imageUrl']
			else:
				_image = image
			if 'rhir' in _image:
				pass
			if 'image_options' in prod:
				if _image in prod['image_options']:
					option = prod['image_options'][_image]
			if 'option' not in locals():
				option = 'unconfigured'
			_exists = self.image_exist(image)
			line = f'''{_id},"{_image}",{_exists},"{option}"'''
			csv.write(line+'\n')

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
			if collection == None: continue
			if 'template' not in collection: continue
			if 'cgBannerTemplate' not in collection: continue
			if collection['active'] == False: continue
			if 'collection' in collection and not collection['collection']:
				continue
			if collection['linkType'] == 'anchor':
				continue
			id = collection['id']
			banner = collection['cgBannerImage']
			if banner not in ('',None):
				imagecheck = self.image_exist(banner)
			else:
				imagecheck = self.image_exist(id)
			if not imagecheck:
				with open(os.path.expanduser(f'~/Desktop/cg_check.csv'),'a') as cg_csv:
					banner = collection['cgBannerImage'].replace(",","\\,")
					cg_csv.write(f'''{collection['id']},{collection['type']},{collection['displayName']},"{banner}",{imagecheck}\n''')

rh = rh_atg_wrapper()
# rh.product_image_check()
rh.cg_check()