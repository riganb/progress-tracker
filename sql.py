import sqlite3

class Database:
	tables = ["platform", "user", "question", "attempt", "stats"]
	schemas = {"platform": "pid INTEGER(3), pname VARCHAR(33), url VARCHAR(50), PRIMARY KEY(pid)",
	"user": "uid INTEGER(3), uname VARCHAR(33), age INTEGER(2), desg VARCHAR(15), mail VARCHAR(33)",
	"question": "qid VARCHAR(100), qname VARCHAR(100), qlink VARCHAR(100), pid REFERENCES platform(pid), difficulty VARCHAR(20), categories VARCHAR(200), points INTEGER, PRIMARY KEY(qid)",
	"attempt": "uid REFERENCES user(uid), qid references question(qid), solved VARCHAR(3), PRIMARY KEY(uid, qid)",
	"stats": "entity VARCHAR(55) PRIMARY KEY, total INTEGER(7)"}

	table_headings = {"platform": ["P_ID", "NAME", "LINK"],
	"user": ["U_ID", "NAME", "AGE", "DESIGNATION", "MAIL"],
	"question": ["Q_ID", "NAME", "PNAME", "LEVEL", "CATEGORIES"],
	"attempt": ["U_ID", "U_NAME", "Q_ID", "Q_NAME", "SOLVED"],
	"stats": ["ENTITY", "TOTAL COUNT"]}

	score_chart = [[["School", "Basic", "Easy"], 1, 'warning'], [["Medium"], 3, 'success'], [["Hard"], 5, 'danger']]

	#*for creation of tables
	def __init__(self, fname):
		self.conn = sqlite3.connect(fname, check_same_thread=False)
		self.curr = self.conn.cursor()
		self.existing_tables = set(tname[0] for tname in self.curr.execute("SELECT name FROM sqlite_master WHERE TYPE='table'"))
		for table in self.tables:
			if table not in self.existing_tables:
				self.curr.execute(f"CREATE TABLE {table}({self.schemas[table]})")
		
		##?update total count for all properties
		self.curr.execute(f"INSERT OR IGNORE INTO stats VALUES('Users', (SELECT COUNT(*) FROM user))")
		self.curr.execute(f"INSERT OR IGNORE INTO stats VALUES('Platforms', (SELECT COUNT(*) FROM platform))")
		self.curr.execute(f"INSERT OR IGNORE INTO stats VALUES('Questions', (SELECT COUNT(*) FROM question))")
		self.curr.execute(f"INSERT OR IGNORE INTO stats VALUES('Attempts', (SELECT COUNT(*) FROM attempt))")
		self.conn.commit()

		#?can change the following statements into a loop for inserting more platforms
		self.curr.execute(f"INSERT OR IGNORE INTO platform VALUES('001', 'GeeksForGeeks', 'https://practice.geeksforgeeks.org/')")
		self.curr.execute(f"INSERT OR IGNORE INTO platform VALUES('002', 'LeetCode', 'https://leetcode.com/')")
		self.conn.commit()

		#*this function is being used to check for and create triggers
		self.make_triggers()

	def get_headings(self, table_name):
		return self.table_headings[table_name]
	
	def insert_platform(self, data):
		if data["pid"] == "":
			return False
		try:
			self.curr.execute(f"INSERT INTO platform VALUES('{data['pid']}', '{data['pname']}', '{data['url']}')")
			self.conn.commit()
			return True
		except:
			return False
	
	def get_platforms(self):
		return self.curr.execute("SELECT * FROM platform").fetchall()
	
	#TODO: for later, will stay disabled for now
	#?for deleting questions and totalscores under this, loop through qids using delete_question function and call delete_totalscore_by_pid for deleting totalscores for the given pid
	def del_platform(self, pid):
		try:
			self.curr.execute(f"DELETE FROM user WHERE pid='{pid}'")
			#?delete questions using qid's under this platform
			qids = self.curr.execute(f"SELECT qid FROM question WHERE pid='{pid}'").fetchall()
			for qid in qids:
				self.del_question(qid[0])
			self.conn.commit()
			return True
		except:
			return False
	
	def insert_user(self, data):
		if data["uid"] == "":
			return False
		users = self.get_users()
		for user in users:
			print(user[0])
			if data["uid"] == str(user[0]):
				return False
		try:
			#TODO trigger to create rows in totalscore for every platform with this user with score set to 0
			
			self.curr.execute(f"INSERT INTO user VALUES('{data['uid']}', '{data['uname']}', '{data['age']}', '{data['desg']}', '{data['mail']}')")
			self.conn.commit()
			return True
		except:
			return False

	def get_users(self):
		return self.curr.execute("SELECT * FROM user").fetchall()
	
	def del_user(self, uid):
		try:
			self.curr.execute(f"DELETE FROM user WHERE uid='{uid}'")
			self.del_attempt_by_uid(uid)
			self.del_totalscore_by_uid(uid)
			return True
		except:
			return False

	def insert_question(self, data):
		try:
			print(data)
			diff = data['difficulty']
			points = 5 if diff == 'Hard' else (3 if diff == 'Medium' else 1)
			self.curr.execute(f"INSERT INTO question VALUES('{data['qid']}', '{data['qname']}', '{data['qlink']}', '{data['pid']}', '{diff}', '{', '.join(data['topics'])}', '{points}')")
			self.conn.commit()
			return True
		except:
			return False
	
	def get_questions(self):
		return self.curr.execute("SELECT q.*, pname, p.url FROM question q JOIN platform p WHERE q.pid = p.pid").fetchall()
	
	def del_question(self, qid):
		try:
			self.del_attempt_by_qid(qid)
			self.curr.execute(f"DELETE FROM question WHERE qid='{qid}'")
			self.conn.commit()
			return True
		except:
			return False
	
	def question_exists(self, qid):
		questions = self.curr.execute("SELECT * FROM question").fetchall()
		for question in questions:
			if qid == question[0]:
				return True
		return False
	
	#TODO: use this for updation as well
	#?refer to https://sebhastian.com/mysql-insert-if-not-exists/ for clarification on using REPLACE instead of INSERT
	def insert_or_update_attempt(self, data):
		try:
			self.curr.execute(f"REPLACE INTO attempt VALUES('{data['uid']}', '{data['qid']}', '{data['solved']}')")
			self.conn.commit()
			return True
		except:
			return False

	def get_attempts(self):
		attempts = self.curr.execute("SELECT * FROM attempt ORDER BY uid, qid").fetchall()
		att_list = list()
		for attempt in attempts:
			uid, qid, solved = attempt[0], attempt[1], attempt[2]
			uname = self.curr.execute(f"SELECT uname FROM user WHERE uid={uid}").fetchone()[0]
			qname, qlink = self.curr.execute(f"SELECT qname, qlink FROM question WHERE qid='{qid}'").fetchone()
			colour, alt = ['success', 'danger'] if solved == 'Yes' else ['danger', 'success']
			update_val = 'No' if solved == 'Yes' else 'Yes'
			att_list.append([uid, uname, qid, qname, qlink, solved, colour, alt, update_val])
		return att_list

	def del_attempt(self, uid, qid):
		try:
			self.curr.execute(f"DELETE FROM attempt WHERE uid='{uid}' AND qid='{qid}'")
			self.conn.commit()
			return True
		except:
			return False

	def del_attempt_by_uid(self, uid):
		try:
			self.curr.execute(f"DELETE FROM attempt WHERE uid='{uid}'")
			self.conn.commit()
			return True
		except:
			return False

	def del_attempt_by_qid(self, qid):
		try:
			self.curr.execute(f"DELETE FROM attempt WHERE qid='{qid}'")
			self.conn.commit()
			return True
		except:
			return False

	def get_stats(self):
		return self.curr.execute("SELECT * FROM stats").fetchall()
	
	def get_scorechart(self):
		return self.score_chart

	trig_names = ['que_i', 'que_d', 'usr_i', 'usr_d', 'pfm_i', 'pfm_d', 'att_i', 'att_d']
	#* 'on_attempt_create', 'on_attempt_update'
	triggers = {'que_i':'''CREATE TRIGGER que_i
AFTER INSERT ON question
BEGIN
    UPDATE stats SET total = total + 1 WHERE entity = 'Questions';
END;''',
    'que_d':'''CREATE TRIGGER que_d
AFTER DELETE ON question
BEGIN
    UPDATE stats SET total = total - 1 WHERE entity = 'Questions';
END;''',
    'usr_i':'''CREATE TRIGGER usr_i
AFTER INSERT ON user
BEGIN
    UPDATE stats SET total = total + 1 WHERE entity = 'Users';
END;''',
    'usr_d':'''CREATE TRIGGER usr_d
AFTER DELETE ON user
BEGIN
    UPDATE stats SET total = total - 1 WHERE entity = 'Users';
END;''',
    'pfm_i':'''CREATE TRIGGER pfm_i
AFTER INSERT ON platform
BEGIN
    UPDATE stats SET total = total + 1 WHERE entity = 'Platforms';
END;''',
    'pfm_d':'''CREATE TRIGGER pfm_d
AFTER DELETE ON platform
BEGIN
    UPDATE stats SET total = total - 1 WHERE entity = 'Platforms';
END;''',
    'att_i':'''CREATE TRIGGER att_i
AFTER INSERT ON attempt
BEGIN
    UPDATE stats SET total = (SELECT COUNT(*) FROM attempt) WHERE entity = 'Attempts';
END;''',
    'att_d':'''CREATE TRIGGER att_d
AFTER DELETE ON attempt
BEGIN
    UPDATE stats SET total = (SELECT COUNT(*) FROM attempt) WHERE entity = 'Attempts';
END;'''}

	def make_triggers(self):
		existing_trigs = self.curr.execute("SELECT name from sqlite_master WHERE TYPE='trigger'").fetchall()
		existing_trigs = set([trig[0] for trig in existing_trigs])
		for trig in self.trig_names:
			if trig not in existing_trigs:
				self.curr.execute(self.triggers[trig])
		self.conn.commit()
		pass

