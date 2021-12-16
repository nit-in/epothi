from os import urandom
import scrapy
from datetime import date,timedelta
from pathlib import Path
from yarl import URL
import requests
import subprocess
class EpothiSpider(scrapy.Spider):
	name = 'epothi'
	allowed_domains = ['shantibabunewspapers.com/']
	base = "https://shantibabunewspapers.com"
	base_link = "https://shantibabunewspapers.com/epaper/"
	base_folder = "~/epothi"
	base_folder_path = Path(base_folder).expanduser()

	def start_requests(self):
		end_date = date.today()
		start_date = date(2021,11,20)
		for dates in self.date_range(start_date,end_date):
			news_date = dates.strftime("%d-%m-%Y")
			eng_link = self.base_link + str(news_date) + "/English/"
			for newspaper in ['BL','BS', 'ET','FE', 'NIE', 'Hindu', 'Mint']:
				paper_link = eng_link + newspaper
				print(paper_link)
				yield scrapy.Request(paper_link,self.parse_link)

			#for newspaper in ['Magazines', 'Magzines', 'Magzine']:
			#	paper_link = eng_link + newspaper
			#	print(paper_link)
			#	yield scrapy.Request(paper_link,self.parse_link_mag)

			# for newspaper in ['Editorials']:
			# 	paper_link = eng_link + newspaper
			# 	print(paper_link)
			# 	yield scrapy.Request(paper_link,self.parse_link_ed)

	def date_range(self,sd,ld):
		date_list = []
		for n in range(int((ld - sd).days)):
			date_list.append(ld-timedelta(n-1))
		return date_list

	def parse_link(self, response):
		anchors = response.css("a::attr(href)").extract()
		for link in anchors:
			if 'delhi' in str(link).lower() and 'pdf' in str(link).lower():
				self.download(link)
				break
			elif 'mumbai' in str(link).lower() and 'pdf' in str(link).lower():
				self.download(link)
				break
			else:
				pass
			

	def parse_link_ed(self, response):
		anchors = response.css("a::attr(href)").extract()
		for link in anchors:
			if '.pdf' in str(link).lower():
				self.download(link)

	def parse_link_mag(self, response):
		anchors = response.css("a::attr(href)").extract()
		for link in anchors:
			if 'ad.pdf' in str(link).lower():
				pass
			elif 'ad.jpg' in str(link).lower():
				pass
			elif '.pdf' in str(link).lower():
				self.download(link)
			else:
				pass


	def check_folder(self,folder_path):
		if folder_path.exists():
			pass
		else:
			folder_path.mkdir(parents=True)


	def check_file(self,file_name,file_size):
		if file_name.exists() and file_name.lstat().st_size==file_size:
			return True
		else:
			return False

	def download(self,link):
		self.check_folder(self.base_folder_path)
		link = self.base + link
		url = URL(link)
		np = url.parts[4]
		ed = url.parts[5]
		dt = url.parts[2]
		date_path = Path(self.base_folder_path,dt)
		np_path = Path(date_path,np)
		self.check_folder(np_path)
		pdfname = np +"_"+ dt + "_" +ed
		file_path = Path(np_path,pdfname)
		re = requests.head(link).headers["Content-Length"]
		if not self.check_file(file_path,int(re)):
			self.wget_download(link,file_path)
		else:
			pass

	def wget_download(self,link,pdf_path):
		program = "wget"
		arg1 = "--show-progress"
		arg2 = "--server-response"
		arg3 = "--continue"
		arg4 = "-O"
		print(f"\nDownloading: {pdf_path}")
		print(f"pdf_pth {pdf_path}")
		print(f"link {link}")
		subprocess.call([program,arg1,arg2,arg3,str(link),arg4,str(pdf_path)])
