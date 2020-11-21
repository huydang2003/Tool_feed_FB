import json
from time import localtime

class setting():
	def save_file_json(self, path_input, data):
		f = open(path_input, 'w', encoding='utf8')
		json.dump(data, f, ensure_ascii=False, indent=4)
		f.close()

	def load_file_json(self, path_input):
		f = open(path_input, 'r', encoding='utf8')
		data = json.load(f)
		f.close()
		return data

	def fill_cookie(self, cookie):
		try:
			cookie = cookie.split(';')
			for cookie_tp in cookie:
				if 'c_user' in cookie_tp: c_user = cookie_tp.split('=')[1]
				if 'xs' in cookie_tp: xs = cookie_tp.split('=')[1]
				if 'datr' in cookie_tp: datr = cookie_tp.split('=')[1]
			cookie = f'c_user={c_user};xs={xs};datr={datr};'
			return cookie
		except: return ''

	def show_nick(self):
		list_nick = self.load_file_json('data/nicks.json')
		print("<<<///Danh sách nick chạy:")
		cout = 0
		for nick in list_nick:
			print(f"{cout}.{list_nick[cout]['name']}")
			cout+=1
		print("///>>>")
	
	def add_nick(self, name, cookie):
		list_nick = self.load_file_json('data/nicks.json')
		nick = {}
		nick['name'] = name
		nick['cookie'] = self.fill_cookie(cookie)
		list_nick.append(nick)
		self.save_file_json('data/nicks.json', list_nick)

	def edit_nick(self, vt, cookie):
		try:
			list_nick = self.load_file_json('data/nicks.json')
			cookie = self.fill_cookie(cookie)
			if cookie != '': list_nick[vt]['cookie'] = cookie
			self.save_file_json('data/nicks.json', list_nick)
		except: pass

	def delete_nick(self, vt):
		try:
			list_nick = self.load_file_json('data/nicks.json')
			list_nick.pop(vt)
			self.save_file_json('data/nicks.json', list_nick)
		except: pass

	def time_now(self):
		h = localtime().tm_hour
		p = localtime().tm_min
		s = localtime().tm_sec
		if int(h)<10: h = f'0{h}'
		if int(p)<10: p = f'0{p}'
		if int(s)<10: s = f'0{s}'
		time_now = f'{h}:{p}:{s}'
		return time_now