from xlib.appenginekit import Handler, route
from model.test import Test


@route('/test/')
class TestHandler(Handler):
    def get(self):
        self.respond('Yea.. {}'.format(len(Test.query().fetch(keys_only=True))))

# @get('/test/')
# def do_shit(request, response):
# 	#TODO
# 	request.url
# 	request.headers
# 	request.body
# 	response.status
# 	response.headers
# 	response.body
# 	
# 	#TODO
# 	request.params
# 	request.cookies
# 	#TODO: http auth
# 	raise response.Error(404)
# 	raise response.Redirect('https://dick.poop/')
# 	response.status
# 	response.cookies
# 	response.content_type
# 	response.headers
# 	response.write({})
# 
# 
# @cron
# def do_the_thing():
# 	pass
# 
# 
# @task
# def do_stuff(params):
# 	#TODO
# 	pass
# q = do_stuff.Queue()
# q.add({}, id='asdf')
# q.flush()