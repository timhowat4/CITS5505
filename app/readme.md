-- MovieVote. --

For this project we were required to build a multi-user web application. The application was written using HTML, CSS, Flask, AJAX, JQuery, and Bootstrap. MovieVote provides a platform for users to vote on their favourite movies, suggest new movies for votes, and view current leaderboard standings. 


-- Design --

Our vision for MovieVote was an accessible, user-friendly platform to enable social choice voting. This application enables users to not only vote on their favourite movies but also view other user's current vote preferences, comment suggestions for new movies to vote on, or just say whatever they like about the current leaderboard standings. We chose a simple layout with minimal page links and also stylized the application in a stripped-back, essentials only manner to enable maximal functionality and site purpose.

We opted to have many of the functions of the web application available only to registered users to promote internal activity. Users who have not signed in to the application will only be able to view the leaderboard page, and will have to sign in to vote, comment, and view users. MovieVote Administrators are able to add and delete movies for voting, and grant Admin status to registered users.


-- Requirements/Installation --

Flask - pip install flask
SQLAlchemy - pip install flask-sqlalchemy
Flask-Migrate - pip install flask-migrate
Flask-Login - pip install flask-login
Flask-Bootstrap - pip install flask-bootstrap
Flask-Mail - pip install flask-mail
Flask-wtf - pip install flask-wtf
JSON Web Tokens - pip install pyjwt


-- Launching the application --

The flask-application is easily launched on a local host:
In the top level directory, specify into the terminal "FLASK_APP=microblog.py", followed by "flask run".

It may be necessary to additionally type "flask db migrate" followed by "flask db upgrade" to sync with the database.


-- Built With --

HTML, CSS, Flask, AJAX, JQuery, and Bootstrap.


-- References --

Tutorials:

https://github.com/miguelgrinberg/microblog - Miguel Grinberg's microblog mega-tutorial.
https://danidee10.github.io/2016/09/18/flask-by-example-1.html - Flask by example _osaetindaniel.

Images:

PulpFiction.jpeg - https://wallpapertag.com/wallpaper/full/0/d/8/173009-pulp-fiction-wallpaper-1920x1080-high-resolution.jpg
Interstellar2.jpg - http://kokice.me/top-10-preporuka-za-filmove-iz-2014/
HarryPotterDeathlyHallows2.jpg - http://wallpapersexpert.com/harry-potter-wallpapers/3302245.html
Endgame2.jpg - https://www.ubackground.com/wallpaper/films/avengers_endgame_movie_marvel_comics_poster/22-0-18272

Templating:
See static and font folders.

Bootstrap compiled CSS/JS: Available at 'https://getbootstrap.com/docs/4.0/getting-started/download/'.
https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css
https://fonts.googleapis.com/css?family=Pacifico
https://code.jquery.com/jquery-3.2.1.slim.min.js
https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js 
https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js 


-- Authors --
Tim Howat, Reuben Mansfield

-- Acknowledgments --
Special thanks to Miguel Grinberg for a fantastic Flask-App Mega-Tutorial.

