import os, sys, threading
sys.path.insert(0,os.path.expanduser('~/'))
from rh_atg_api import rh_atg_api
rh = rh_atg_api.rh_atg_wrapper()

def main():
	for _prod in prods:
		prod = {
			'id':_prod,
			'options':rh.get_product_options(_prod)
		}
		# threading.Thread(target= rh._thread_prod_image_check, args =(prod,'') ).start()
		
		rh._thread_prod_image_check(prod,'')
	for thd in threading.enumerate():
		if thd != threading.main_thread():
			thd.join()

if len(sys.argv) > 1: 
	prods = sys.argv[1].split(',')
	print(prods)
	main()