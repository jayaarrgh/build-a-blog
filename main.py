#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        i = Blog.get_by_id(int(id))
        a = i.subject
        b = i.content
        post = ("<h1>" + a + "</h1>" + "<h3>" + b + "</h3>")
        self.response.write(post)


class WelcomePage(webapp2.RequestHandler):
    def get(self):
        a = "<h1><a href='/blog'>Click here to access the blog</a></h1>"
        self.response.out.write(a)


class MainPage(Handler):
    def render_front(self, subject="", content="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("front.html", subject=subject, content=content, error=error, blogs=blogs)

    def get(self):
        self.render_front()


class NewPost(Handler):
    def render_front(self, subject="", content="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("newpost.html", subject=subject, content=content, error=error, blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = Blog(subject=subject, content=content)
            post.put()

            self.redirect("/blog/" + str(post.key().id()))
        else:
            error = "We need both a subject and some content!"
            self.render_front(subject, content, error)


app = webapp2.WSGIApplication([("/", WelcomePage),
                               ("/blog", MainPage),
                               ("/blog/newpost", NewPost),
                               (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
                               ], debug=True)




