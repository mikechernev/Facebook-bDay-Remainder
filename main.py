# coding=utf-8
import webapp2
import jinja2
import os
import json
import facebook
import datetime
import logging

from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.api import mail
from google.appengine.api import urlfetch
from models import Users, AllUsers, Settings

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

APP_ID = "387045461339078"
APP_SECRET = "f1a565c20eec03f66fbc01aee5f715a3"
MY_URL = "//facebookbirthdayreminder.appspot.com"

def force_utf8(string):
    if type(string) == str:
        return string
    return string.encode('utf-8')

def force_unicode(string):
    if type(string) == unicode:
        return string
    return string.decode('utf-8')

class MainPage(webapp2.RequestHandler):
    def get(self):
        scope = "email,friends_birthday,offline_access"
        template_values = {
            'appId': APP_ID,
            'appSecret': APP_SECRET,
            'myUrl': MY_URL, 
            'scope': scope
        }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class AjaxCall(webapp2.RequestHandler):
    def post(self):
        fb_user = facebook.get_user_from_cookie(self.request.cookies, APP_ID, APP_SECRET)
        if fb_user:
            access_token = fb_user['access_token']
            url = urlfetch.fetch("https://graph.facebook.com/me?access_token=" + access_token, method=urlfetch.GET, deadline=20)
            profile = json.loads(url.content)
            self.response.out.write("Welcome " + profile['name'])
            query = Users.all()
            query.filter("accessToken = ", access_token)
            if query.get():
                pass
            else:
                user = Users()
                user.facebookID = profile['id']
                user.email = db.Email(profile['email'])
                user.accessToken = access_token
                user.put()
                self.response.out.write("<br>You are now added to the database")
                taskqueue.add(url='/birthdays', params={"email": profile['email'], "access_token": access_token})

class ProcessUsers(webapp2.RequestHandler):
    def get(self):
        count = Users.all().count()
        
        if count > 0:
            users = Users.all().fetch(count)
            for user in users:
#        fb_user = facebook.get_user_from_cookie(self.request.cookies, APP_ID, APP_SECRET)
#        if fb_user:
#        access_token = fb_user['access_token']
#                access_token = "AAAFgBAs8K8YBAGgNcgyoZCJVDcj5ZBPVM3ZBmR3XkTgDsCeUSzdlU4NUb6ZAo2o6WE0jZBz8399hBL2TzYlXW8Hv3BKZCWahwZD"
                taskqueue.add(url='/processUsers', params={"access_token": user.accessToken})
        
    def post(self):
        access_token = self.request.get("access_token")
        url = urlfetch.fetch("https://graph.facebook.com/me/friends?access_token=" + access_token, method=urlfetch.GET, deadline=20)
        facebook_data = json.loads(url.content)
        try:
            facebook_data['data']
        except:
            try:
                facebook_data['error']
            except:
                pass
            else:
                if facebook_data['error']['code'] == 190 and facebook_data['error']['error_subcode'] == 463:
                    pass
                else:
                    pass
            logging.info(facebook_data)
        else:
            for friend in facebook_data['data']:
                if AllUsers.all().filter("facebookID = ", friend['id']).get():
                    pass
                else:
                    url = urlfetch.fetch("https://graph.facebook.com/" + friend['id'] + "?access_token=" + access_token, method=urlfetch.GET, deadline=20)
                    friend_info = json.loads(url.content)
                    user = AllUsers()
                    try:
                        friend_info['birthday']
                    except:
                        pass
                    else:
                        user.facebookID = friend_info['id']
                        user.name = friend_info['name']
                        user.birthday = int(friend_info['birthday'][:2]+friend_info['birthday'][3:5])
                        user.put()
        

class DisplayUsers(webapp2.RequestHandler):
    def get(self):
        count = Users.all().count()
        if count > 0:
            users = Users.all().fetch(count)
            for user in users:
                url = urlfetch.fetch("https://graph.facebook.com/me?access_token=" + user.accessToken, method=urlfetch.GET, deadline=20)
                profile = url.content
                self.response.out.write(profile+"<br>")
        else:
            self.response.out.write("No users")
            
