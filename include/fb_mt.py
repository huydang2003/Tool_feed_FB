import os
import requests
from bs4 import BeautifulSoup
import re
import json

class fb_mt():
	def __init__(self):
		self.ses = requests.session()

	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def load_file_json(self, path_input):
		f = open(path_input, 'r', encoding='utf8')
		data = json.load(f)
		f.close()
		return data

	def get_headers(self, cookie):
		headers_fb = {
			'authority': 'mbasic.facebook.com',
			'upgrade-insecure-requests': '1',
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-mode': 'navigate',
			'accept-language': 'en-US,en;q=0.9',
			'user_agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36',
			'cookie': cookie
		}
		return headers_fb

	def get_token(self, cookie):
		headers = self.get_headers(cookie)
		url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
		res = self.ses.get(url, headers=headers)
		token = re.findall(r'accessToken\\":\\"(.*?)\\', res.text)
		if token != []: token = token[0]
		else: token = ''
		return token

	def check_cookie(self, cookie_fb):
		token = self.get_token_fb(cookie_fb)
		if token=='': return False
		else: return True

	def get_save_info(self, name, cookie):
		token = self.get_token(cookie)
		params = {'access_token': token}
		url = 'https://graph.facebook.com/me?feed'
		res = self.ses.get(url, params=params)
		data = res.json()
		if 'error' not in data:
			# try:
				path_data = f'data/nicks/{name}'
				if not os.path.exists(path_data): os.mkdir(path_data)
				path_output = f'{path_data}/info.json'
				self.save_file_json(path_output, data)
				url = 'https://graph.facebook.com/me?fields=friends'
				res = self.ses.get(url, params=params)
				data = res.json()
				data = data['friends']['data']
				path_output = f'{path_data}/list_friend.json'
				self.save_file_json(path_output, data)
			# except: pass

	def show_info(self, name):
		path_index = f'data/nicks/{name}'
		if os.path.exists(path_index):
			path_input = f'{path_index}/info.json'
			data = self.load_file_json(path_input)
			fb_info = {'name':'', 'id':0, 'username': '', 'birthday':0, 'email':None, 'friends':0}
			fb_info['id'] = data['id']
			fb_info['birthday'] = data['birthday']
			fb_info['name'] = data['name']
			fb_info['username'] = data['id']	
			if 'email' in data: fb_info['email'] = data['email']
			if 'username' in data: fb_info['username'] = data['username']
			path_input = f'{path_index}/list_friend.json'
			data = self.load_file_json(path_input)
			fb_info['friends'] = len(data)
			print('<=============================>')
			for tt in fb_info: print('>>>',tt,':',fb_info[tt]) 
			print('<=============================>')
		else:
			print('<=============================>')
			print('>>>No have information!!!')
			print('<=============================>')
# Lay danh sach new feed
	def get_list_story(self, cookie):
		list_story = []
		headers=self.get_headers(cookie)
		res = self.ses.get('https://mbasic.facebook.com/home.php', headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		main = soup.find(id='m_newsfeed_stream')
		data = str(main)
		list_story = re.findall(r'\"like_(.*?)\"', data)
		return list_story
# Lấy thong tin bài viết
	def get_info_story(self, token, id_status):
		params = {'access_token': token}
		url = f'https://graph.facebook.com/{id_status}?fields=from, message'
		res = self.ses.get(url, params=params)
		data = res.json()
		if 'error' in data: return False #Id lỗi
		else:
			if 'from' not in data: return False
			if 'category' in data['from']: return False
			else:
				if 'name' in data['from']:
					title = data['from']['name']
				else:
					title = ''
				if 'message' in data:
					caption = data['message'].replace('\n', '')
					if len(caption)>30: caption = caption[0:25]+'...'
				else:
					caption = '???'
		return title, caption
# comment bai viet
	def comment_story(self, token, id_status, content):
		params = {'access_token': token, 'message':content}
		url = f'https://graph.facebook.com/{id_status}/comments'
		res = self.ses.post(url, params=params)
		data = res.json()
		if 'id' in data: return 1
		else:
			if data['error']['code'] == 368: return 2 # block
			if data['error']['code'] == 190: return 3 #Cookie die
			else: return 0 #Loi link
# bay to cam bai viet
	def reaction_story(self, cookie, token, id_status, reaction):
		dict_reaction = {'LIKE':0, 'LOVE':1, 'THUONGTHUONG':2, 'HAHA':3, 'WOW':4, 'SAD':5, 'ANGRY':6}
		params = {'access_token': token}
		url = f'https://graph.facebook.com/{id_status}/likes'
		res = self.ses.post(url, params=params)
		data = res.json()
		if data != True:
			if data['error']['code'] == 368: return 2 # block
			if data['error']['code'] == 190: return 3 #Cookie die
			else: return 0 #Loi link
		if reaction!='LIKE':	
			link = 'https://mbasic.facebook.com/reactions/picker/?is_permalink=1&ft_id='+id_status
			headers = self.get_headers(cookie)
			res = self.ses.get(link, headers=headers)
			soup = BeautifulSoup(res.content, 'html.parser')
			soup = soup.body.find(id='root')
			list_li = soup.find_all('li')	
			vt = dict_reaction[reaction]
			try: url = list_li[vt].a.get('href')
			except: return 0	
			link = 'https://mbasic.facebook.com' + url
			self.ses.get(link, headers=headers)
		return 1
# Lay danh sach loi moi ket ban
	def get_list_friend_request(self, cookie):
		list_friend_request = {}
		headers = self.get_headers(cookie)
		res = self.ses.get('https://mbasic.facebook.com/friends/center/requests', headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.find(id='friends_center_main')
		soup = soup.find_all('tbody')
		for f1 in soup:
			f1 = f1.find_all('a')
			for f2 in f1:
				url = f2.get('href')
				if 'confirm=' in url:
					id_user = re.findall(r'confirm=(.*?)&', url)[0]
					link = 'https://mbasic.facebook.com' + url
					list_friend_request[id_user] = link
		return list_friend_request
# Lay danh sach ban	goi y
	def get_list_friend_suggest(self, cookie):
		list_friend_suggest = {}
		headers = self.get_headers(cookie)
		res = self.ses.get('https://mbasic.facebook.com/friends/center/suggestions', headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.find(id='objects_container')
		soup = soup.find_all('tbody')
		for f1 in soup:
			f1 = f1.find_all('a')
			for f2 in f1:
				url = f2.get('href')
				if 'add_friend.php' in url:
					id_user = re.findall(r'id=(.*?)&', url)[0]
					link = 'https://mbasic.facebook.com' + url
					list_friend_suggest[id_user] = link
		return list_friend_suggest
# Dang bai viet
	def post_photo(self, token, content, link_photo):
		check = False
		params = {'access_token': token}
		url = 'https://graph.facebook.com/me?fields=albums'
		res = requests.get(url, params=params)
		data = res.json()
		list_albums = data['albums']['data']
		for albums in list_albums:
			if albums['type'] == 'wall' or albums['type'] == 'mobile':
				id_albums = albums['id']
				break
		url = f'https://graph.facebook.com/{id_albums}/photos'
		payload = {'message': content, 'url': link_photo}
		res = requests.post(url, data=payload, params=params)
		if 'post_id' in res.json(): check = True
		return check

	def friend_request(self, cookie, link):
		headers = self.get_headers(cookie)
		self.ses.get(link, headers=headers)