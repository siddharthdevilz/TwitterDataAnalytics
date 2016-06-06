from flask import Flask, render_template, request, redirect, flash
import os
import inGraph
app = Flask(__name__)
app.secret_key = 'random'

@app.route('/')
def hello_world():
    author = "Me"
    name = "You"
    return render_template('index.html', author=author, name=name)

@app.route('/search', methods = ['POST'])
def search():
	print request.form['sbutton']
	if request.form['sbutton']=="Search":
	    text = request.form['key']
	    num = request.form['num']
	    flash("Please wait graph is being populated")
	    print("The name is '" + text + num +"'")
	    t = inGraph.putingraph(text,num)
	    flash("Tweets populated : "+ str(t))
	    return redirect('/')
	elif request.form['sbutton']=="Clear Graph":
		inGraph.cleargraph()
		flash("Graph cleared")
		return redirect('/')

#@app.route('/cleargraph', methods = ['POST'])
#def cleargraph():
	

if __name__ == '__main__':
    app.run()