class Birthdays(webapp2.RequestHandler):
    def get(self):
        count = Users.all().count()
        
        if count > 0:
            users = Users.all().fetch(count)
            for user in users:
                taskqueue.add(url='/birthdays', params={"email": user.email, "access_token": user.accessToken})
                
        else:
            self.response.out.write("No users")

    def post(self):        access_token = self.request.get("access_token")
        email = self.request.get("email")
        url = urlfetch.fetch("https://graph.facebook.com/me?access_token=" + access_token, method=urlfetch.GET, deadline=20)
        user_data = json.loads(url.content)
        url = urlfetch.fetch("https://graph.facebook.com/me/friends?access_token=" + access_token, method=urlfetch.GET, deadline=20)
        facebook_data = json.loads(url.content)
        message = mail.EmailMessage(sender="Bithdays Update<birtdayreminder-info@mikechernev.com>",
                                    subject="Your birthday fellas")
        message.to = email
        try:
            facebook_data['data']
        except:
            message.body = """
            Hi there,
            There seems to be a problem with your account.
            
            """
            try:
                facebook_data['error']
            except:
                message.body += "We'll try to resolve it as soon as possible"
            else:
                if facebook_data['error']['code'] == 190 and facebook_data['error']['error_subcode'] == 463:
                    message.body += "Your access token is invalid. In order to use the Birthday reminder you will have to subscribe again"
                else:
                    message.body += "We'll try to resolve it as soon as possible"
            logging.info(facebook_data)
            message.send()
            logging.info("Message sent to " + str(email))
            user = Users.all().filter("email = ", email)
            db.delete(user)
            logging.info("User with email - " + email + " deleted")
        else:
            url = urlfetch.fetch("https://graph.facebook.com/me?access_token=" + access_token, method=urlfetch.GET, deadline=20)
            user_data = json.loads(url.content)
            birthday_list = ""
            birtday_list_html = ""
            now = datetime.datetime.now()
            current_date = now.strftime("%m/%d")
            message.body = "Hi there,\n"
            message.html ='<h4 style="color: ##20a050; margin:0; padding:0">Hi there '+user_data['name']+'</h4>'
            message.html +='<h3 style="color: #2da3bd; margin:0; padding:0">Birthdays Today</h3>'
            
            for friend in facebook_data['data']:
                url = urlfetch.fetch("https://graph.facebook.com/" + friend['id'] + "?access_token=" + access_token, method=urlfetch.GET, deadline=20)
                friend_info = json.loads(url.content)
                try:
                    friend_info['birthday']
                except:
                    pass
                else:
                    birthday = friend_info['birthday'][:5]
                    if birthday == current_date:
                        birthday_list += friend_info['name'] + " - Bday: " + friend_info['birthday'] + "\n"
                        birthday_list += "Write on " + friend_info['first_name'] + "'s wall -" + friend_info['link'] + "\n\n"
                        birtday_list_html += '<div style="background: #e6e6e6; margin-top: 10px; color: #2b81c5; position: relative; padding: 10px; width: 300px; overflow: hidden;">'
                        birtday_list_html += '<img style="margin-left:auto; margin-right:auto; float:left; height:60px; width:auto;" src="https://graph.facebook.com/'+friend_info['id']+'/picture">'
                        birtday_list_html += '<div style="float: left; margin-left: 10px; margin-top:10px">'
                        birtday_list_html += '<p style="margin: 0; padding: 0; font-size:16px; font-family: Times New Romman serif;">'+friend_info['name']+'</p>'
                        birtday_list_html += '<p style="margin: 0; padding: 0; font-size:16px; font-family: Times New Romman serif;"><a href="'+friend_info['link']+'" style="color: #8e8e8e; text-decoration: none;">Write on '+friend_info['first_name']+'\'s wall</a></p>'
                        birtday_list_html += '</div></div>'
            if birthday_list != "":
                message.body += "Today the people with birthdays are:\n\n" + birthday_list
                message.html += birtday_list_html
                message.send()
                logging.info("Message sent to " + str(email))

