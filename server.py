
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key='secretkey'

DATABASEURI = "postgresql://krd2141:6952@34.75.94.195/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():

  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):

  try:
    g.conn.close()
  except Exception as e:
    pass

######################################################################################################################

###############      INDEX ROUTE      ################################################################################
@app.route('/')
def index():
    return render_template("index.html")


########################      CHEFS ROUTE      ########################################################################
@app.route('/chefs/', methods=['GET','POST'])
def chefs():
  cursor = g.conn.execute('''SELECT C.chef_name, C.shows, S.cuisine_name, C.followers
  FROM chefs C, specializes_in S
  WHERE C.chef_id = S.chef_id''')
  names = cursor.fetchall()
  cursor.close()
  return render_template("chefs.html", names= names)


#########################     RECIPES ROUTE      #######################################################################
@app.route('/recipes/', methods=['GET','POST'])
def recipes():
  cursor = g.conn.execute("SELECT title, total_time, difficulty FROM recipes")
  names = cursor.fetchall()
  cursor.close()
  return render_template("recipes.html", names=names)


######################     INDIVIDUAL RECIPES VALUES      ###############################################################
@app.route('/single_recipe', methods=["GET","POST"])
def single_recipe():
  if request.method=='POST':
    result = request.form.get('title')
    cursor = g.conn.execute('SELECT * FROM recipes WHERE recipes.title = %s',(result))
    info = cursor.fetchall()
    cursor = g.conn.execute('''SELECT I.ingredient, I.brand, I.quantity
    FROM includes I, recipes R
    WHERE I.recipe_id = R.recipe_id AND R.title = %s''',(result))
    igList = cursor.fetchall()
    cursor = g.conn.execute('''SELECT *
    FROM writes_reviews_about W, recipes R
    WHERE W.recipe_id = R.recipe_id AND R.title = %s''',(result))
    reviews = cursor.fetchall()
    cursor = g.conn.execute('''SELECT L.cuisine_name
    FROM labeled_as L, recipes R
    WHERE L.recipe_id = R.recipe_id AND R.title = %s''',(result))
    tabs = cursor.fetchall()
    cursor.close()
    return render_template('single_recipe.html',info=info, igList=igList, reviews=reviews, tabs=tabs)

  return render_template('single_recipe.html')


############################    UPDATE LIKE    ##########################################################################
@app.route('/updateLike', methods=['GET','POST'])
def updateLike():
  result = request.form.get('like')
  g.conn.execute('''UPDATE writes_reviews_about
  SET likes = likes+1
  WHERE review_num = %s''', (result))
  return redirect(url_for('recipes'))



#########################################  NEW COMMENT #############################################################
@app.route('/addComment', methods=['GET','POST'])
def addComment():
  num = 5000
  num = str(num+1)
  recipe = request.form.get('title')
  recipe = str(recipe)
  if not session.get("username"):
    return redirect(url_for("index"))
  else:
    rating = request.form['rating']
    date = request.form['date']
    comment = request.form['comment']
    username = request.form['username']
    g.conn.execute('''INSERT INTO writes_reviews_about(review_num, rating, likes, date, comment, recipe_id, username)
    VALUES(%s, %s, 0, %s, %s, %s, %s)''', (num, rating, date, comment, recipe, username))                
    return redirect(url_for('single_recipe'))

@app.route('/movePage2', methods=['POST'])
def movePage2():
  recName = request.form.get('recName')
  if request.method=='POST':
    return render_template('addComment.html', recName=recName)


#############################   ADD RECIPE   ############################################################################
@app.route('/addRecipe', methods=['GET','POST'])
def addRecipe():
  if not session.get("username"):
    return redirect(url_for("index"))
  else:
    cursor = g.conn.execute('''SELECT * FROM recipes''')
    number = cursor.fetchall()
    num = len(number)
    num = str(num*2+1)
    username = request.form['username']
    title = request.form['title']
    total_time = request.form['total_time']
    prep_time = request.form['prep_time']
    cook_time = request.form['cook_time']
    difficulty = request.form['difficulty']
    method = request.form['method']
    directions = request.form['directions']
    g.conn.execute('''INSERT INTO recipes(recipe_id, title, total_time, prep_time, cook_time, difficulty, method, directions)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)''', (num, title, total_time, prep_time, cook_time, difficulty, method, directions))
    g.conn.execute('''INSERT INTO owner(recipe_id, username) VALUES(%s, %s)''', (num, username))
    return redirect(url_for('recipes'))

  
