import os
import random
from time import sleep
from include.setting import setting
from include.fb_mt import fb_mt

class Tool_feed_fb():
	if not os.path.exists('data'): os.mkdir('data')
	if not os.path.exists('data/nicks'): os.mkdir('data/nicks')
	if not os.path.exists('data/nicks.json'): open('data/nicks.json', 'w').write('[]')
	if not os.path.exists('comment.txt'): open('comment.txt', 'w').close()
	if not os.path.exists('status.txt'): open('status.txt', 'w').close()
	def __init__(self):
		self.fb_mt = fb_mt()
		self.setting = setting()
		self.list_nick = None

	def auto_post_photos(self, cookie):
		print('\n[AUTO ĐĂNG BÀI VIẾT]')
		list_cap = open('status.txt', 'r', encoding='utf8').read().split('\n\n')
		content = random.choice(list_cap)
		link_photo = 'https://source.unsplash.com/random'
		token = self.fb_mt.get_token(cookie)
		check = self.fb_mt.post_photo(token, content, link_photo)
		if check == True: print(f'\t[{self.setting.time_now()}] [POST SUCCESS]')
		else: print('\t[POST FAILED]')

	def auto_send_friend_suggest(self, cookie):
		print('\n[AUTO GỬI LỜI MỜI KB]') 
		list_friend_suggest = self.fb_mt.get_list_friend_suggest(cookie)
		if list_friend_suggest=={}:
			print('\t[KHÔNG CÓ BẠN BÈ GỢI Ý]')
		else:
			sl = len(list_friend_suggest)
			print(f'\n[BẮT ĐẦU GỬI LỜI MỜI KB ĐẾN {sl} NGƯỜI]\n')
			for id_friend in list_friend_suggest:
				link = list_friend_suggest[id_friend]
				self.fb_mt.friend_request(cookie, link)
				print(f'\t[{self.setting.time_now()}] ID:{id_friend}', end=' ')
				s = random.randint(5,10)
				print(f'[wait {s}s]')
				sleep(s)

	def auto_accept_friend_request(self, cookie):
		print('\n[AUTO CHẤP NHẬN KB]')
		list_friend_request = self.fb_mt.get_list_friend_request(cookie)
		if list_friend_request=={}:
			print('[KHÔNG CÓ LỜI MỜI KB]')
		else:
			sl = len(list_friend_request)
			print(f'[BẮT ĐẦU CHẤP NHẬN {sl} LỜI MỜI]\n')
			for id_friend in list_friend_request:
				link = list_friend_request[id_friend]
				self.fb_mt.friend_request(cookie, link)
				print(f'\t[{self.setting.time_now()}] ID: {id_friend}', end=' ')
				s = random.randint(5,10)
				print(f'[wait {s}s]')
				sleep(s)

	def auto_comment_reaction(self, cookie):
		sl = random.randint(5, 10)
		print(f'\n[AUTO COMMENT & REACTON ({sl})]')
		list_reaction = ['LIKE', 'LOVE', 'THUONGTHUONG', 'HAHA', 'WOW']
		list_cmt = open('comment.txt', 'r', encoding='utf8').read().split('|')
		cout = 1
		check_block = {'reaction': False, 'comment': False}
		list_story = []
		list_story_old = []

		while True:
			while True:
				if len(list_story)>0: break
				list_story = self.fb_mt.get_list_story(cookie)
			token = self.fb_mt.get_token(cookie)
			for id_status in list_story:
				if id_status in list_story_old: continue
				list_story_old.append(id_status)
				check = self.fb_mt.get_info_story(token, id_status)
				if check==False: continue
				name = check[0]
				caption = check[1]
				print(f'+BÀI VIẾT {cout}:{name}|{caption}')
				if check_block['reaction']==False:
					reaction = random.choice(list_reaction)
					check = self.fb_mt.reaction_story(cookie, token, id_status, reaction)
					if check==1: print(f'\t[{self.setting.time_now()}] [reaction]: {reaction}')
					elif check==2:
						print('\t[BLOCK REACTON]')
						check_block['reaction'] = True
					elif check==3:
						print('\t[COOKIE DIE]')
						return 0
					elif check==0: print('\t[REACTON FAILED]')	
				sleep(3)
				if check_block['comment']==False:
					content = random.choice(list_cmt)
					content = content.replace('#', name)
					check = self.fb_mt.comment_story(token, id_status, content)
					if check==1: print(f'\t[{self.setting.time_now()}] [comment]: {content}')
					elif check==2:
						print('\t[BLOCK COMMENT]')
						check_block['comment'] = True
					elif check==3:
						print('\t[COOKIE DIE]')
						return 0
					elif check==0: print('\t[COMMENT FAILED]')	
				cout+=1

				if cout>sl:
					print("[HOÀN THÀNH COMMENT & REACTON]")
					return 0

				if check_block['comment']==True and check_block['reaction']==True:
					print("[BLOCK ALL]")
					return 0
				s = random.randint(10, 15)
				print(f"[wait {s}s]")
				sleep(s)
			list_story = []

	def process(self, list_vt):
		for vt in list_vt:
			vt=int(vt)
			name = self.list_nick[vt]['name']
			cookie = self.list_nick[vt]['cookie']
			self.fb_mt.get_save_info(name, cookie)
			self.fb_mt.show_info(name)
			
			self.auto_comment_reaction(cookie)
			sleep(10)
			self.auto_post_photos(cookie)
			sleep(10)
			self.auto_accept_friend_request(cookie)
			sleep(10)
			self.auto_send_friend_suggest(cookie)
			print(f"***XONG: {name}")
			print("\n[CHUYỂN NICK ]")
			sleep(10)

	def run(self):
		print("<><><><><><><><><><><>")
		print('\t+Windows(0)\n\t+Termux(1)')
		check = input('***Chạy trên: ')
		if check=='0': cl = 'cls'
		elif check=='1': cl = 'clear'
		while True:
			os.system(cl)
			self.setting.show_nick()
			print('[OPTION]')
			print('\t1.Chạy\n\t2.Chỉnh sửa\n\t3.Thêm\n\t4.Xóa\n<><><><><><><>')
			check = input("***Nhập lựa chọn: ")
			if check!='1':
				if check!='2':
					if check=='4':
						while True:
							try:
								vt = int(input("+Chọn nick cần xóa: "))
								self.setting.delete_nick(vt)
								print("\t[Xóa thành công!!!]")
								op = input('Xóa nữa không(y/n):')
								if op!='y': break
							except: break
					elif check=='3':
						while True:
							try:
								name = input("+name: ")
								cookie = input("+cookie: ")
								tool.setting.add_nick(name, cookie)
								print("\t[Thêm thành công!!!]")
								op = input('Thêm nữa không(y/n):')
								if op!='y': break
							except: break
					os.system(cl)
					self.setting.show_nick()
				elif check=='2':
					while True:
						try:
							vt = int(input("+Chọn nick cần sửa: "))
							cookie = input("Cookie: ")
							self.setting.edit_nick(vt, cookie)
							print("\t[Sửa thành công!!!]")
							op = input('Có muốn sửa nữa không(y/n):')
							if op!='y': break
						except: break
					os.system(cl)
					self.setting.show_nick()
			elif check=='1':
				# print('[SETTING]')
				self.list_nick = self.setting.load_file_json('data/nicks.json')
				list_vt = input('>>>>>Nhập nick chạy: ').split(' ')
				print('[START]')
				self.process(list_vt)
				print("[Kết thúc tool]")
				return 0

if __name__ == '__main__':
	tool = Tool_feed_fb()
	tool.run()