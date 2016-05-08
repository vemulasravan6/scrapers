__author__ = 'sravan'
import requests
from lxml import html
import csv,time,sys,os

def dictToCsvWriter(file_name=None, column_names=[ ], list_of_dicts=[ ], delimiter=',',override_existing=False):
	wrote_rows = 0
	if file_name==None:
		file_name=time.strftime("%d%m%y_%H%M%S")+".csv"
	if len(column_names)==0:
		column_names = list_of_dicts[0].keys()
	with open(file_name, "wb") as csv_file:
		writer = csv.DictWriter(f=csv_file,fieldnames=column_names,delimiter=delimiter,quoting=csv.QUOTE_NONE, quotechar='')

		writer.writeheader()
		for dict in list_of_dicts:
			try:
				writer.writerow(dict)
				wrote_rows=wrote_rows+1
			except:
				print sys.exc_info()
				print(dict)
				print('Exception occ in csv write..')
				pass
	if len(list_of_dicts)-wrote_rows>2:
		print('Report "'+file_name+'" Generated with %s rows out of %s rows '%(wrote_rows,len(list_of_dicts)))

def csvRead(file=None,debug=False,delimiter_char=','):
	csv_list = []
	ifile  = open(file, "rb")
	reader = csv.reader(ifile,delimiter=delimiter_char)
	rownum = 0
	for row in reader:
		# Save header row.
		if rownum == 0:
			header = row
		else:
			dict = {}
			colnum = 0
			for col in row:
				try:
					dict[header[colnum]] = col
					if debug:
						print '%-8s: %s' % (header[colnum], col)
				except:
					pass
				colnum += 1
			csv_list.append(dict)
		rownum += 1
	ifile.close()
	return csv_list

def productPageScraper(url, category, source):
    product_list = []
    details={}
    page = requests.get(url)
    tree = html.fromstring(page.text)
    products =  tree.xpath(".//div[contains(@class,'product-card new_ outofstock')]")
    for product in products:
        prod={}
        prod['category']    = category
        prod['source']      = source
        try:
            prod['title']=product.xpath(".//div/span[contains(@class,'product-card__name')]/text()")[0]
        except:
            prod['title']=''
            pass
        try:
            prod['available_price']=product.xpath(".//*[contains(@class,'product-card__price')]/text()")[0]
        except:
            prod['available_price']=''
            pass
        try:
            prod['mrp']=product.xpath(".//*[contains(@class,'product-card__old-price')]/text()")[0]
        except:
            prod['mrp']=''
            pass
        try:
            prod['product_discount']=product.xpath(".//*[contains(@class,'product-card__sale')]/text()")[0].replace("- ","")
        except:
            prod['product_discount']=''
            pass
        try:
            prod['product_img']=product.xpath(".//div[@class='product-card__img']/img/@data-original")[0]
        except:
            prod['product_img']=''
            pass
        try:
            prod['url']=product.xpath(".//a/@href")[0]
        except:
            prod['url']=''
            pass
        product_list.append(prod)
    return product_list

def getPaginatedUrls(base_url):
    paginated_urls = []
    url = base_url+'?itemperpage=120&page=1'
    page = requests.get(url)
    tree = html.fromstring(page.text)
    try:
        pagination_last_digit = tree.xpath(".//span[@class='pages']/a[last()]/text()")[0].strip()
        pagination_last_digit = int(pagination_last_digit)
    except:
        pagination_last_digit = ''
        pass
    i=1
    while(i<=pagination_last_digit):
        paginated_urls.append(base_url+'?itemperpage=120&page='+str(i))
        i=i+1
    return paginated_urls

def crawl():
    configs = csvRead(file='configs/configs-lazada.csv',delimiter_char=',')
    products = []
    for config in configs:
        print config
        paginated_urls = getPaginatedUrls(config['url'])
        for paginated_url in paginated_urls:
            products = products+productPageScraper(url=paginated_url,category=config['category'],source=config['source'])
    return products

fin_lis = crawl()

dictToCsvWriter(file_name='data_dump/lazada_all.csv',delimiter='^',list_of_dicts=fin_lis)