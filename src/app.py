from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
from flask import session

from src.common.database import Database
from src.models.blog import Blog
from src.models.post import Post
from src.models.user import User

#use a more secure secret key for real world use
app = Flask(__name__)
app.secret_key = "finn"

@app.route('/')
def home_template():
    return render_template('home.html')

#default route renders the login page
@app.route('/login')
def login_template():
    return render_template('login.html')

@app.route('/register')
def register_template():
    return render_template('register.html')

#initializes database before doing anything else
@app.before_first_request
def initialize_database():
    Database.initialize()

#use post instead of get to hide data from url
@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    #set email to None for now if login is invalid
    if User.login_valid(email, password):
        User.login(email)
        return render_template('profile.html', email=session['email'], auth_failed=False)
    else:
        return render_template('home.html', auth_failed=True)


@app.route('/auth/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password']

    # email is added to current session in register function
    if User.register(email, password):
        return render_template('profile.html', email=session['email'])
    else:
        return render_template('register.html', user_exists=True)

@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blogs(user_id=None):
    if user_id is not None:
        author = User.get_by_id(user_id)
        myPage = False
    else:
        author = User.get_by_email(session['email'])
        myPage = True
    blogs = author.get_blogs()

    return render_template('user_blogs.html', blogs=blogs, email=author.email, myPage = myPage)

#allow post and get to access route with or without data
@app.route('/blogs/new', methods=['POST', 'GET'])
def create_new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_email(session['email'])

        new_blog = Blog(user.email, title, description, user._id)
        new_blog.save_to_mongo()

        #instead of rendering template, redirect thru function for /blogs
        return make_response(user_blogs(user._id))

@app.route('/blogs/delete/<string:blog_id>')
def delete_blog(blog_id):
    if Blog.delete_blog(blog_id):
        print('blog deleted')
    else:
        print("blog couldn't be deleted")
    return make_response(user_blogs())

@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    blog = Blog.from_mongo(blog_id)
    user = User.get_by_id(blog.author_id)
    if user.email == session['email']:
        myPage = True
    else:
        myPage = False
    posts = blog.get_posts()

    return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id, myPage=myPage)



@app.route('/posts/new/<string:blog_id>', methods = ['POST', 'GET'])
def create_new_post(blog_id):
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.get_by_email(session['email'])

        new_post = Post(blog_id, title, content, user.email)
        new_post.save_to_mongo()

        return make_response(blog_posts(blog_id))

@app.route('/logout')
def logout():
    User.logout()
    return render_template('home.html', signout_success=True)


@app.route('/all_users')
def get_all_users():
    users = User.get_users()
    return render_template('all_users.html', users=users)

if __name__ == '__main__':
    app.run(port=8282)