import os, sys
import datetime, logging
logging.basicConfig(filename='cg_check.log',level = logging.DEBUG)
sys.path.insert(0,os.path.expanduser('~/'))
from rh_atg_api import rh_atg_api
from box_api import box_api_class
ouput_file = os.path.expanduser(f'~/Desktop/cg_check.csv')
if os.path.exists(ouput_file): os.remove(ouput_file)
rh = rh_atg_api.rh_atg_wrapper()
rh.cg_check()
box = box_api_class.box_api()
t = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
new_path = os.path.expanduser(f'~/Desktop/cg_check_{t}.csv')
os.rename(ouput_file, new_path)
box.upload(new_path,255853055115)
os.remove(new_path)