import os, sys, logging, threading
logging.basicConfig(filename='file_attach.log',level = logging.DEBUG)
sys.path.insert(0,os.path.expanduser('~/'))
from rh_atg_api import rh_atg_api
from box_api import box_api_class
from gx_api import galaxy_api_class

'''
Take a list of prodIDs and check the images on the prod against the images in GX; 
report back on the missing files per prod
'''

KEYWORD_REQUESTS = ['imageUrl','lifestyleImage']

class prod_checker():
	def __init__(self, prods: list|tuple) -> None:
		if type(prods) not in (list, tuple): 
			raise ValueError(f"Expected argument of type List or Tuple but received {type(prods)}")
		self.prod_list = prods
		gx_query_params = {
			'query':[
			]
		}
		atg_image_thread = threading.Thread(target = self._get_atg_images)
		atg_image_thread.start()
		for prod in self.prod_list:
			# get the images from the prod on the site
			# build the GX query
			gx_query_params['query'].extend(
				[
					{
						'cRetoucher_ ImageName': f'*{prod}*',
						'omit': 'false'
					},
					# {
					# 	'ProdID' : prod
					# },
				]
			)
		gx_query_params['query'].append(
			{
				'RetouchStatus' : 'Dropped',
				'omit' : 'true'
			}
		)

		# get the image lists from GX
		gx = galaxy_api_class.gx_api(production = True)
		gx_response = gx.find_records(gx_query_params)
		gx_assets = {}

		if 'response' in gx_response:
			for asset in gx_response['response']['data']:
				asset_data = asset['fieldData']
				p = self._get_prod_id_from_file(asset_data['ImageName'])
				if p not in gx_assets: gx_assets[p] = [asset_data['cRetoucher_ ImageName'],]
				else: gx_assets[p].append(asset_data['cRetoucher_ ImageName'])

		# ensure the other thread is complete
		if atg_image_thread.is_alive(): atg_image_thread.join()
		for prod in self.prod_list:
			if prod not in gx_assets: 
				continue
			if len(gx_assets[prod]) > len(self.atg_image_list[prod]):
				print(prod)
	
	def _get_prod_id_from_file(self, file) -> str | None:
		for prod in self.prod_list:
			if prod in file:
				return prod
	
	def _get_atg_images(self):
		_rh = rh_atg_api.rh_atg_wrapper()
		self.atg_image_list = {}
		for prod in self.prod_list:
			info = _rh.get_product_info(prod)
			images = info['alternateImages']
			res = []
			for i in images:
				i['imageUrl'] = i['imageUrl'].replace('//media.restorationhardware.com/is/image/rhis/','')
			res = [i for i in images if i['lifestyleImage'] == False]
			# images = [i.replace('//media.restorationhardware.com/is/image/rhis/','') for i in images]
			self.atg_image_list[prod] = res
			

rh = rh_atg_api.rh_atg_wrapper()
prods = rh.get_category_products('cat19210007')
prods = [i['id'] for i in prods]
# prods = ('prod29560802','prod22350071','prod18940137','prod18940131','prod28311052','prod12440076','prod12440079','prod24920050','prod13100121','prod13100120')
g = prod_checker(prods)