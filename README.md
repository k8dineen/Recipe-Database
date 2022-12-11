# 4111-proj1 Part 3

PostgreSQL account: cec2262

postgresql://cec2262:3293@34.75.94.195/proj1part2

IP: http://172.31.46.208:8111


Original description: 
"This application is a recipe database. Someone looking to find a recipe would use this application. Users also looking to be a part of a cooking/recipe community would also use this website. Upon creating a user account, the user will be able to use this application to search for recipes as well as add their own recipes. The user will also have other options to interact with the application such as rating, commenting, and liking. The recipes that will exist in the database from the start will all have been manually entered by us."

Actaul Implementation: 
This application is a recipe database. Users will be prompted to sign up for an account, seach for recipes using the search box or by navigating through the Navbar links. The user will stay logged in until the physical clicking of "logout"
 This ensures the user can like, follow, create, comment on recipes. The information is stored and displayed in the /profile page. The user has the option to add their own recipes as well. Essentially, the application performs how we had written it in part 1. 

First webpage we foudn interesting: 
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

  --The reason we find this working so well is because it initiates so many connections to different tables in order to display results to the HTML file. This page is related to different database operations becasue this is how a developer would have to display information from various tables. Databses need to store a variety of infomration in different tables, and this page is showing exaclty how to display info from different tables. 

  ****Second Webpage *******
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



--this webpage we find very interesting because it gave us an idea of how login or authentication sessions work. FOr instance, in this application, a user creates an account and will stay authenticated until the user presses "logout."
Obviously, security wise, this isn't ideal. But, this is a great foundation to learn from. This is related to DB operations just for the simple fact that most websites require authentication before using their applications. SO our does relate in that regard! 


