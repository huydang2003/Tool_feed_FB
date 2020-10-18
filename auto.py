import requests
from bs4 import BeautifulSoup
import re
import json
import os
import random
from time import sleep

class FB_tool(object):
	def __init__(self):
		self.ses = requests.session()
		self.input = {}
		self.fb_info = {}
		self.list_fb_id = []
		self.data = None
		self.list_ct = {}

	def get_list_fb_id(self):
		self.data = open('input/cookie.txt', 'r').read()	
		self.list_fb_id = re.findall(r'c_user=(.*?);', self.data)

	def check_cookie(self, fb_id):
		list_cookie = self.data.split('\n')
		cout = 1
		check = False
		for cookie in list_cookie:
			if cookie=='': continue
			fc = re.findall(r'c_user=(.*?);', cookie)
			if fc == []: continue
			temp = fc[0]
			if temp==fb_id:
				token = self.get_token(cookie)
				if token=='':
					print(f'[cookie DIE (line {cout})]')
					return check
				self.list_ct[fb_id] = {}
				self.list_ct[fb_id]['cookie'] = cookie
				self.list_ct[fb_id]['token'] = token
				print(f'[cookie LIVE (line {cout})]')
				self.get_info(token)
				check = True
				return check
			cout+=1
		print('No have cookie')
		return check
				
	def get_headers(self, cookie):
		headers = {
			'authority': 'mbasic.facebook.com',
			'upgrade-insecure-requests': '1',
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-mode': 'navigate',
			'accept-language': 'en-US,en;q=0.9',
			'user_agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36'
		}
		headers['cookie'] = cookie
		return headers

	def get_token(self, cookie):
		url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
		res = self.ses.get(url, headers=self.get_headers(cookie))
		token = re.findall(r'accessToken\\":\\"(.*?)\\', res.text)
		if token != []: token = token[0]
		else: token = ''
		return token

	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def get_info(self, token):
		params = {'access_token': token}
		url = 'https://graph.facebook.com/me?feed'
		res = self.ses.get(url, params=params)
		data = res.json()
		path_data = f'data/{data["name"]}_{data["id"]}'
		if not os.path.exists(path_data): 
			os.mkdir(path_data)
			path_output = f'{path_data}/info.json'
			self.save_file_json(path_output, data)
			url = 'https://graph.facebook.com/me?fields=friends'
			res = self.ses.get(url, params=params)
			data = res.json()
			data = data['friends']['data']
			path_output = f'{path_data}/list_friend.json'
			self.save_file_json(path_output, data)

	def show_info(self, fb_id):
		list_folder = os.listdir('data')
		name_folder = fb_id
		for x in list_folder:
			if fb_id in x: name_folder = x
		path_index = f'data/{name_folder}'
		if os.path.exists(path_index):
			path_input = f'{path_index}/info.json'
			data = self.load_file_json(path_input)
			self.fb_info[fb_id] = {'name':'', 'id':0, 'username': '', 'birthday':0, 'email':'', 'friends':0}
			self.fb_info[fb_id]['id'] = data['id']
			self.fb_info[fb_id]['birthday'] = data['birthday']
			self.fb_info[fb_id]['email'] = data['email']
			self.fb_info[fb_id]['name'] = data['name']
			self.fb_info[fb_id]['username'] = data['id']	
			if 'username' in data:
				self.fb_info[fb_id]['username'] = data['username']
			path_input = f'{path_index}/list_friend.json'
			data = self.load_file_json(path_input)
			self.fb_info[fb_id]['friends'] = len(data)
			print('<=============================>')
			for tt in self.fb_info[fb_id]: print('>>>',tt,':',self.fb_info[fb_id][tt]) 
			print('<=============================>')
		else:
			print('<=============================>')
			print('>>>No have information!!!')
			print('<=============================>')

	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def load_file_json(self, path_input):
		f = open(path_input, 'r', encoding='utf8')
		data = json.load(f)
		f.close()
		return data

# Lay danh sach loi moi ket ban
	def get_list_friend_request(self, fb_id):
		list_friend_request = {}
		cookie = self.input[fb_id]['cookie']
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
	def get_list_friend_suggest(self, fb_id):
		list_friend_suggest = {}
		cookie = self.input[fb_id]['cookie']
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

# Lay bao viet tren trang ca nhan(link comment, va link binh luan)
	def get_list_story(self, cookie, link):
		list_story = []
		headers=self.get_headers(cookie)
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.find(id='m_newsfeed_stream')
		list_span = soup.find_all('span')
		for span in list_span:
			temp = str(span.get('id'))
			if 'like' in temp:
				id_status = temp.replace('like_', '')
				list_story.append(id_status)
		return list_story

# Lấy info bài viết
	def get_info_story(self, token, id_status):
		params = {'access_token': token}
		url = f'https://graph.facebook.com/{id_status}?fields=from, message'
		res = self.ses.get(url, params=params)
		data = res.json()
		try:
			title = data['from']['name']
			caption = data['message']
			if len(caption)>30: caption = caption[0:25]+'...'
		except:
			title = ''
			caption = '??????'
		return title, caption

# comment bai viet
	def comment_story(self, token, id_status, content):
		params = {'access_token': token, 'message':content}
		url = f'https://graph.facebook.com/{id_status}/comments'
		res = self.ses.post(url, params=params)
		data = res.json()
		if 'id' in data: return 1
		else:
			if data['error']['code'] != 368: return 0
			else: return 2
		return check

