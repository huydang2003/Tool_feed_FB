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

	def get_list_fb_id(self):
		f = open('cookie.txt', 'r')
		self.data = f.read()
		f.close()
		self.list_fb_id = re.findall(r'c_user=(.*?);', self.data)

	def check_cookie(self, fb_id):
		check = False
		list_cookie = self.data.split('\n')
		cout = 1
		for cookie in list_cookie:
			c_user = re.findall(r'c_user=(.*?);', cookie)
			if c_user == []: print(f'Line {cout}: cookie sai!!!')
			else:
				user_id = c_user[0]
				if user_id != fb_id: continue
				self.input[user_id] = {}
				token = self.get_token(cookie)		
				if token=='': print(f'Line {cout}: {self.list_nick[user_id]} >> cookie die!!!')
				else:
					print(f'Line {cout}: {user_id} >> cookie live!!!')
					self.input[user_id]['cookie'] = cookie
					self.input[user_id]['token'] = token
					path_file_data = f'data/{user_id}'
					if not os.path.exists(path_file_data): os.mkdir(path_file_data)
					self.get_info(user_id, path_file_data)
					check = True
				break
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

	def get_profile(self, user_id):
		params = {'access_token':self.input[user_id]['token']}
		url = f'https://graph.facebook.com/me?feed'
		res = self.ses.get(url, params=params)
		data = res.json()
		return data

	def get_list_friend(self, user_id):
		params = {'access_token':self.input[user_id]['token']}
		url = f'https://graph.facebook.com/me?fields=friends'
		res = self.ses.get(url, params=params)
		data = res.json()
		data = data['friends']['data']
		return data

	def get_info(self, user_id, path_file_data):
		data = self.get_profile(user_id)
		path_output = f'{path_file_data}/info.json'
		self.save_file_json(path_output, data)
		data = self.get_list_friend(user_id)
		path_output = f'{path_file_data}/list_friend.json'
		self.save_file_json(path_output, data)

	def show_info(self, fb_id):
		path_index = f'data/{fb_id}'
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

	def friend_request(self, fb_id, link):
		cookie = self.input[fb_id]['cookie']
		headers = self.get_headers(cookie)
		self.ses.get(link, headers=headers)

