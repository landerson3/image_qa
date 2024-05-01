# cat1537037
import os, sys
import datetime
sys.path.insert(0,os.path.expanduser('~/'))
from rh_atg_api import rh_atg_api
from box_api import box_api_class
output_path = os.path.expanduser(f'~/Desktop/product_image_check.csv')
if os.path.exists(output_path): os.remove(output_path)
rh = rh_atg_api.rh_atg_wrapper(target = 'b')
rh.product_image_check('cat1537037')
# box = box_api_class.box_api()
# t = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
# new_path = os.path.expanduser(f'~/Desktop/product_image_check_{t}.csv')
# os.rename(output_path, new_path)
# box.upload(new_path,255853055115)
# os.remove(new_path)