class Mike(webapp2.RequestHandler):
    def get(self):
        count = Users.all().count()
        
        if count > 0:
            users = Users.all()
            users.filter("facebookID = ", "691580472")
            users.fetch(1)
            for user in users:
                taskqueue.add(url='/mike', params={"email": user.email, "access_token": user.accessToken})
                
        else:
            self.response.out.write("No users")

    def post(self):
        access_token = self.request.get("access_token")
        email = self.request.get("email")
        url = urlfetch.fetch("https://graph.facebook.com/me/friends?access_token=" + access_token, method=urlfetch.GET, deadline=20)
        facebook_data = json.loads(url.content)
        message = mail.EmailMessage(sender="Bithdays Update<mike@mikechernev.com>",
                                    subject="Your birthday fellas")
        message.to = "mike@mikechernev.com"
        try:
            facebook_data['data']
        except:
            message.body = """
            Hi there,
            There seems to be a problem with your account.
            
            """
            try:
                facebook_data['error']
            except:
                message.body += "We'll try to resolve it as soon as possible"
            else:
                if facebook_data['error']['code'] == 190 and facebook_data['error']['error_subcode'] == 463:
                    message.body += "Your access token is invalid. In order to use the Birthday reminder you will have to subscribe again"
                else:
                    message.body += "We'll try to resolve it as soon as possible"
            logging.info(facebook_data)
            message.send()
            logging.info("Message sent to " + str(email))
        else:
            birthday_list = ""
            message.body = "Hi there,\n"
            birtday_list_html = ""
            message.html ='<h3 style="color: #2da3bd; margin:0; padding:0">Birthdays Today</h3>'
            
            for friend in facebook_data['data']:
                url = urlfetch.fetch("https://graph.facebook.com/" + friend['id'] + "?access_token=" + access_token, method=urlfetch.GET, deadline=20)
                friend_info = json.loads(url.content)
                try:
                    friend_info['birthday']
                except:
                    pass
                else:
                    birthday_list += friend_info['name'] + " - Bday: " + friend_info['birthday'] + "\n"
                    birthday_list += "Write on " + friend_info['first_name'] + "'s wall -" + friend_info['link'] + "\n\n"
                    birtday_list_html += '<div style="background: #e6e6e6; margin-top: 10px; color: #2b81c5; position: relative; padding: 10px; width: 300px; overflow: hidden;">'
                    birtday_list_html += '<img style="margin-left:auto; margin-right:auto; float:left; height:60px; width:auto;" src="https://graph.facebook.com/'+friend_info['id']+'/picture">'
                    birtday_list_html += '<div style="float: left; margin-left: 10px; margin-top:10px">'
                    birtday_list_html += '<p style="margin: 0; padding: 0; font-size:16px; font-family: Times New Romman serif;">'+friend_info['name']+'</p>'
                    birtday_list_html += '<p style="margin: 0; padding: 0; font-size:16px; font-family: Times New Romman serif;"><a href="'+friend_info['link']+'" style="color: #8e8e8e; text-decoration: none;">Write on '+friend_info['first_name']+'\'s wall</a></p>'
                    birtday_list_html += '</div></div>'
            if birthday_list != "":
                message.body += birthday_list
                message.html += birtday_list_html
                message.send()
                logging.info("Message sent to " + str(email))

class List(webapp2.RequestHandler):
    def get(self):
        users = Users.all()
        users.filter("facebookID = ", "691580472")
        users.fetch(1)
        user_key = users[0].key()
        template = jinja_environment.get_template('list.html')
        self.response.out.write(template.render())

class OtherPages(webapp2.RedirectHandler):
    def get(self):
        self.redirect('/')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/ajax', AjaxCall),
                               ('/processUsers', ProcessUsers),
                               ('/users', DisplayUsers),
                               ('/birthdays', Birthdays),
                               ('/mike', Mike),
                               ('/list', List),
                               ('/.*', MainPage)
                               ], debug=True)
