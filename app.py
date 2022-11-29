from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route("/")
def home():
    return redirect ("/register")

@app.route("/register", methods =["POST", "GET"])
def register():
    form = RegisterForm()
    if "user_id" in session:
        user = User.query.filter_by(id=session["user_id"]).first()
        flash('You are alreayd logged in!', "primary")
        return redirect(f"/users/{user.username}")
    if form.validate_on_submit():
        username = form.username.data ## grab the username input
        password = form.password.data ## grab the password input
        email = form.email.data ## grab the email input
        first_name = form.first_name.data ## grab the first name input
        last_name = form.last_name.data ## grab the last name input
        new_user= User.register(username, password, email, first_name, last_name) ## create the new user using the .register method defined in models.py under User classmethod
        db.session.add(new_user) ## add that new user and commit it to the db
        db.session.commit()
        session['user_id'] = new_user.id ## store the newly registered user in the sesssion
        flash('You are in! Successfully Created Your Account!', "success") 
        return redirect(f"/users/{new_user.username}") ## redirect to /secret endpoint if successfully registered user
  
    return render_template("register.html", form=form) # render template on the get request or if validate fails


@app.route("/login", methods =["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data ## grab the username input
        password = form.password.data ## grab the password input
        user = User.authenticate(username, password)
        if user: ## if the user is returned AKA login has been successful and authenticated
            flash(f"Welcome Back, {user.username}!", "primary")
            session['user_id'] = user.id ## store that logged in user in the session
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.'] ## if it failed then we add this message to the errors list which will render in the template

    return render_template('login.html', form=form)


@app.route("/users/<username>")
def secret(username):
    """page that is displayed when user is logged in """
    user = User.query.filter_by(username=username).first()
    if "user_id" not in session:
        flash("Please login/register first!", "danger")
        return redirect('/')
    elif user.id != session["user_id"]:
        return redirect('/')
    
    all_feedback = Feedback.query.all()
    return render_template("secret.html", user=user, all_feedback= all_feedback)


@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/')

@app.route("/users/<username>/delete", methods =["POST"])
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user.id == session["user_id"]:
        feedback = Feedback.query.filter_by(username=user.username) ## getting the list of feedback that is made by that user
        for f in feedback: ## looping through all the feedback and deleting those first before we can delete user
            db.session.delete(f)
            db.session.commit()
        db.session.delete(user)
        db.session.commit()
        return redirect('/logout')
    flash("You don't have permission to do that!", "danger")
    return redirect('/')

@app.route("/users/<username>/feedback/add", methods =["POST", "GET"])
def add_feedback(username):
    if "user_id" not in session:
        flash("Please login/register first!", "danger")
        return redirect('/')

    user = User.query.filter_by(username=username).first()
    if user.id == session["user_id"]:
        form= FeedbackForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_feedback = Feedback(title=title, content=content, username = user.username)
            db.session.add(new_feedback)
            db.session.commit()
            flash('Feedback Created!', 'success')
            return redirect(f"/users/{user.username}")

        return render_template("feedback.html", form = form, user=user)
    
@app.route("/feedback/<int:feedback_id>/update", methods =["POST", "GET"])
def update_feedback(feedback_id):
    """Display a form to edit feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=feedback)
    if feedback.user.id == session["user_id"]:
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            flash('Feedback changes saved!', 'success')
            return redirect (f"/users/{feedback.user.username}")
    
    return render_template("editfeedback.html", form=form, feedback=feedback)

@app.route("/feedback/<int:feedback_id>/delete", methods =["POST"])
def delete_feedback(feedback_id):
    """Delete a specific piece of feedback and redirect to /users/<username>"""
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.user.id == session["user_id"]:
        db.session.delete(feedback)
        db.session.commit()
        flash('Deleted feedback', 'success')
        return redirect(f"/users/{feedback.user.username}")
    flash('You cant do that', 'danger')
    return redirect("/")

