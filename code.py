import webapp2
import os
import datetime
import time
import json
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.api import mail

class ConfirmUserSignup(webapp2.RequestHandler):
    def post(self):
        user_address = self.request.get('addr')
        sender_address = "jybra1520@gmail.com"
        subject = "Confirm your registration"
        body = "Thank you for signinup"

        mail.send_mail(sender_address, user_address, subject, body)


def render_template(handler, templatename,templatevalues):
	path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
	html = template.render(path,templatevalues)
	handler.response.out.write(html)

class User(ndb.Model):
	registered = ndb.IntegerProperty()
	email = ndb.StringProperty()
	fname=ndb.StringProperty()
	lname=ndb.StringProperty()	
	gender=ndb.StringProperty()
	bMonth=ndb.StringProperty()
	bDay=ndb.StringProperty()
	bYear=ndb.StringProperty()
	habit_weight=ndb.StringProperty()
	habit_cardio=ndb.StringProperty()
	habit_abs=ndb.StringProperty()
	habit_upperbody=ndb.StringProperty()
	habit_treadmill=ndb.StringProperty()
	habit_yoga=ndb.StringProperty()
	goal_gain=ndb.StringProperty()
	goal_lose=ndb.StringProperty()
	goal_enduarance=ndb.StringProperty()
	time_mon=ndb.StringProperty()
	time_tue=ndb.StringProperty()
	time_wed=ndb.StringProperty()
	time_thu=ndb.StringProperty()
	time_fri=ndb.StringProperty()
	time_sat=ndb.StringProperty()
	time_sun=ndb.StringProperty()
	skill_level=ndb.IntegerProperty()
	matchingpoints=ndb.IntegerProperty()





class Matches(webapp2.RequestHandler):
	def get(self):

		#members=User.query().fetch()
		
		currUser = users.get_current_user()

		
		q=User.query(ndb.GenericProperty("email") == currUser.email()).fetch(1)
		log=User.query(ndb.GenericProperty("email") == currUser.email()).fetch(1)

		x=int(log[0].skill_level)
		upbound=x+15
		lowbound=x-15

		mem=User.query();
		for m in mem:
			if(m.email is log[0].email):
				continue
			points=int (0);
			if m.habit_weight==log[0].habit_weight:
				points=points+10
			if m.habit_yoga==log[0].habit_yoga:
				points=points+10
			if m.habit_cardio==log[0].habit_cardio:
				points=points+10
			if m.habit_abs==log[0].habit_abs:
				points=points+10
			if m.habit_upperbody==log[0].habit_upperbody:
				points=points+10
			if m.habit_treadmill==log[0].habit_treadmill:
				points=points+10
			if m.goal_lose==log[0].goal_lose:
				points=points+30
			if m.goal_gain==log[0].goal_gain:
				points=points+30
			if m.goal_enduarance==log[0].goal_enduarance:
				points=points+30
			
			if m.time_mon==log[0].time_mon:
				points=points+5
			if m.time_tue==log[0].time_tue:
				points=points+5
			if m.time_wed==log[0].time_wed:
				points=points+5
			if m.time_thu==log[0].time_thu:
				points=points+5
			if m.time_fri==log[0].time_fri:
				points=points+5
			if m.time_sat==log[0].time_sat:
				points=points+5
			if m.time_sun==log[0].time_sun:
				points=points+5
			if m.skill_level>lowbound and m.skill_level<upbound:
				points=points+65
			if m.email==log[0].email:
				points=-10000
			m.matchingpoints= int(points)
			m.put();
			#max points is 250 points
		
		#members=User.query(ndb.GenericProperty("email") != currUser.email() )
		#and ndb.GenericProperty("skill_level")<upbound and ndb.GenericProperty("skill_level")>lowbound
		members=User.query().order(-User.matchingpoints)
		members=members.fetch(5)
		for m in members:
			if m.email == log[0].email:
				members.remove(m)
		link = ""
		link_text = ""
		user = users.get_current_user()
		if user:
			link = users.create_logout_url(self.request.uri)
			link_text = 'Logout'
		else:
			link = users.create_login_url(self.request.uri)
			link_text = 'Login'
	#	q = User.query(all()
		#q.filter("emai; =", "Smith")
		
 		posts=InstantPost.query().fetch()
		template_values = {
        'fname': range(1),
        'lname': range(7),
        'members': members,
        #'members': list_user,
        'curruser': currUser,
        'currStats' : q,
        'posts': posts,
        'loggedin': log[0],
        'link': link,
        'link_text' : link_text
    }

		render_template(self,'portfolio.html',template_values)


