
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key='secretkey'

DATABASEURI = "postgresql://cec2262:3293@34.75.94.195/proj1part2"


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

#####################################################################################################################################

###############      INDEX ROUTE      ###############################################################################################
@app.route('/')
def index():
    return render_template("index.html")



###############      CHEFS ROUTE      ###############################################################################################
@app.route('/chefs/', methods=['GET','POST'])
def chefs():
  cursor = g.conn.execute("SELECT chef_name, show, followers, posts FROM chefs")
  names = cursor.fetchall()
  cursor.close()

  return render_template("chefs.html", names= names)


###############      CHEFS PAGE ROUTE      ###############################################################################################
@app.route('/chefs/<chef_id>', methods=['GET','POST'])
def renderChef_id(chef_id=None):
  cursor = g.conn.execute("SELECT chef_id FROM chefs")
  chefInfo = chefs[chef_id]
  cursor.close()
  return render_template("chef_id.html", chefInfo=chefInfo)

###############      RECIPES ROUTE      ###############################################################################################

@app.route('/recipes/', methods=['GET','POST'])
def recipes():
  cursor = g.conn.execute("SELECT title, total_time, difficulty FROM recipes")
  names = cursor.fetchall()
  cursor.close()
  return render_template("recipes.html", names=names)


@app.route('/single-recipe/', methods=['GET','POST'])
def recipeInfo(title):
  cursor = g.conn.execute('SELECT * FROM recipes WHERE title = %s', (title))
  info = cursor.fetchall()
  cursor.close()
  return render_template("single-repice.html", info=info)



###############      PROFILE ROUTE      ###############################################################################################
@app.route('/profile/', methods=['GET','POST'])
def profile():
  if not session.get("username"):
    return redirect(url_for("index"))
  else:
    cursor = g.conn.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
    account = cursor.fetchone()
    return render_template('profile.html', account=account)



######## USER LOGIN #################################
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
      return redirect(url_for('profile'))
    else:
      return redirect(url_for('index'))
  
  cursor.close()
  return render_template('profile.html')


########### LOGOUT ##########################
@app.route("/logout")
def logout():
  session["username"]=None
  return redirect("/")


######## NEW USER #################################
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
        g.conn.execute('INSERT INTO users(username,first_name,last_name,email) VALUES(%s, %s, %s, %s)', (username, first_name, last_name, email))
        cursor = g.conn.execute('SELECT * FROM users WHERE username=%s AND email=%s', (username, email))
        session['username']= username
        return redirect(url_for('profile'))
  cursor.close()
  return render_template("index.html")


###############      ADD ROUTE      ###############################################################################################
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
