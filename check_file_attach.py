# take an export of images in the standard RT Outsource Export format and check that they are attached to the appropriate prodIDs
# export should be as tab delimited doc


import threading, requests, re, os, sys
sys.path.insert(0,os.path.expanduser('~'))
from gx_api import galaxy_api_class



def get_prod_images(prodid):
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'content-type': "application/json"}

	url = f'https://rh.com/rh/api/product/v1/{prodid}'
	# url = f'https://rh.com/rh/api/product/image/v1/{prodid}'
	try:
		r = requests.get(url, headers = headers)
	except (ConnectionError, requests.exceptions.ConnectionError):
		return get_prod_images(prodid)
	data = r.json()
	if 'alternateImages' not in data.keys(): return []
	images = data['alternateImages']
	return images


def check_prod(wc_name, prod):
	product_images = get_prod_images(prod)
	# check 
	for image in product_images:
		if wc_name in image['imageUrl']:
			with open(os.path.expanduser('~/Desktop/image_attach.csv'),'a') as doc:
				doc.write(f'{prod},{wc_name},True\n')
			return
	with open(os.path.expanduser('~/Desktop/image_attach.csv'),'a') as doc:
				doc.write(f'{prod},{wc_name},False\n')


## add functionality to check if file exists on S7
def s7_file_exists(filename:str) -> bool:
	pass

## add functionality to pull image list from GX
def get_gx_files() -> list:
	'''returns a list of records from galaxy that meet the specified hard-coded params'''
	p = {
		'query':[
			{
			'c_WA_Launch_Date_Earliest' : f'>={date}',
			'wm_Pickup_Source':'*',
			'omit' : 'false'
			},
		]
		}
	gx = galaxy_api_class.gx_api()
	gx.find_records(p)
	pass

## add functionality to check if file is in BCC
def get_atg_file(image_name:str) -> bool|str:
	pass
	## build BCC import for new imagery

## add functionality to upload final to DMC
def upload_to_ftp(file:str) -> None:
	'''take a filepath and upload it to the the Automated Uploads folder in the RH FTP'''
	pass

# add functionality to check prod image order
	# needs to take into account the product department, category, product type, etc. 
	# See https://docs.google.com/spreadsheets/d/12xARfcmb51pIUGCRhALyiRNedCkNKBoiHxPydJM5FYw/edit#gid=626463043
	# correct order as needed and return the csv for upload

# add functionality to build product image attach document


# update to run on a found GX set of files
with open('/Users/landerson2/Downloads/OD_ALTS.txt','r') as file:
	csv = file.readlines()
	headers = csv[0].split('\t')
	for l in csv:
		line = l.split('\t')
		if headers == line: continue
		line_data = {}
		for i,v in enumerate(headers):
			try:
				line_data[v] = line[i]
			except IndexError:
				line_data[v] = ''
		prod,image_name = line_data['ProdID'], line_data['cRetoucher_ ImageName']
		wc_name = re.search(r"prod\d+_E\d+.*",image_name)
		if wc_name:
			wc_name = wc_name.group(0).replace(".tif","")
			# check_prod(wc_name, prod)
			threading.Thread(target = check_prod, args = (wc_name, prod)).start()
			while threading.active_count() > 30: continue
