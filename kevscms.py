from fasthtml import *
from fasthtml.common import *
from fastlite import *
from dataclasses import dataclass
from models import User, Post, Post_text, Media, Comment

# Add the Font Awesome script to the page
font_awesome_script = Script(src="https://kit.fontawesome.com/a66cf5c2cf.js", crossorigin="anonymous")

bootstrap_css = Link(href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css", rel="stylesheet", integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC", crossorigin="anonymous")

login_redir = RedirectResponse('/login/')

def before(request, session):
    request.scope['auth'] = session.get('auth', None)
    if not request.scope['auth']:
        print('user not authenticated, redirecting to login')
        return login_redir
    print('user authenticated')

bware = Beforeware(before, skip=[r'/favicon.ico', r'/static/.*', r'/login/', r'.*\.css'])

app = FastHTML(bware=bware, live=True, hdrs=[bootstrap_css, font_awesome_script])
rt = app.route
db = database('kevscms.sqlite')

dt = db.t

if 'user' not in dt:
    users = db.create(User, pk='id')
    # Add some users
    users.insert(username='Kev',firstname='Kevin', lastname='McAleer', email="kevinmcaleer@gmail.com", password="password", is_admin=True, is_active=True)
    users.insert(username='Jenni', email="jennimcaleer@me.com", password="password", is_admin=False, is_active=True)
    users.insert(username='Alex', email="alexmcaleer@icloud.com", password="password", is_admin=False, is_active=True)
users = dt.user
if 'post' not in dt:
    posts = db.create(Post)
    posts.insert(title='My First Post', user_id=1)
    posts.insert(title='My Second Post', user_id=1)
    posts.insert(title='My First Post by Jen', user_id=2)
    posts.insert(title='My Second Post by Jen', user_id=2)
    posts.insert(title='My First Post by Alex', user_id=3)
    posts.insert(title='My Second Post by Alex', user_id=3)
posts = dt.post
if 'post_text' not in dt:
    post_texts = db.create(Post_text)

posts_text = dt.post_text
if 'media' not in dt:
    media = db.create(Media)
media = dt.media
if 'Comment' not in dt:
    comments = db.create(Comment)    
comments = dt.comment
def user_table():
    return Ul(*users(), cls=list_class)

def render_navbar(username=None):

    if username: # User is logged in and authenticated
        navbar = Nav(
            Ul(
                Li(A("Home", href="/", cls="nav-link"), cls="nav-item"),
                Li(A("My Projects", href="/posts/", cls="nav-link"), cls="nav-item"),
                Li(A("Logout", href="/logout/", cls="nav-link"), cls="nav-item"),
                Li(A(username, href='#', name="profile", cls="nav-link"), cls="nav-item"),    
        cls="navbar-nav"),
        cls="navbar navbar-expand-lg navbar-light bg-light")
    else:
        navbar = Nav(
            Ul(
                Li(A("Home", href="/" , cls="nav-link"), cls="nav-item"),
                Li(A("Register", href="/register/" , cls="nav-link"), cls="nav-item"),
                Li(A("Login", href="/login/" , cls="nav-link"), cls="nav-item"),
                Li(A("", href='#', name="profile" , cls="nav-link"),),
            cls="navbar-nav"
            ),
            cls="navbar navbar-expand-lg navbar-light bg-light"
        )
    return navbar

@rt('/posts')
def post_table(request):
    navbar = render_navbar(get_current_user(request)['username'])
    posts = get_posts(user_id=get_current_user(request)['id'])
    return navbar, Ul(*posts)

@rt('/register/', name="user_register", methods=['GET', 'POST'])
async def register(request):
    """Register a new user"""

    # Handle POST request for form submission
    if request.method == 'POST':
        form_data = await request.form()
        username = form_data.get('username')
        email = form_data.get('email')
        password = form_data.get('password')

        # Validation could go here (e.g., check if user already exists)

        # Insert the new user into the database
        users.insert(username=username, email=email, password=password)

        print(users)
        # Redirect to a success page or the user list
        return Redirect('/')

    # Render the registration form for GET request
    form = Form(
        Fieldset(
            Label('Username', For='username'),
            Input(id='username', name='username', value='', required=True),
            Label('Email', For='email'),
            Input(id='email', name='email', value='', type='email', required=True),
            Label('Password', For='password'),
            Input(id='password', name='password', type='password', value='', required=True),
            Button('Register', type='submit', hx_post='/register/'),
        )
    )
    
    # Render the page

    navbar = render_navbar(request)
    page = Titled('Register', navbar, H2('Register User'), Hr(), form)
    return page

