import requests
import random
import re

def get_headers(cookie):
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

def get_token(headers):
		url = 'https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed'
		res = requests.get(url, headers=headers)
		token = re.findall(r'accessToken\\":\\"(.*?)\\', res.text)
		if token != []: token = token[0]
		else: token = ''
		return token

data = open('input/list_cap.txt', 'r', encoding='utf8').read()
list_cap = data.split('\n\n')
cap = random.choice(list_cap)
message = cap + '\n#bot_share_tus'

cookie = 'dpr=1.100000023841858; c_user=100050136994008; datr=UWOFX5VCtkc_YEq13Dc9Cuqy; _fbp=fb.1.1602682178940.582415060; sb=WgSHX0wTwwJ1Xz6fFerAJHUU; spin=r.1002841455_b.trunk_t.1602911755_s.1_v.2_; presence=EDvF3EtimeF1602935451EuserFA21B50136994008A2EstateFDutF0CEchF_7bCC; wd=1144x677; xs=21%3A1MLZv6_QO4gI0g%3A2%3A1598358489%3A323%3A6344%3A%3AAcUqCdI8KQQns70ug1mCXxUL3k2wPtiZRKbVTdVtLHck; fr=0R5b0fawyVFQrjNvt.AWUeZCbEj_mXFlnn7FWSTgxXr5E.Bffz5w.BJ.AAA.0.0.Bfiuix.AWWeN9dtfBI; useragent=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgNi4zKSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvODYuMC40MjQwLjc1IFNhZmFyaS81MzcuMzY%3D; _uafec=Mozilla%2F5.0%20(Windows%20NT%206.3)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F86.0.4240.75%20Safari%2F537.36; '
cookie = 'sb=oFZcXwoupq_Z9JZAd2rCXeVF; datr=pFZcX8k9VH-tO36ZmWs7mxQ2; _fbp=fb.1.1600530164517.249282921; wd=1280x913; c_user=100053313009669; spin=r.1002835993_b.trunk_t.1602861454_s.1_v.2_; xs=2%3Ath7A-cjVXlzuwQ%3A2%3A1602679425%3A17304%3A6269%3A%3AAcVfA9a58hlZC9rW6w8itHyV_OqpWx0RIJ4HO75VlGs; fr=0T5mVt96qsbxbK4sK.AWUB_scEuhyvE0FeCrXnPWZtj2U.BffznN.Jn.AAA.0.0.BfiuhB.AWWxsKx3QO0; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1602939574726%2C%22v%22%3A1%7D'
headers = get_headers(cookie)
token = get_token(headers)
# token = 'EAAAAZAw4FxQIBAKRHnmVINLGGpjcl43eTlnqT5Xoj9JFhz4PPagEeGvuegHRU7fQZBScdMYDrFxNSY3tJPeAZAMYVT2S8xrZBLDwCBbNAJuOwsKGFmkFWDXQ5O9zfWFXynYV777QS2cpN6PD24BJZBsSJA9lpQnI5w8OtTZBkHaWBsmiq6HzG89LXUo8P1Y2MZD'
params = {'access_token': token}

url = 'https://graph.facebook.com/me?fields=albums'
res = requests.get(url, params=params)
data = res.json()
list_albums = data['albums']['data']
for albums in list_albums:
	if albums['type'] == 'wall':
		id_albums = albums['id']
		# print(id_albums)
		break
print(data['albums']['data'])
url = f'https://graph.facebook.com/{id_albums}/photos'
payload = {'message': message, 'url':'https://source.unsplash.com/random'}
res = requests.post(url, data=payload, params=params)
print(res.json())

# print(cap)
# url = 'https://graph.facebook.com/762545077858317?fields=from, message'
# # url = 'https://graph.facebook.com/178856563844352?fields=from,message'

# res = requests.get(url, params=params)
# data = res.json()
# print(data)