class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url = users.create_logout_url('/')
			#self.out.response.write('<html><body>')
			#self.out.response.write({{user.email}})
			self.response.out.write('<html><body>')
			
			self.response.out.write('Hello, ' + user.email() +  'Click <a href="')
			self.response.out.write(url)
			self.response.out.write('">here</a> to log out.')
			self.response.out.write('</body></html>')

			members=User.query().fetch()
			currUser=User.query(ndb.GenericProperty("email") == user.email()).fetch(1)

			if len(currUser) is 1:
				self.response.out.write('n if')
				if currUser[0].registered is 1:
					self.redirect('portfolio')
		
			template_values = {
        	'fname': range(1),
        	'lname': range(7),
        	'members': members,
   		 	}

			render_template(self,'index.html',template_values)
		else:
			url = users.create_login_url()
			self.redirect(url)
		

		

class Goals(webapp2.RequestHandler):
	def get(self):
		posts=InstantPost.query().fetch()
		template_values = {
		'posts': posts,
        'fname': 'b',
        'lname': 'a'

    }
		render_template(self,'goals.html',template_values)


class ProcessForm(webapp2.RequestHandler):
	def post(self):
		user=User()
		currUser = users.get_current_user()

		#bio
		user.email = currUser.email()
		user.fname=self.request.get('fname')
		user.lname=self.request.get('lname')
		user.gender=self.request.get('gender')
		user.bMonth=self.request.get('month')
		user.bDay=self.request.get('day')
		user.bYear=self.request.get('year')

		#Work habit
		user.habit_weight=self.request.get("weight", default_value="no")
		user.habit_cardio=self.request.get("cardio", default_value="no")
		user.habit_abs=self.request.get("abs", default_value="no")
		user.habit_upperbody=self.request.get("upperbody", default_value="no")
		user.habit_treadmill=self.request.get("treadmill", default_value="no")
		user.habit_yoga=self.request.get("yoga", default_value="no")

		#Workout goals
		user.goal_gain=self.request.get("gainMuscle", default_value="no")
		user.goal_lose=self.request.get("loseweight", default_value="no")
		user.goal_enduarance=self.request.get("enduarance", default_value="no")

		#Workout time
		user.time_mon=self.request.get("mon", default_value="no")
		user.time_tue=self.request.get("tue", default_value="no")
		user.time_wed=self.request.get("wed", default_value="no")
		user.time_thu=self.request.get("thu", default_value="no")
		user.time_fri=self.request.get("fri", default_value="no")
		user.time_sat=self.request.get("sat", default_value="no")
		user.time_sun=self.request.get("sun", default_value="no")

		#skill level
		user.skill_level=int(self.request.get('skill'))
		user.registered = 1;

		
		user.put()
		



		self.redirect('portfolio')

class EditForm(webapp2.RequestHandler):
	def post(self):
		
		currUser = users.get_current_user()
		user=User.query(ndb.GenericProperty("email") == currUser.email()).fetch(1)
		#self.response.out.write(user[0].fname)
		#user[0].fname = "a"
		#user[0].put()
		#bio
		#Work habit
		user[0].habit_weight=self.request.get("weight", default_value="no")
		user[0].habit_cardio=self.request.get("cardio", default_value="no")
		user[0].habit_abs=self.request.get("abs", default_value="no")
		user[0].habit_upperbody=self.request.get("upperbody", default_value="no")
		user[0].habit_treadmill=self.request.get("treadmill", default_value="no")
		user[0].habit_yoga=self.request.get("yoga", default_value="no")

		#Workout goals
		user[0].goal_gain=self.request.get("gainMuscle", default_value="no")
		user[0].goal_lose=self.request.get("loseweight", default_value="no")
		user[0].goal_enduarance=self.request.get("enduarance", default_value="no")

		#Workout time
		user[0].time_mon=self.request.get("mon", default_value="no")
		user[0].time_tue=self.request.get("tue", default_value="no")
		user[0].time_wed=self.request.get("wed", default_value="no")
		user[0].time_thu=self.request.get("thu", default_value="no")
		user[0].time_fri=self.request.get("fri", default_value="no")
		user[0].time_sat=self.request.get("sat", default_value="no")
		user[0].time_sun=self.request.get("sun", default_value="no")

		#skill level
		user[0].skill_level=int(self.request.get('skill'))
		user[0].registered = 1; 
		user[0].put()
		#user.put()

		q=User.query(ndb.GenericProperty("email") == currUser.email()).fetch(1)
		log=User.query(ndb.GenericProperty("email") == currUser.email()).fetch(1)

		x=int(log[0].skill_level)
		upbound=x+15
		lowbound=x-15

		mem=User.query();
		for m in mem:
			points=int (0);
			if m.habit_weight==log[0].habit_weight:
				points=points+10
			if m.habit_yoga==log[0].habit_yoga:
				points=points+10
			if m.habit_cardio==log[0].habit_cardio:
				points=points+10
			if m.habit_abs==log[0].habit_abs:
				points=points+10
			if m.habit_upperbody==log[0].habit_upperbody:
				points=points+10
			if m.habit_treadmill==log[0].habit_treadmill:
				points=points+10
			if m.goal_lose==log[0].goal_lose:
				points=points+30
			if m.goal_gain==log[0].goal_gain:
				points=points+30
			if m.goal_enduarance==log[0].goal_enduarance:
				points=points+30
			
			if m.time_mon==log[0].time_mon:
				points=points+5
			if m.time_tue==log[0].time_tue:
				points=points+5
			if m.time_wed==log[0].time_wed:
				points=points+5
			if m.time_thu==log[0].time_thu:
				points=points+5
			if m.time_fri==log[0].time_fri:
				points=points+5
			if m.time_sat==log[0].time_sat:
				points=points+5
			if m.time_sun==log[0].time_sun:
				points=points+5
			if m.skill_level>lowbound and m.skill_level<upbound:
				points=points+65
			if m.email==log[0].email:
				points=-10000
			m.matchingpoints= int(points)
			m.put();
			#max points is 250 points
		
		#members=User.query(ndb.GenericProperty("email") != currUser.email() )
		#and ndb.GenericProperty("skill_level")<upbound and ndb.GenericProperty("skill_level")>lowbound
		members=User.query().order(-User.matchingpoints)

		members=members.fetch(5)
		link = ""
		link_text = ""
		user = users.get_current_user()
		if user:
			link = users.create_logout_url(self.request.uri)
			link_text = 'Logout'
		else:
			link = users.create_login_url(self.request.uri)
			link_text = 'Login'
	#	q = User.query(all()
		#q.filter("emai; =", "Smith")
		
 		posts=InstantPost.query().fetch()
		template_values = {
        'fname': range(1),
        'lname': range(7),
        'members': members,
        #'members': list_user,
        'curruser': currUser,
        'currStats' : q,
        'posts': posts,
        'loggedin': log[0],
        'link': link,
        'link_text' : link_text
    }

		render_template(self,'portfolio.html',template_values)

		



		#self.redirect('portfolio')

		
		

		
		
