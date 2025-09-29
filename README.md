# semester2-group-project
Semester 2 project, group 4 
Very simple questions

Where's the CSS?

/static/css/


What is the skeleton/base/main template?

/templates/base.html




Making a new page
The way pages here work is as follows:

base.html is the "skeleton" needed for each page. It includes the header (top bar), footer and other base things.
Jinja (Rendering engine of used by Flask) supports template inheritance - meaning that it's possible to use base.html and insert content in the middle of it.
That way, we can keep the same navigation bar and general CSS on every single page.


Actually creating it

Create your .html file inside the templates folder, name it whatever you like.
Use the general template you can see in all other files, extending base.html

Look at the tags and simply copy their structure, use {% extends "base.html" %} on each page, where you want to have the navbar and CSS.
The only page that doesn't use the template is the sign-in page.


In the base file, go to line 41 and add an entry for your page to the nav object.

In case you want your page to only be visible for logged-in users, place it inside the current_user.is_authenticated statement


Add an @app.route to your page in app.py, write your backend.
