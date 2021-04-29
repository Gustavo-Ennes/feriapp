from django.test import TestCase
from urllib import request
from bs4 import BeautifulSoup as bs
import requests
from app.models import Banner

class BannerTest(TestCase):
	@classmethod
	def setUpTestData(self):
		self.site_name = "https://www.ilhasolteira.sp.gov.br"
		self.slide_tag = 'sp-pc-post'
		self.slide_container_type = 'div'
		self.tags = {
	        'titulo': '.sp-pc-post-title a',
	        'descricao':'sp-pc-content',
	        'img_link': 'sp-pc-post-img',
	        'link': 'sp-pc-post-image a',
	    }

	def test_site_is_up(self):
		self.assertEqual(
			request.urlopen(self.site_name).getcode(), 
			200
		)

	def test_there_are_slides(self):
		soup = bs(requests.get(self.site_name).content, 'html.parser')
		slides = soup.find_all(self.slide_container_type, {'class': self.slide_tag})
		self.assertGreater(
			len(slides),
			0
		)

	def test_slides_in_db(self):
		banners = Banner.objects.all()
		soup = bs(requests.get(self.site_name).content, 'html.parser')
		slides = soup.find_all(self.slide_container_type, {'class': self.slide_tag})
		pass_test = False

		if slides and banners:
			# slides[len(slides) - 1] comparado com Banners[0]
			last_getted_slide = slides[len(slides) - 1]
			first_slide_in_query = banners[0]
			if last_getted_slide.find('img', self.tags['img_link']).get('src') != first_slide_in_query.link_img:
				pass_test = True


		self.assertTrue(pass_test)