class HandleMessage(webapp2.RequestHandler):
	def post(self):
		text = self.request.get('text')
		user = users.get_current_user()
		if user:
			email = user.email()
			post = InstantPost()
			post.message_text = text
			post.user = email
			post.time = (int)(time.time())
			post.put()

			self.response.out.write('OK')

		else:
			self.response.out.write('You are not logged in brah')
class Newsletter(webapp2.RequestHandler):
	def get(self):
		#data=Weight.query().fetch()
		prof = self.request.get('email')
		q=User.query(ndb.GenericProperty("email") == prof).fetch(1)
		link = ""
		link_text = ""
		user = users.get_current_user()
		if user:
			link = users.create_logout_url(self.request.uri)
			link_text = 'Logout'
		else:
			link = users.create_login_url(self.request.uri)
			link_text = 'Login'
		log=User.query(ndb.GenericProperty("email") == user.email()).fetch(1)
		data=Weight.query(ndb.GenericProperty("email") == prof).fetch()
		goal=WeightGoal.query(ndb.GenericProperty("email") == prof).fetch()
		
		#q=User.query(ndb.GenericProperty("email") == currUser.email()).fetch(1)
		data.sort(key=lambda r: r.date)
		goal.sort(key=lambda r: r.date)
		#posts=InstantPost.query().fetch()
		posts=InstantPost.query(ndb.GenericProperty("profile") == prof).fetch()
		template_values = {
        'data': data,
        'goal':goal,
        'posts':posts,
        'prof': q[0],
        'curr': " ",
        'loggedin': log[0],
        'link_text':link_text,
        'link' : link,
        'b': "a",

    }

		render_template(self,'progress.html',template_values)

class Ajax(webapp2.RequestHandler): 
	def get(self):
		render_template(self,'ajax.html', '')
