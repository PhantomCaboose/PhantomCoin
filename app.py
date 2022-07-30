import flask,sql_helpers, passlib.hash, functools, time
from forms import *


app = flask.Flask(__name__)

def is_logged_in(function):
    @functools.wraps(function)
    def wrap(*args, **kwargs):
        if 'logged_in' in flask.session:
            return function(*args, **kwargs)
        else:
            flask.flash("Unauthorized, please login.", "danger")
            return flask.redirect(flask.url_for('login'))
    return wrap

#log in the user by updating session
def log_in_user(username):
    users = sql_helpers.Table("users", "name", "email", "username", "password")
    user = users.getone("username", username)

    flask.session['logged_in'] = True
    flask.session['username'] = username
    flask.session['name'] = user[0]
    flask.session['email'] = user[1]

#Registration page
@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegisterForm(flask.request.form)
    users = sql_helpers.Table("users", "name", "email", "username", "password")

    #if form is submitted
    if flask.request.method == 'POST' and form.validate():
        #collect form data
        username = form.username.data
        email = form.email.data
        name = form.name.data

        #make sure user does not already exist
        if sql_helpers.isnewuser(username):
            #add the user to mysql and log them in
            password = passlib.hash.sha256_crypt.encrypt(form.password.data)
            users.insert(name,email,username,password)
            log_in_user(username)
            return flask.redirect(flask.url_for('dashboard'))
        else:
            flask.flash('User already exists', 'danger')
            return flask.redirect(flask.url_for('register'))

    return flask.render_template('register.html', form=form)

#Login page
@app.route("/login", methods = ['GET', 'POST'])
def login():
    #if form is submitted
    if flask.request.method == 'POST':
        #collect form data
        username = flask.request.form['username']
        candidate = flask.request.form['password']

        #access users table to get the user's actual password
        users = sql_helpers.Table("users", "name", "email", "username", "password")
        user = users.getone("username", username)
        accPass = user[-1]

        #if the password cannot be found, the user does not exist
        if accPass is None:
            flask.flash("Invalid Username/Password", 'danger')
            return flask.redirect(flask.url_for('login'))
        else:
            #verify that the password entered matches the actual password
            if passlib.hash.sha256_crypt.verify(candidate, accPass):
                #log in the user and redirect to Dashboard page
                log_in_user(username)
                flask.flash('You are now logged in.', 'success')
                return flask.redirect(flask.url_for('dashboard'))
            else:
                #if the passwords do not match
                flask.flash("Invalid Username/Password", 'danger')
                return flask.redirect(flask.url_for('login'))

    return flask.render_template('login.html')

#Transaction page
@app.route("/transaction", methods = ['GET', 'POST'])
@is_logged_in
def transaction():
    form = SendMoneyForm(flask.request.form)
    balance = sql_helpers.get_balance(flask.session.get('username'))

    #if form is submitted
    if flask.request.method == 'POST':
        try:
            #attempt to execute the transaction
            sql_helpers.send_money(flask.session.get('username'), form.username.data, form.amount.data)
            flask.flash("Money Sent!", "success")
        except Exception as e:
            flask.flash(str(e), 'danger')

        return flask.redirect(flask.url_for('transaction'))

    return flask.render_template('transaction.html', balance=balance, form=form, page='transaction')

#Buy page
@app.route("/buy", methods = ['GET', 'POST'])
@is_logged_in
def buy():
    form = BuyForm(flask.request.form)
    balance = sql_helpers.get_balance(flask.session.get('username'))

    if flask.request.method == 'POST':
        #attempt to buy amount
        try:
            sql_helpers.send_money("BANK", flask.session.get('username'), form.amount.data)
            flask.flash("Purchase Successful!", "success")
        except Exception as e:
            flask.flash(str(e), 'danger')

        return flask.redirect(flask.url_for('dashboard'))

    return flask.render_template('buy.html', balance=balance, form=form, page='buy')

#logout the user. Ends current session
@app.route("/logout")
@is_logged_in
def logout():
    flask.session.clear()
    flask.flash("Logout success", "success")
    return flask.redirect(flask.url_for('login'))

#Dashboard page
@app.route("/dashboard")
@is_logged_in
def dashboard():
    balance = sql_helpers.get_balance(flask.session.get('username'))
    blockchain = sql_helpers.get_blockchain().chain
    ct = time.strftime("%I:%M %p")
    return flask.render_template('dashboard.html', balance=balance, session=flask.session, ct=ct, blockchain=blockchain, page='dashboard')

#Index page
@app.route("/")
@app.route("/index")
def index():
    return flask.render_template('index.html')

#Run app
if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug = True)