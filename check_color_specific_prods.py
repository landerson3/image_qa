import os, sys, threading
sys.path.insert(0,os.path.expanduser('~/'))
from rh_atg_api import rh_atg_api
rh = rh_atg_api.rh_atg_wrapper()

# prods = ('prod100265','prod10120144','prod10120151','prod10120154','prod10290001','prod10290002','prod10290004','prod10290005','prod10290006','prod10290007','prod10290008','prod10290009','prod10290010','prod11960205','prod12140060','prod12140061','prod12140062','prod12140063','prod12140064','prod12140065','prod12140066','prod12140067','prod12140068','prod12140069','prod12140070','prod12140071','prod12140072','prod12140073','prod12140074','prod12140075','prod12140076','prod12140077','prod12140078','prod12140095','prod12140096','prod12140097','prod12140098','prod12140099','prod12140100','prod12140101','prod12140102','prod12140103','prod12140104','prod12140105','prod12140106','prod12140107','prod12140108','prod12140109','prod12140110','prod12230003','prod14320178','prod14970293','prod14970301','prod14970304','prod14970315','prod14970316','prod14970317','prod14970321','prod14970322','prod14970323','prod14970324','prod14970393','prod14970394','prod14970396','prod14970397','prod14970399','prod14970400','prod14970403','prod14970404','prod14970405','prod14970406','prod14970407','prod14970408','prod14970409','prod14970410','prod14970411','prod14970413','prod14970414','prod14970415','prod14970416','prod14970417','prod14970418','prod14970419','prod15010192','prod15900022','prod1861123','prod1861127','prod1861130','prod1861142','prod1861145','prod1861146','prod1861147','prod1861148','prod1871112','prod1871114','prod1871206','prod1871208','prod20340034','prod20340035','prod20340036','prod20340037','prod20340038','prod20340039','prod20340040','prod20340041','prod20340042','prod20340043','prod20340044','prod20340045','prod20340046','prod20340047','prod20340048','prod20340049','prod20340067','prod20340068','prod20340069','prod20340070','prod20340071','prod20340072','prod20340073','prod20340074','prod20340075','prod20340076','prod20340077','prod20340078','prod20340079','prod20340080','prod20340081','prod20340082','prod2090061','prod2110719','prod2110720','prod2110722','prod2110723','prod2110814','prod2110815','prod2110816','prod2110818','prod2110819','prod2110820','prod2110821','prod2110822','prod2111378','prod2111380','prod2111415','prod2111418','prod2111419','prod2111435','prod2111436','prod2120051','prod2170168','prod2170170','prod2170212','prod2170220','prod2170226','prod2250012','prod2250013','prod2380051','prod2380052','prod2380053','prod2380054','prod2380055','prod2380073','prod2380075','prod2380132','prod2380133','prod2380134','prod2380135','prod2380136','prod2380137','prod2380138','prod2380163','prod2380165','prod2380195','prod2380196','prod2380197','prod2380198','prod2380199','prod2380200','prod2380201','prod2380226','prod2380228','prod24400553','prod24400554','prod24400555','prod24400556','prod24400557','prod24400558','prod24400559','prod24400560','prod24400561','prod24400562','prod24400563','prod24400564','prod24400565','prod24400566','prod24400567','prod24400583','prod24400584','prod24400585','prod24400586','prod24400587','prod24400588','prod24400589','prod24400590','prod24400591','prod24400592','prod24400593','prod24400594','prod24400595','prod24400596','prod24400597','prod24400613','prod24400614','prod24400615','prod24400616','prod24400617','prod24400618','prod24400619','prod24400620','prod24400621','prod24400622','prod24400625','prod24400626','prod24400627','prod24400650','prod24400651','prod24400652','prod24400655','prod24400656','prod24400657','prod24560968','prod24560969','prod24560972','prod24560973','prod24560974','prod24560975','prod24560976','prod24560977','prod24560978','prod24560979','prod24560980','prod24560981','prod24560997','prod24560998','prod24560999','prod2460616','prod2460618','prod2460620','prod2511147','prod2511148','prod25340074','prod25340075','prod25340076','prod25340077','prod25350032','prod25350033','prod25350034','prod25350035','prod60117','prod60119','prod6490082','prod6490083','prod6490086','prod6490087','prod6490218','prod6490220','prod7550782','prod7550783','prod7550785','prod7550786','prod7550787','prod7550788','prod7550789','prod7550790','prod7550823','prod7550824','prod7550826','prod7550827','prod7550828','prod7550829','prod7550830','prod7550831','prod7550839','prod7550842','prod7550845','prod7550846','prod7550847','prod7550849','prod7550851','prod7551808','prod7551817','prod7551818','prod7551819','prod7551820','prod7551821','prod7551822','prod7551823','prod7551824','prod7551825','prod7551829','prod7551831','prod7551833','prod7551835','prod7551839','prod7560041','prod7590785','prod7590798','prod7590803','prod7640418','prod7640419','prod7640447','prod7870154','prod7870160','prod7870165','prod80413','prod80419','prod80660','prod80912','prod80913','prod8760146','prod8760147','prod8760164','prod8760165','prod8780235','prod8780246','prod8780318','prod8780320','prod8790516','prod9340077','prod9340078','prod9340080','prod9340082','prod9340117','prod9340119','prod9350062','prod9690047','prod9690049','prod9820187','prod9820188','prod9820189','prod9820190','prod9820191','prod9820192','prod9900022','prod9900023','prod9900024','prod9910054','prod9910055')

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