class MessageXml(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		messages = list()
		if user:
			query = InstantPost.query()
			query.order(-InstantPost.time)
			#q=User.query(ndb.GenericProperty("email") == currUser.email()).fetch(1)
			messages = query.fetch(40)

		template_values = {
				'messages': messages
			}
		self.response.headers["Content-Type"] = "text/xml"
		render_template(self,'messages.xml',template_values)



class HandleAjax(webapp2.RequestHandler):
	
	def post(self):
		#urlsafe = self.request.get("text")
		text = self.request.get('text')
		author = self.request.get('author')
		profile = self.request.get('profile')
		user = users.get_current_user()	
		if user:
			email = user.email()
			post = InstantPost()
			post.message_text = text
			post.user = email
			post.time = (int)(time.time())
			post.author = author
			post.profile = profile
			post.put()	
		#ui = ndb.Key(urlsafe=urlsafe).get()
		obj={
			'user' : "a",
			'goal': text
		}
		self.response.write(json.dumps(obj))


class InstantPost(ndb.Model):
	message_text = ndb.StringProperty()
	user = ndb.StringProperty()
	time = ndb.IntegerProperty()
	author = ndb.StringProperty()
	authorEmail = ndb.StringProperty()
	profile = ndb.StringProperty()

class Weight(ndb.Model):
	Year = ndb.IntegerProperty()
	Month = ndb.IntegerProperty()
	Day = ndb.IntegerProperty()
	Value = ndb.IntegerProperty()
	prop = ndb.StringProperty()
	date = ndb.DateTimeProperty()
	email = ndb.StringProperty()

class WeightGoal(ndb.Model):
	Year = ndb.IntegerProperty()
	Month = ndb.IntegerProperty()
	Day = ndb.IntegerProperty()
	Value = ndb.IntegerProperty()
	prop = ndb.StringProperty()
	date = ndb.DateTimeProperty()
	email = ndb.StringProperty()

class EditProfile(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		q=User.query(ndb.GenericProperty("email") == user.email()).fetch(1)
		link = ""
		link_text = ""
		user = users.get_current_user()
		if user:
			link = users.create_logout_url(self.request.uri)
			link_text = 'Logout'
		else:
			link = users.create_login_url(self.request.uri)
			link_text = 'Login'


		if user:
			mail = user.email()
			template_values = {
        	'currStats' : q[0],
        	#'loggedin': log[0],
        	'link': link,
        	'link_text' : link_text,
        	'loggedin' : q[0]
    		}
			render_template(self,'edit.html',template_values)

class AddWeight(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		text = self.request.get('text')
		arr = text.split(',')
		for i in range(len(arr)-1):
			if not arr:
				break
			actual = arr.pop(0)
			if not arr:
				break
			date = arr.pop(0)
			if not arr:
				break
			value = arr.pop(0)
			if(actual == "true"):
				weight = Weight()
				weight.Value = int(value)
				lst = date.split("/")
				weight.Month = int(lst.pop(0)) -1
				weight.Day = int(lst.pop(0)) 
				weight.Year = int(lst.pop(0))
				weight.date = datetime.datetime(weight.Year, weight.Month, weight.Day, 13, 34, 5, 787000)
				weight.email = user.email()
				#weight.Value = value
				weight.put()
			elif(actual == "false"):
				weight = WeightGoal()
				weight.Value = int(value)
				lst = date.split("/")
				weight.Month = int(lst.pop(0)) 
				weight.Day = int(lst.pop(0)) 
				weight.Year = int(lst.pop(0))
				weight.date = datetime.datetime(weight.Year, weight.Month, weight.Day, 13, 34, 5, 787000)
				weight.email = user.email()
				#weight.Value = value
				weight.put()

			
		#val = newstr.split(",")
		#weight = Weight()
		#weight.prop = val.pop()
		#weight.put()
	user = users.get_current_user()
		#if user:
		#	weight = Weight()	
		#	weight.Year = 1
		#	weight.put()

class HandleMessage(webapp2.RequestHandler):
	def post(self):
		text = self.request.get('text')
		user = users.get_current_user()
		author = self.request.get('author')
		if user:
			email = user.email()
			post = InstantPost()
			post.message_text = text;
			post.user = email
			post.time = int(time.time())
			post.author = "i"
			post.put()

			self.response.out.write('OK')

		else:
			self.out.write('You are not LOGGED in') 

class Login(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url = users.create_logout_url('/')
			#self.out.response.write('<html><body>')
			#self.out.response.write({{user.email}})
			self.response.out.write('<html><body>')
			#href="/edit?uid=
			self.response.out.write('Hello, ' + user.email() +  'Click <a href="')
			self.response.out.write(url)
			self.response.out.write('">here</a> to log out.')
			self.response.out.write('</body></html>')
		else:
			url = users.create_login_url()
			self.response.out.write('<html><body>')
			self.response.out.write('Click <a href="')
			self.response.out.write(url)
			self.response.out.write('"here</a> to log in.')
			self.response.out.write('</body></html>')

app = webapp2.WSGIApplication([
	('/',MainPage),
	('/processform',ProcessForm),
	('/editform',EditForm),
	('/portfolio',Matches),
	('/login',Login),
	('/goals',Goals),
	#('/sendmsg',HandleMessage),
	('/sendmsg',HandleAjax),
	('/messages',MessageXml),
	('/ajax',Ajax),
	('/su',ConfirmUserSignup),
	('/newsletter',Newsletter),
	('/weight',AddWeight),
	('/edit',EditProfile)
	
	


	],debug=True)