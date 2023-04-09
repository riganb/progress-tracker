import requests
from requests_html import HTMLSession
import re
from urllib.parse import urlparse
import hashlib

request_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'}

def gfg_question_details(url, url_obj, html):
	pid, platform, plink = 1, 'GeeksForGeeks', 'https://practice.geeksforgeeks.org'
	html_text = html.html
	qname = html.find('title', first=True).text.split(' | ')[0]
	qlink = '/'.join(['https:/', *url.split('/')[2:5], '1'])
	hashcode = calc_hashcode(qlink)
	difficulty = re.search(r'"difficulty":"(.*?)"', html_text).group(1)
	topics = re.search(r'"topic_tags"\:\s?\[(.*?)\]', html.text).group(1).replace('"', '').split(',')
	qdata = {'qid': hashcode, 'qname': qname, 'qlink': qlink, 'pid': pid, 'platform': platform, 'plink': plink, 'difficulty': difficulty, 'topics': topics}
	return qdata

def leetcode_question_details(url, url_obj, html, text):
	pid, platform, plink = 2, 'LeetCode', 'https://leetcode.com'
	qlink = '/'.join(['https:/', *url.split('/')[2:5]])
	hashcode = calc_hashcode(qlink)
	qname = html.find('title', first=True).text[:-11]
	difficulty = 'Easy'
	ne, nm, nh = text.find('Easy'), text.find('Medium'), text.find('Hard')
	if nm < nh and nm < ne:
		difficulty = 'Medium'
	elif nh < nm and nh < ne:
		difficulty = 'Hard'
	topics = [re.findall(r'"name":"(\w+)","slug":', text)[0],]
	qdata = {'qid': hashcode, 'qname': qname, 'qlink': qlink, 'pid': pid, 'platform': platform, 'plink': plink, 'difficulty': difficulty, 'topics': topics}
	return qdata

def calc_hashcode(link):
	hash_str = '/'.join([*link.split('/')[2:5]])
	return hashlib.sha1(hash_str.encode('utf-8')).hexdigest()

def question_details(URL: str):
	try:
		session = HTMLSession()
		response = session.get(URL, headers=request_headers)
		html = response.html
		text = response.text
		url_obj = urlparse(URL)
		if url_obj.netloc == 'practice.geeksforgeeks.org':
			return gfg_question_details(URL, url_obj, html)
		elif url_obj.netloc == 'leetcode.com':
			return leetcode_question_details(URL, url_obj, html, text)
		elif re.fullmatch(r"https://.*?\..+?/.+", URL) != None:
			return 'Error! Possible reason: Platform not available.'
		else:
			print('crc', url_obj.netloc)
			return 'Error! Possible reason: Invalid link, enter complete URL.'
	except:
		return 'Error! Possible reason: Broken or invalid link.'


# question_details("https://leetcode.com/problems/two-sum/")
# question_details("https://leetcode.com/problems/string-to-integer-atoi/")
# question_details("https://leetcode.com/problems/palindrome-number/")

# question_details('https://practice.geeksforgeeks.org/problems/first-element-to-occur-k-times5150/1?page=1&curated[]=1&sortBy=submissions')

