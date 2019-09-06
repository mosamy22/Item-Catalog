from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from dbconfig import Country, Base, Club,User
from sqlalchemy.orm import sessionmaker,joinedload
from flask import make_response
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"



# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all items
@app.route('/')
@app.route('/catalog/')
def showItems():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    countries = session.query(Country)
    clubs = session.query(Club).order_by((Club.id).desc()).limit(12)
    if 'username' not in login_session:
        return render_template('Allcatalog.html', countries=countries,clubs = clubs)
    #else:
    return render_template('privateAllcatalog.html', countries=countries,clubs = clubs)

# show the clubs of country
@app.route('/catalog/<string:country_name>/items')
def showCountryClubs(country_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    country = session.query(Country).filter_by(name = country_name).one()
    country_id = country.id
    countries = session.query(Country)
    clubs = session.query(Club).filter_by(country_id = country_id).order_by((Club.id).desc()).limit(12)

    return render_template('countryclubs.html', countries=countries,clubs = clubs,country_name = country.name)

@app.route('/catalog/<string:country_name>/<string:club_name>')
def showdescription(club_name,country_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    club = session.query(Club).filter_by(title = club_name).one()
    description = club.description
    if 'username' not in login_session :
        return render_template('description.html', club = club_name,description = description)
    else:
        return render_template('privatedescription.html', club = club_name,description = description)

# Create a new Club

@app.route('/catalog/new/', methods=['GET', 'POST'])
def newClub():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        country_name = request.form['country']
        country = session.query(Country).filter_by(name = country_name).one()
        newClub = Club(
            title=request.form['name'],user_id=login_session['user_id'],description=request.form['description'],country_name=country.name,country_id=country.id)
        session.add(newClub)
        flash('New Club %s Successfully Created' % newClub.title)
        session.commit()
        return redirect(url_for('showItems'))
    else:
        return render_template('newclub.html')

# Edit the club
@app.route('/catalog/<string:club_name>/edit/', methods=['GET', 'POST'])
def editClub(club_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedClub = session.query(
        Club).filter_by(title=club_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedClub.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this club. Please create your own Club in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedClub.title = request.form['name']
        if request.form['description']:
            editedClub.description = request.form['description']
        if request.form['country']:
            editedClub.country_name = request.form['country']
            country = session.query(Country).filter_by(name = request.form['country']).one()
            country_id = country.id
            editedClub.country_id = country_id
            session.add(editedClub)
            flash('Club Successfully Edited %s' % editedClub.title)
            session.commit()
            return redirect(url_for('showdescription',club_name = editedClub.title,country_name = editedClub.country_name))
    else:
        return render_template('editclub.html', club=editedClub)

# Delete a club
@app.route('/catalog/<string:club_name>/delete/', methods=['GET', 'POST'])
def deleteClub(club_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    deletedClub = session.query(Club).filter_by(title=club_name).one()
    if deletedClub.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this club. Please create your own Club in order to delete it.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(deletedClub)
        flash('%s Successfully Deleted' % deletedClub.title)
        session.commit()
        return redirect(url_for('showItems'))
    else:
        return render_template('deleteclub.html', club= deletedClub)

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        return redirect(url_for('showItems'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showItems'))


#logging via facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token


    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    #login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    #output += '<img src="'
    #output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

#logging via google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# JSON APIs to view Catalog Items
@app.route('/catalog.json')
def showItemsJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Country).options(joinedload(Country.items)).all()
    return dict(Catalog=[dict(c.serialize, items=[i.serialize
                                                     for i in c.items])
                         for c in categories])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
