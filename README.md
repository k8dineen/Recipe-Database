# 4111-proj1 Part 3

-Login on the home page that will redirect the user to their profile and print out their information.
-If they are not in the database when you click login it just stays on the homepage.
-If they are not logged in and they click the Profile tab, it will keep them at the homepage until they login
-New user form to add users to the database. If you try to add a user with the same a repeated user name
it just redirects to the homepage again. 
-Search bar allows user to search for recipes by ingredients. Displaying recipe information on search.html
    -changes both user input and database values to lower() to search for anything with those letters
-Once logged in, user has the option to log out or delete their account
-Recipe page lists all recipes in database, linking them to a new page that displays all their info
-Lists out ingredients, brand, and amount
-Displays all the reviews and ratings
-Users have option to add a recipes to their favorites, increasing that database value
-Users can like individual reviews, updating the page and amount of likes
-Add recipe button allows users to add recipes to datbase





Chris:
I have spent far too long working on a redirect and I need a new approach. It seems after looking through multiple 
resources, I should look at changing the redirects from a clickable link to a form. I'm going to try and add a 
button to each database row that allows the user to click and hopefully to a new HTML page. After that, to display
a user profile page, I will most likely just add a search box where the user will just have to type in the name
of the profile they would like to visit. Hopefully using forms will make it easier. 

-For this push, I am going to merge with main to establish a point where I can pull from if I need to start over