@app.route('/movePage', methods=['POST'])
def movePage():
  if request.method=='POST':
    return render_template('addRecipe.html')


##############################     PROFILE ROUTE    #####################################################################
@app.route('/profile/', methods=['GET','POST'])
def profile():
  if not session.get("username"):
    return redirect(url_for("index"))
  else:
    cursor = g.conn.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
    account = cursor.fetchone()
    cursor = g.conn.execute('''SELECT R.title
    FROM recipes R, owner O
    WHERE R.recipe_id = O.recipe_id AND O.username = %s''',(session['username']))
    posts = cursor.fetchall()
    cursor.close()
    return render_template('profile.html', account=account, posts=posts)


###########################      SEARCH FUNCTION   ######################################################################
@app.route('/search', methods=["GET", "POST"])
def search():
  if request.method == 'POST':
    form = request.form
    word = form['wordsearch']
    word = word.lower()
    search = "%{}%".format(word)
    cursor = g.conn.execute('''
    SELECT DISTINCT recipes.title, includes.ingredient, includes.quantity, recipes.directions
    FROM recipes, includes, labeled_as
    WHERE lower(includes.ingredient) LIKE %s AND includes.recipe_id = recipes.recipe_id''', (search))
    info = cursor.fetchall()
    cursor.close()
    return render_template('search.html', info=info)


##########################     USER LOGIN        ########################################################################
@app.route('/login_form', methods = ['POST','GET'])
def login():
  if request.method == 'POST':
    session.pop('username', None)
    username = request.form['username']
    email = request.form['email']
    cursor = g.conn.execute('SELECT * FROM users WHERE username=%s AND email=%s', (username, email))
    account = cursor.fetchall()
    if account:
      session['username']= username
      session['loggedIn'] = True
      return redirect(url_for('profile'))
    else:
      return redirect(url_for('index'))
  
  cursor.close()
  return render_template('profile.html')


#################################    LOGOUT    ##########################################################################
@app.route("/logout")
def logout():
  session["username"]=None
  session['loggedIn']=False
  return redirect("/")


#################################    DELETE USER      ####################################################################
@app.route("/delete")
def delete():
  username = session["username"]
  g.conn.execute('DELETE FROM users WHERE users.username=%s', (username))
  session["username"]=None
  return redirect("/")


##########################    DELETE RECIPE     ###########################################################################
@app.route('/deleteRecipe', methods=['GET','POST'])
def deleteRecipe():
  username = session['username']
  recipe = request.form.get('recipe')
  cursor=g.conn.execute('''SELECT R.recipe_id 
  FROM recipes R, owner O 
  WHERE O.username = %s AND R.recipe_id = O.recipe_id AND R.title=%s''',(username, recipe))
  id = cursor.fetchall()
  print(id)
  g.conn.execute('''DELETE FROM owner WHERE owner.recipe_id = %s''', (id))
  g.conn.execute('''DELETE FROM recipes WHERE recipes.recipe_id=%s''',(id))
  return redirect(url_for('profile'))
  

###############################      NEW USER      ########################################################################
@app.route('/add_user', methods =['GET', 'POST'])
def adduser():
  if request.method == 'POST' and 'username' in request.form:
      username = request.form["username"]
      first_name = request.form["first_name"]
      last_name = request.form["last_name"]
      email = request.form["email"]
      cursor = g.conn.execute('SELECT * FROM users WHERE username=%s', (username))
      account = cursor.fetchall()
      if len(account) > 0:
        return render_template("index.html")
      else:
        g.conn.execute('''INSERT INTO users(username,first_name,last_name,email,favorites)
        VALUES(%s, %s, %s, %s, 0)''', (username, first_name, last_name, email))
        cursor = g.conn.execute('SELECT * FROM users WHERE username=%s AND email=%s', (username, email))
        session['username']= username
        return redirect(url_for('profile'))
  cursor.close()
  return render_template("index.html")


###########################     FAVORITES UPDATE        ###################################################################
@app.route('/favorite', methods=['POST','GET'])
def favorite():
  checked = 'check' in request.form
  if checked:
    username = session['username']
    g.conn.execute('''UPDATE users
    SET favorites = favorites+1
    WHERE username = %s''',(username))
    return redirect(url_for('recipes'))
  return render_template('index.html')


##############################      ADD ROUTE      ####################################################3####################
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