def lookup_user(username, password):
    try: 
        print(f'searching for username is {username} and password is {password}')
        search_string = f"username='{username}'"
        result = users(where=search_string)
        print(f'result is {result}')
        if result:
            user = result[0]
            if user['password'] == password:
                print('password matches')
                return user
            else:
                print('password does not match')
                return None
    except NotFoundError: 
        print('username not found')
        return None

@rt('/login')
async def login(request):
    """Login a user"""
    # Handle POST request for form submission
    if request.method == 'POST':
        form_data = await request.form()
        username = form_data.get('username')
        password = form_data.get('password')

        # Validation could go here (e.g., check if user exists and password matches)

        # Authenticate the user
        user = lookup_user(username=username, password=password)
        if not user:
            navbar = render_navbar()
            return Redirect('/')
        
        # Set the user as authenticated
        request.session['auth'] = user['id']

        return Redirect('/')

    # Render the login form for GET request
    form = Form(
        Fieldset(
            Label('Username', For='username'),
            Input(id='username', name='username', value='', required=True),
            Label('Password', For='password'),
            Input(id='password', name='password', type='password', value='', required=True),
            Hr(),
            Label(id='register', name='register', value='Register', hx_get='/register/'),
            A('Register', href='/register/'),
            Button('Login', type='submit', hx_post='/login/'),
            Br(),
        )
    )

    navbar = None

    # Render the page
    page = Titled('Login', navbar, H2('Login'), Hr(), form)
    return page
@rt('/logout/', name="user_logout")
async def logout(request):
    """Logout a user"""
    request.session['auth'] = None
    return Redirect('/')

def get_current_user(request):
    """Get the current authenticated user"""
    user_id = request.session['auth']
    print(f'get_curent_user request - user_id is {user_id}')
    if user_id:
        return users[user_id]
    return None

def public_posts():
    """Get the public posts from active users"""

    # SQL query to join post and user tables and filter by active users

    query = """
        SELECT post.*, user.username 
        FROM post
        JOIN user ON post.user_id = user.id
        WHERE user.is_active = True
    """

    # print(f'Executing query: {query}')
    result = db.q(query)
    print(f'Result is: {result}')
    return result


def get_posts(user_id, limit=10):
    """Get the posts for a user"""
    my_posts = posts(where=f"user_id={user_id}", limit=limit)
    # print(f'Posts for user: {user_id}, {my_posts}')
    return my_posts

@rt('/')
async def index(request):
    """ Main Homepage """
    
    username = None
    if not request.session['auth']:
        print('user not authenticated, redirecting to login')
        # navbar = Nav('Login')
        return login_redir

    current_user = get_current_user(request)
    username = current_user['username']
    print('current user:', username)
    navbar = render_navbar(username)
    page_content = P('Welcome to Kevs CMS')
    # public_posts = get_posts(user_id=current_user['id'])
    # print('public posts', public_posts())
    post_cards = []
    for post in public_posts():
        card = Div(
            Div(
                H5(post['title'], cls="card-title"),
                P(post['date_created'], cls="card-text"),
                P(post['date_last_updated'], cls="card-text"),
                P('By ', post['username'], cls="card-text"),
                A("Read More", href=f"/posts/{post['id']}", cls="btn btn-primary"),
                cls="card-body"
            ),
            cls="card"
        )
        post_cards.append(Div(card, cls="col-md-4 mb-4"))

    # Wrap all cards in a Bootstrap row
    show_posts = Div(*post_cards, cls="row")
    page = Titled('Projects', navbar, H2('Kevs Robots'), Hr(), page_content, show_posts)

    return page

@rt('/posts/{id}')
def get_post(id:int):
    """Get a single post"""
    
    post_dict = posts[id]
    print(f'post_dict - {post_dict}')
    post = Post(**post_dict)
    print(f'post is {post}')        
    print(f'post title is {post.title}')

    page_content = H1(post.title), \
            P('Created: ', post.date_created), \
            P('Last Updated: ',post.date_last_updated), \
            P('Author',post.user_id)
    navbar = render_navbar()

    return Titled(post.title, navbar, page_content)

serve()