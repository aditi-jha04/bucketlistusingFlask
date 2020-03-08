from flask import Flask, render_template,request,redirect,url_for 
from pymongo import MongoClient 
from bson.objectid import ObjectId 
from bson.errors import InvalidId 
import os
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter 

mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
client = MongoClient(mongodb_host, mongodb_port)    
db = client.bucketlist  
blists = db.blist

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissupposedtobeasecret'
title = "BucketList with Flask"
heading = "My Bucket List"

twitter_blueprint = make_twitter_blueprint(api_key='GdWX0iNjKtvQJDFAwJZsc6IqT', api_secret='cVsNzKIc7QiCDIbJAS3NE3tJDrsdAzbjrRAbVH0gZiDPzXLm0l')

github_blueprint = make_github_blueprint(client_id='790c691f198429411955', client_secret='3031591ff5ef6b9feae268ddcce6bf3dda016a8f')

app.register_blueprint(twitter_blueprint, url_prefix='/twitter_login')

app.register_blueprint(github_blueprint, url_prefix='/github_login')


@app.route('/twitter')
def twitter_login():
	if not twitter.authorized:
		return redirect(url_for('twitter.login'))
	account_info=twitter.get('account/settings.json')

	if account_info.ok:
		account_info_json = account_info.json()

		return '<h1> Your Twitter Name is @{}'.format(account_info_json['screen_name'])

	return '<h1>Request Failed!</h1>'



def redirect_url():
	return request.args.get('next') or \
		request.referrer or \
		url_for('index')

@app.route("/list")
def lists ():
	
	blists_l = blists.find()
	a1="active"
	return render_template('index.html',a1=a1,blists=blists_l,t=title,h=heading)

@app.route("/")
@app.route("/uncompleted")
def goals ():
	
	blists_l = blists.find({"done":"no"})
	a2="active"
	return render_template('index.html',a2=a2,blists=blists_l,t=title,h=heading)


@app.route("/completed")
def completed ():
	
	blists_l = blists.find({"done":"yes"})
	a3="active"
	return render_template('index.html',a3=a3,blists=blists_l,t=title,h=heading)

@app.route("/done")
def done ():
	#Done-or-not ICON
	id=request.values.get("_id")
	goal=blists.find({"_id":ObjectId(id)})
	if(goal[0]["done"]=="yes"):
		blists.update({"_id":ObjectId(id)}, {"$set": {"done":"no"}})
	else:
		blists.update({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
	redir=redirect_url()	# Re-directed URL i.e. PREVIOUS URL from where it came into this one

#	if(str(redir)=="http://localhost:5000/search"):
#		redir+="?key="+id+"&refer="+refer

	return redirect(redir)

@app.route("/add")
def add():
	return render_template('add.html',h=heading,t=title)

@app.route("/action", methods=['POST'])
def action ():
	#Adding a goal
	name=request.values.get("name")
	description=request.values.get("description")
	date=request.values.get("date")
	pr=request.values.get("pr")
	blists.insert({ "name":name, "description":description, "date":date, "pr":pr, "done":"no"})
	return redirect("/list")

@app.route("/remove")
def remove ():
	#Deleting a goal with various references
	key=request.values.get("_id")
	blists.remove({"_id":ObjectId(key)})
	return redirect("/list")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	goal=blists.find({"_id":ObjectId(id)})
	return render_template('update.html',goals=goal,h=heading,t=title)

@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a goal with various references
	name=request.values.get("name")
	description=request.values.get("description")
	date=request.values.get("date")
	pr=request.values.get("pr")
	id=request.values.get("_id")
	blists.update({"_id":ObjectId(id)}, {'$set':{ "name":name, "description":description, "date":date, "pr":pr }})
	return redirect("/")

@app.route("/search", methods=['GET'])
def search():
	#Searching a goal with various references

	key=request.values.get("key")
	refer=request.values.get("refer")
	if(refer=="id"):
		try:
			blists_l = blists.find({refer:ObjectId(key)})
			if not blists_l:
				return render_template('index.html',a2=a2,blists=blists_l,t=title,h=heading,error="No such ObjectId is present")
		except InvalidId as err:
			pass
			return render_template('index.html',a2=a2,blists=blists_l,t=title,h=heading,error="Invalid ObjectId format given")
	else:
		blists_l = blists.find({refer:key})
	return render_template('searchlist.html',blists=blists_l,t=title,h=heading)

@app.route("/about")
def about():
	a4="active"
	return render_template('credits.html',a4=a4,t=title,h=heading)

if __name__ == "__main__":
	env = os.environ.get('APP_ENV', 'development')
	port = int(os.environ.get('PORT', 8000))
	debug = False if env == 'production' else True
	app.run(host='0.0.0.0', port=port, debug=debug)
	