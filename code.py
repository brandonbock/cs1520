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





class Matches(webapp2.RequestHandler):
	def get(self):

		members=User.query().fetch()
		currUser = users.get_current_user()
		q=User.query(ndb.GenericProperty("email") == currUser.email()).fetch(1)

	#	q = User.query(all()
		#q.filter("emai; =", "Smith")
		
 		posts=InstantPost.query().fetch()
		template_values = {
        'fname': range(1),
        'lname': range(7),
        'members': members,
        'curruser': currUser,
        'currStats' : q,
        'posts': posts,
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
		else:
			url = users.create_login_url()
			self.redirect(url)
		members=User.query().fetch()
		template_values = {
        'fname': range(1),
        'lname': range(7),
        'members': members,
    }

		render_template(self,'index.html',template_values)

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
		user.skill_level=self.request.get('skill')


		
		user.put()
		



		self.redirect('portfolio')
		
		
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
		render_template(self,'newsletter.html','')

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
		user = users.get_current_user()	
		if user:
			email = user.email()
			post = InstantPost()
			post.message_text = text
			post.user = email
			post.time = (int)(time.time())
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
	'''

class HandleMessage(webabb2.RequestHandler):
	def post(self):
		text = self.request.get('text')
		user = users.get_current_user()
		if user:
			email = user.email()
			post = InstantPost()
			post.message_text = text;
			post.user = email
			post.time = int(time.time())
			post.put()

			self.response.out.write('OK')

		else:
			self.out.write('You are not LOGGED in') '''

class Login(webapp2.RequestHandler):
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
	('/portfolio',Matches),
	('/login',Login),
	('/goals',Goals),
	#('/sendmsg',HandleMessage),
	('/sendmsg',HandleAjax),
	('/messages',MessageXml),
	('/ajax',Ajax),
	('/su',ConfirmUserSignup),
	('/newsletter',Newsletter)
	
	


	],debug=True)