# bay to cam bai viet
	def reaction_story(self, cookie, token, id_status, reaction):
		params = {'access_token': token}
		url = f'https://graph.facebook.com/{id_status}/likes'
		res = self.ses.post(url, params=params)
		data = res.json()
		if data != True:
			if data['error']['code'] != 368: return 0
			else: return 2
		else:	
			dict_reaction = {'LIKE':0, 'LOVE':1, 'TUTU':2, 'HAHA':3, 'WOW':4, 'SAD':5, 'ANGRY':6}
			link = 'https://mbasic.facebook.com/reactions/picker/?is_permalink=1&ft_id='+id_status
			headers = self.get_headers(cookie)
			res = self.ses.get(link, headers=headers)
			soup = BeautifulSoup(res.content, 'html.parser')
			soup = soup.body.find(id='root')
			list_li = soup.find_all('li')	
			vt = dict_reaction[reaction]
			url = list_li[vt].a.get('href')	
			link = 'https://mbasic.facebook.com' + url
			self.ses.get(link, headers=headers)
			return 1

	def post_photo(self, token, content, link_photo):
		check = False
		params = {'access_token': token}
		url = 'https://graph.facebook.com/me?fields=albums'
		res = requests.get(url, params=params)
		data = res.json()
		list_albums = data['albums']['data']
		for albums in list_albums:
			if albums['type'] == 'wall':
				id_albums = albums['id']
				break
		url = f'https://graph.facebook.com/{id_albums}/photos'
		payload = {'message': content, 'url': link_photo}
		res = requests.post(url, data=payload, params=params)
		if 'post_id' in res.json(): check = True
		return check

	def friend_request(self, cookie, fb_id, link):
		headers = self.get_headers(cookie)
		self.ses.get(link, headers=headers)

def auto_comment_reaction(tool):
	list_reaction = ['LOVE','TUTU','HAHA','WOW']
	data = open('input/list_cmt.txt', 'r', encoding='utf8').read()
	list_cmt = data.split('|')
	sl = random.randint(7, 15)
	print(f'[Tự động tương tác với {sl} người]')
	cout = 0
	list_story = []
	list_story_old = []
	list_tt = [1, 2]
	link = 'https://mbasic.facebook.com/home.php'
	while cout < sl:
		cookie = tool.list_ct[fb_id]['cookie']
		token = tool.list_ct[fb_id]['token']
		while True:
			if len(list_story)>0: break
			list_story = tool.get_list_story(cookie, link)
		for id_status in list_story:
			if id_status in list_story_old: continue
			info = tool.get_info_story(token, id_status)
			name = info[0]
			caption = info[1]
			print(f'>>>bài viết:{name}|{caption}')
			for x in list_tt:
				reaction = random.choice(list_reaction)
				content = f'Hi {name}!!!Chúc ngày mới tốt lành!!!\n{random.choice(list_cmt)}'
				if x==1:
					check = tool.reaction_story(cookie, token, id_status, reaction)
					if check==1: print(f'\t>>>reaction: {reaction}')
					if check==2:
						print('\t>>>Block reaction!!!')
						# list_tt.remove(x)
						break
				if x==2:
					check = tool.comment_story(token, id_status, content)
					if check==1: print(f'\t>>>comment: {content}')
					if check==2:
						print('\t>>>Block comment!!!')
						# list_tt.remove(x)
						break
				cout+=1
			s = random.randint(5, 10)
			print(f'[wait {s}s]')
			sleep(s)

def auto_post_photos(tool):
	print('\n[Tự động đăng bài viết]')
	token = tool.list_ct[fb_id]['token']
	data = open('input/list_cap.txt', 'r', encoding='utf8').read()
	list_cap = data.split('\n\n')
	content = random.choice(list_cap)
	link_photo = 'https://source.unsplash.com/random'
	check = tool.post_photo(token, content, link_photo)
	if check == True: print('Đăng bài viết thành công!!!')
	else: print('Đăng bài viết thất bại!!!')

def auto_send_friend_suggest(tool, fb_id):
	print('\n[Tự động gửi lời mời kết bạn]')
	cookie = tool.list_ct[fb_id]['cookie']
	list_friend_suggest = tool.get_list_friend_suggest(fb_id)
	if list_friend_suggest=={}:
		print('[Không có bạn bè gợi ý !!!]')
	else:
		sl = random.randint(3, len(list_friend_suggest)) 
		print(f'\n[Đang gửi lời mời kết bạn tới {sl} người:]')
		cout = 1
		for id_friend in list_friend_suggest:
			link = list_friend_suggest[id_friend]
			tool.friend_request(cookie, fb_id, link)
			print(f'\t>>>{cout}>>send: {id_friend}', end=' ')
			cout+=1
			s = random.randint(1,5)
			print(f'>>delay {s}s')
			sleep(s)

if __name__ == '__main__':
	if not os.path.exists('data'): os.mkdir('data')
	if not os.path.exists('input'): os.mkdir('input')
	if not os.path.exists('input/cookie.txt'): open('input/cookie.txt', 'w').close()
	if not os.path.exists('input/list_cmt.txt'): open('input/list_cmt.txt', 'w').close()
	if not os.path.exists('input/list_cap.txt'): open('input/list_cap.txt', 'w').close()
	input('Thêm thông tin vào thư mục "input"!!!')
	tool = FB_tool()
	tool.get_list_fb_id()
	for fb_id in tool.list_fb_id:
		tool.check_cookie(fb_id)
		tool.show_info(fb_id)
		list_tt = [1, 2, 3, 4]
		random.shuffle(list_tt)
		for x in list_tt:
			if x==1: auto_comment_reaction(tool)
			if x==2: auto_post_photos(tool)
			if x==3: auto_send_friend_suggest(tool, fb_id)		
		print('\nHoàn thành 1 của nợ!!!\n')
		s = random.randint(30,45)
		print(f'\nChuyển FB sau {s}s..\n')
		sleep(s)
	print('Xong')