# Lay bao viet tren trang ca nhan(link comment, va link binh luan)
	def get_list_story_home(self, fb_id):
		list_story = {}
		cookie = self.input[fb_id]['cookie']
		headers = self.get_headers(cookie)
		res = self.ses.get('https://mbasic.facebook.com/home.php', headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.find(id='m_newsfeed_stream')
		list_div = soup.find_all('div')
		cout = 1
		for div in list_div:
			if div.get('role') == "article":
				temp = {'title':'', 'reaction_link':'', 'cmt_link':''}
				temp['title'] = div.text[0:25]+'...'
				list_a = div.find_all('a')
				for a in list_a:
					url = a.get('href')
					if '/reactions/' in url:
						link = 'https://mbasic.facebook.com' + url
						temp['reaction_link'] = link
					if '/story.php?' in url or '/groups/' in url:
						link = 'https://mbasic.facebook.com' + url
						temp['cmt_link'] = link
				if temp['reaction_link'] != '':
					list_story[cout] = temp
					cout+=1
		return list_story

# Lay bao viet nick(link comment, va link binh luan)
	def get_list_story_friend(self, fb_id, id_friend):
		list_story = {}
		cookie = self.input[fb_id]['cookie']
		headers = self.get_headers(cookie)
		res = self.ses.get(f'https://mbasic.facebook.com/profile.php?id={id_friend}', headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.find(id='structured_composer_async_container')
		list_div = soup.find_all('div')
		cout = 1
		for div in list_div:
			if div.get('role') == "article":
				temp = {'title':'', 'reaction_link':'', 'cmt_link':''}
				temp['title'] = div.text[0:25]+'...'
				list_a = div.find_all('a')
				for a in list_a:
					url = a.get('href')
					if '/reactions/' in url:
						link = 'https://mbasic.facebook.com' + url
						temp['reaction_link'] = link
					if '/story.php?' in url or '/groups/' in url:
						link = 'https://mbasic.facebook.com' + url
						temp['cmt_link'] = link
				if temp['reaction_link'] != '':
					list_story[cout] = temp
					cout+=1
		return list_story
		
# Lay link bao mang
	def get_link(self):
		list_link = []
		list_link_web = [
			'https://news.zing.vn',
			'https://vnexpress.net',
			'https://www.24h.com.vn',
			'http://vietnamnet.vn',
			'https://tuoitre.vn',
			'http://kenh14.vn',
			'https://www.dkn.tv',
			'http://www.doisongphapluat.com',
			'http://dantri.com.vn',
			'https://thanhnien.vn'
		]
		link_web = random.choice(list_link_web)
		for link_web in list_link_web:
			res = self.ses.get(link_web)
			soup = BeautifulSoup(res.content, 'html.parser')
			list_a = soup.body.find_all('a')
			list_a = list_a[1:]
			cout = 0
			for a in list_a:
				if cout > 4: break
				title = a.text
				if len(title) > 50:
					url = a.get('href')
					if 'javascript' in url: continue
					if len(url) < 25: continue
					if 'https' not in url:
						url = link_web + url
					list_link.append(url)
					cout+=1
		f = open('input/list_link.json', 'w', encoding='utf8')
		json.dump(list_link, f, indent=4)
		f.close()

# comment bai viet
	def comment_story(self, fb_id, link, content):
		cookie = self.input[fb_id]['cookie']
		headers = self.get_headers(cookie)
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.body.find(id="root")
		check = False

		list_h3 = soup.find_all('h3')
		if list_h3 == []: return check
		for h3 in list_h3:
			a = h3.find_all('a')
			if a == []: continue
			url = a[0].get('href')
			if self.fb_info[fb_id]['username'] in url:
				return check

		list_form = soup.find_all('form')
		if list_form == []: return check
		for form in list_form:
			url = form.get('action')
			if '/comment.php?' in url:
				ls_input = form.find_all('input')
				payload = {'comment_text': content, 'fb_dtsg': '', 'jazoest': ''}
				for i in ls_input:
					if i.get('name') == 'fb_dtsg': payload['fb_dtsg'] = i.get('value')
					if i.get('name') == 'jazoest': payload['jazoest'] = i.get('value')
				check = True
				break
		if check == True:
			url = 'https://mbasic.facebook.com' + url
			self.ses.post(url, data=payload, headers=headers)

			res = self.ses.get(link, headers=headers)
			# soup = BeautifulSoup(res.content, 'html.parser')
			# soup = soup.body.find(id="root")
			# list_h3 = soup.find_all('h3')
			# if list_h3 == []: return check
			# for h3 in list_h3:
			# 	a = h3.find_all('a')
			# 	if a == []: continue
			# 	url = a[0].get('href')
			# 	if self.fb_info[fb_id]['username'] in url:
			# 		return check


			f = open('html.html', 'w', encoding='utf8')
			f.write(res.text)
			f.close()
		return check

# bay to cam bai viet
	def reaction_story(self, fb_id, link, reaction):
		cookie = self.input[fb_id]['cookie']
		headers = self.get_headers(cookie)
		res = self.ses.get(link, headers=headers)
		soup = BeautifulSoup(res.content, 'html.parser')
		soup = soup.body.find(id='root')
		check = False
		list_li = soup.find_all('li')
		if list_li == []: return check
		dict_reactions = {'LIKE':0, 'LOVE':1, 'TUTU':2, 'HAHA':3, 'WOW':4, 'SAD':5, 'ANGRY':6}
		vt = dict_reactions[reaction]
		url = list_li[vt].a.get('href')	
		link = 'https://mbasic.facebook.com' + url
		self.ses.get(link, headers=headers)
		check = True
		return check

# dang link
	def post_link(self, fb_id, link):
		params = {'access_token': self.input[fb_id]['token']}
		list_message =['^(*-*)^', '(>_<)', '(-__-)', '(>_<)_<)', '(X_X)', '(@_@)', '→_→', '(o_O)','(=_=)']
		message = '#bot_share_link' + ' ' + random.choice(list_message)
		payload = {'message': message, 'link':link}
		url = 'https://graph.facebook.com/me/feed?'
		res = self.ses.post(url, data=payload, params=params)

# tu dong comment ang reaction
def auto_reaction_and_comment(tool, fb_id):
	f = open('input/list_cmt.txt', 'r', encoding='utf8')
	data = f.read()
	f.close()
	if data=='': list_cmt = ['tương tác tốt :)']
	else: list_cmt = data.split('|')

	sl = random.randint(1, 1)
	print(f'Bình luận và bày tỏ cảm súc bài viết tới {sl} người!!!')
	cout = 1
	while True:
		list_story = tool.get_list_story_home(fb_id)
		for stt in list_story:
			title = list_story[stt]['title']
			reaction_link = list_story[stt]['reaction_link']
			cmt_link = list_story[stt]['cmt_link']
			print('+++>>>', cout ,'>>|bài viết:',title)
			if reaction_link != '':
				list_reactions = ['LIKE', 'LOVE', 'TUTU', 'HAHA', 'WOW']
				reaction = random.choice(list_reactions)
				check = tool.reaction_story(fb_id, reaction_link, reaction)
				print('\t', end='')
				if check == True: print('<|reaction:', reaction)
				else: print('<|reaction:', check)
			if cmt_link != '':
				content = f'#bot_comment #{cout} {random.choice(list_cmt)}'
				check = tool.comment_story(fb_id, cmt_link, content)
				print('\t', end='')
				if check == True: print('<|comment:', content)
				else: print('<|comment:',check)
			cout += 1
			if cout > sl: return True

			s = random.randint(5,10)
			print(f'>>delay {s}s')
			sleep(s)

# Auto dang bai viet
def auto_post_link(tool, fb_id):
	f = open('input/list_link.json', 'r')
	list_link = json.load(f)
	f.close()
	
	sl = random.randint(1,3)
	print(f'Tự động đăng {sl} bài viết!!!')
	cout = 1
	while True:
		if list_link==[]:
			print('Cho link vào file "input/list_link.txt"!!!')
			return False
		link = random.choice(list_link)
		list_link.remove(link)
		tool.post_link(fb_id, link)
		print(f'  >>>{cout}>>POST LINK: {link}')
		cout+=1
		if cout > sl: return True
		s = random.randint(10,30)
		print(f'>>delay {s}s')
		sleep(s)

# Tu dong ket ban de xuat
def auto_send_friend_suggest(tool, fb_id):
	list_friend_suggest = tool.get_list_friend_suggest(fb_id)
	if list_friend_suggest=={}:
		print('Không có bạn bè gợi ý !!! haha')
		return False
	sl = len(list_friend_suggest)
	print(f'+++>>>Đang gửi lời mời kết bạn tới {sl} người:')
	cout = 1
	for id_friend in list_friend_suggest:
		link = list_friend_suggest[id_friend]
		tool.friend_request(fb_id, link)
		print(f'\t>>>{cout}>>send: {id_friend}', end=' ')
		cout+=1
		s = random.randint(1,5)
		print(f'>>delay {s}s')
		sleep(s)
	return True

# Tu dong chap nhan ket ban
def auto_accept_friend_request(tool, fb_id):
	list_friend_request = tool.get_list_friend_request(fb_id)
	if list_friend_request=={}:
		print('Không có lời mời kết bạn!!!')
		return False
	print(f'>>>>>Tìm thấy {len(list_friend_request)} lời mời!!!')
	print('Bắt đầu chấp nhận và tương tác:')
	max_story = random.randint(2,5)
	cout = 1
	for id_friend in list_friend_request:
		link = list_friend_request[id_friend]
		tool.friend_request(fb_id, link)
		print(f'>>>>{cout}>>>accept ID: {id_friend}')
		list_story = tool.get_list_story_friend(fb_id, id_friend)
		if list_story=={}: return False
		print(f'Có {len(list_story)} bài viết!!!')
		for stt in list_story:
			title = list_story[stt]['title']
			reaction_link = list_story[stt]['reaction_link']
			cmt_link = list_story[stt]['cmt_link']
			print('+>', stt ,'>>|bài viết:',title)
			if reaction_link != '':
				list_reactions = ['LIKE', 'LOVE', 'TUTU', 'HAHA', 'WOW']
				reaction = random.choice(list_reactions)
				check = tool.reaction_story(fb_id, reaction_link, reaction)
				print('\t', end='')
				if check == True: print('<|reaction:', reaction)
				else: print('<|reaction:', check)
			cout += 1
			if cout > max_story: return True
			s = random.randint(1,3)
			print(f'>>delay {s}s')
			sleep(s)
	return True

if __name__ == '__main__':
	if not os.path.exists('data'): os.mkdir('data')
	if not os.path.exists('input'): os.mkdir('input')
	if not os.path.exists('cookie.txt'): open('cookie.txt', 'w').close()
	if not os.path.exists('input/list_cmt.txt'): open('input/list_cmt.txt', 'w').close()
	tool = FB_tool()
	# tool.get_link()
	tool.get_list_fb_id()
	for fb_id in tool.list_fb_id:
		tool.check_cookie(fb_id)
		tool.show_info(fb_id)
		print(tool.list_fb_id)
		list_tt = [1, 2, 3, 4]
		random.shuffle(list_tt)
		for x in list_tt:
			if x==1:
				check = auto_reaction_and_comment(tool, fb_id)
				if check == True: print('\n><><><Tự động comment => xong!!!\n')
			# if x==2:
			# 	check = auto_send_friend_suggest(tool, fb_id)
			# 	if check == True: print('\n><><><Tự động gửi kết bạn => xong!!!\n')
			# if x==3:
			# 	check = auto_post_link(tool, fb_id)
			# 	if check == True: print('\n><><><Tự động đăng bài => xong!!!\n')
			# if x==4:
			# 	check = auto_accept_friend_request(tool, fb_id)
			# 	if check == True: print('\n><><><Tự động chấp nhận bạn bè => xong!!!\n')
		print('\nHoàn thành 1 của nợ!!!\n')
		s = random.randint(30,45)
		print(f'\nChuyển FB sau {s}s..\n')
		sleep(s)
	print('Xong')