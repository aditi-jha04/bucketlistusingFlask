from flask import Flask, render_template,request,redirect,url_for 
from pymongo import MongoClient 
from bson.objectid import ObjectId 
from bson.errors import InvalidId 
import os

mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
client = MongoClient(mongodb_host, mongodb_port)    
db = client.bucketlist  
blists = db.blist

app = Flask(__name__)
title = "BucketList with Flask"
heading = "My Bucket List"


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
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	blists.insert({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
	return redirect("/list")

@app.route("/remove")
def remove ():
	#Deleting a goal with various references
	key=request.values.get("_id")
	blists.remove({"_id":ObjectId(key)})
	return redirect("/")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	goal=blists.find({"_id":ObjectId(id)})
	return render_template('update.html',goals=goal,h=heading,t=title)

@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a goal with various references
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	id=request.values.get("_id")
	blists.update({"_id":ObjectId(id)}, {'$set':{ "name":name, "desc":desc, "date":date, "pr":pr }})
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
	return render_template('credits.html',t=title,h=heading)

if __name__ == "__main__":
	env = os.environ.get('APP_ENV', 'development')
	port = int(os.environ.get('PORT', 8000))
	debug = False if env == 'production' else True
	app.run(host='0.0.0.0', port=port, debug=debug)
	