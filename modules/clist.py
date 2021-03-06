import pymongo
import random
import uuid
import web

class DynamicForm(web.form.Form):
    def add(self, element):
        listElements = list(self.inputs)
        listElements.append(element)
        self.inputs = tuple(listElements)


class Default:

    def GET(self):
        return "OK"

class Create:

    createForm = DynamicForm(
        web.form.Textbox('name', description='Name'),
        web.form.Textarea('users', description='Users'),
        web.form.Textarea('itemlist', descritption='Items'),
        web.form.Hidden('id', value=uuid.uuid4()),
        web.form.Button('submit', type='submit', description='Submit')
    )

    def GET(self):
        return render.create(self.createForm)

    def POST(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.check
        collection = db.lists

        f = self.createForm()
        if not f.validates():
            return render.error("Form not validated.")

        print(f.d.name)
        print(f.d.users)
        print(f.d.itemlist)

        document = {'id' : f.d.id, 'name' : f.d.name,
            'users' : self.parseUsers(f.d.users),
            'items' : self.parseItems(f.d.itemlist), 'ownerId' : 1}

        collection.insert(document)

        return web.seeother('/View?id=%s' % f.d.id)

        # Alert all users per email!

    def parseUsers(self, users):
        ret = []
        id = 1

        r = lambda: random.randint(0,255)

        for mail in users.split(','):
            randId = random.randint(0,4096)
            ret.append({'id' : id, 'email' : mail.strip(), 'color' : "#%02X%02X%02X" % (r(), r(), r()), 'random' : randId, 'used' : 0})
            id = id + 1
        return ret

    def parseItems(self, items):
        ret = []
        id = 1

        for name in items.split(','):
            ret.append({'id' : id, 'name' : name.strip(), 'checked' : []})
            id = id + 1

        return ret

class Check:

    def GET(self):
        parameters = web.input(id=None,item=None,user=None)
        if parameters.id is None or parameters.item is None or parameters.user is None:
            return render.error("Da fuck.")

        client = pymongo.MongoClient('localhost', 27017)
        db = client.check
        collection = db.lists

        document = collection.find_one({'id' : parameters.id})
        if document is None:
            return render.error("No document with this id.")

        del document['_id']
        for item in document['items']:
            if item['id'] == int(parameters.item):
                exists = False
                for user in item['checked']:
                    if user['id'] == int(parameters.user):
                        exists = True
                        break
                if exists:
                    item['checked'].remove({'id' : int(parameters.user)})
                else:
                    item['checked'].append({'id' : int(parameters.user)})
                break

        collection.update({'id' : parameters.id}, {'$set' : document})

        return web.seeother('/View?id=%s' % parameters.id)


class View:

    def GET(self):
        # Get id from the url parameters.
        parameters = web.input(id=None)
        if parameters.id is None:
            return render.error("No Id was specified.")

        # Open connection to MongoDB
        client = pymongo.MongoClient('localhost', 27017)
        db = client.check
        collection = db.lists

        document = collection.find_one({'id' : parameters.id})
        if document is None:
            return render.error("The specified Id does not exist.")

        return render.view(document)

class Update:

    def GET(self):
        return "OK"

class Delete:

    def GET(self):
        return "OK"

render = web.template.render('templates/', base='layout')

urls = (
    '/', 'Default',
    '/Create', 'Create',
    '/Check', 'Check',
    '/View', 'View',
    '/Update', 'Update',
    '/Delete', 'Delete'
)

app = web.application(urls, locals())
