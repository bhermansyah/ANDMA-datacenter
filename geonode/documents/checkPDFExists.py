import os,sys
import csv
import glob

os.environ.setdefault("DJANGO_SETTINGS_MODULE","geonode.settings")

from geonode.base.models import Region
from geonode.documents.models import Document
import geonode.documents.models
import geonode.documents.views
import logging

path_source = '/home/uploader/161213/'
path_dest = '/home/ubuntu/DRR-datacenter/geonode/uploaded/96_Geonode/'
fin_up_path = '96_Geonode/'
logger = logging.getLogger('uploadpdf')

f_IN = open(sys.argv[1], 'r+U')
f_OUT= open(sys.argv[2], 'wt')
first = True
try:
	reader = csv.reader(f_IN)
	writer = csv.writer(f_OUT)
	remaining = list(reader)
	for idx, row in enumerate(reader):
		if first:
		   first = False
		else :

			if os.path.isfile(os.path.normpath(path_source+row[10]+'/'+row[0])):
				print os.path.normpath(path_source+row[10]+'/'+row[0])
				os.rename((os.path.normpath(path_source+row[10]+'/'+row[0])), (os.path.normpath(path_dest+row[10]+'/'+row[0])))
				kwargs = {
					'doc_file':os.path.normpath(fin_up_path+row[10]+'/'+row[0]),
					'title':row[1],
					'owner_id':1,
					'papersize':row[8],
					'datasource':row[2],
					'subtitle':row[12]
				}
				newdata = Document.objects.filter(title=row[18])
				if newdata:
					newdata.update(**kwargs)
				else:
					newdata = Document(**kwargs)
				newdata.category_id = row[5]
				newdata.date = row[9]
				newdata.abstract = row[14]
				try:
					newdata.save()
					# tempKeyword = None, row[7].split("-")
					# for xx in tempKeyword :
					# 	if xx!='':
					# 		newdata.keywords.add(xx)
					valid_keywords = filter(None, row[7].split("-"))
					newdata.keywords.add(*valid_keywords)
					row[16]=newdata.id
					loc = Region.objects.get(pk=row[4])
					newdata.regions.add(loc)
					del remaining[idx]
				except Exception as e:
					msg = "{0} error...!, {1}".format(row[0], e.message)
					print msg
					sys.exit(msg)
		writer.writerow(row)
		logger.info('upload pdf succesfull: '+row[1])
finally:

	# write remaining list back to f_IN
	f_IN.seek(0)
	csv.writer(f_IN).writerows(remaining)
	f_IN.truncate()

	f_IN.close()
	f_OUT.close()
