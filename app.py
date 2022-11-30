from flask import Flask, render_template , request , redirect , session
import pymongo                                         #to manage the relation with mongodb
import bcrypt                                          #crypt passwords
import bson                                            #Binary JSON
from sessionManagement import UserLogged               #to check if user is logged or not


###################-----------------------------###################
app = Flask(__name__)
app.secret_key = "SecretKey"


###################-----------------------------###################
# Connect to database 
client = pymongo.MongoClient('mongodb+srv://Sseddik:mlkj1234@cluster0.ev6jjvr.mongodb.net/test')
db = client["DataBaseTest"]


###################-----------------------------###################
#Question 1
#Login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.users.find_one({'email': email}) #See if the user already registered 
        if user is not None and bcrypt.checkpw(password.encode("utf-8"), user['password']):
            session["email"] = email
            return redirect("/users") 
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


###################-----------------------------###################
#Question 2
#Registration
@app.route('/register', methods=['GET','POST'])
def registration():
    print(db)
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user = db.users.find_one({'email': email})#See if the user already registered 
        if user is None and password == confirm_password:
            HashPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) #Hash the password
            # Insert new user in database
            print("trying")
            db.users.insert_one({
                'username': username,
                'email': email,
                'password': HashPassword,
                'balance' : 100 
            })
            return redirect("/login")
        else:
            
            return render_template('register.html')  #password and confirm password doesn't match
    else:
        print(request.method)
        return render_template('register.html')


###################-----------------------------###################
#Question 3
#profile and passowrd update
@app.route('/profile', methods=['GET' , 'POST'])
def profile():
    if UserLogged():
        if request.method == 'POST':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_new_password = request.form['confirm_password']
            user = db.users.find_one({'email': session['email']}) #See if the user already registered 
            # See if the the user exists and the confirm password and the new password matches
            if user is not None and bcrypt.checkpw(current_password.encode("utf-8"), user['password']) and new_password == confirm_new_password:
                HashPassword = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                # Change the password
                db.users.update_one({'email': session['email']}, {'$set': {'password': HashPassword}})
                return redirect("/profile")
            else:
                return render_template('profile.html')
        else:
            email = session["email"]
            user = db.users.find_one({'email': email})
            return render_template('profile.html', user=user)
    else:
        return redirect("/login")


###################-----------------------------###################
#Question 4
#List users 
@app.route('/users', methods=['GET'])
def list_users():
    if UserLogged():
        users = db.users.find()
        return render_template('users.html', users=users)
    else:
        return redirect("/login")


###################-----------------------------###################
#Question 5
#show user profile
@app.route('/showProfile/<id>', methods=['GET'])
def show_user_profile(id):
    if UserLogged():
        user = db.users.find_one({'_id': bson.ObjectId(id)})
        return render_template('showProfile.html', user=user)
    else:
        return redirect("/login")


###################-----------------------------###################
#Question 6
#send money 
@app.route('/sendMoney', methods=['GET' , 'POST'])
def send_money():
    if UserLogged():
        selectedUser = db.users.find_one({'_id' : bson.ObjectId(request.args.get('id'))})
        currentUser = db.users.find_one({'email': session['email']})
        users = db.users.find()
        if request.method == "GET":
            return render_template('sendMoney.html', selectedUser=selectedUser , currentUser=currentUser , users=users)
        else:
            money = request.form['money']
            user_id = request.form['user_id']

            #see if the balance is enough for the transaction
            if float(currentUser['balance']) >= float(money):
                #Add the amount to the selected user
                db.users.update_one({'_id': bson.ObjectId(user_id)}, {'$inc': {'balance': +float(money)}})
                #Remove the amount from the current user
                db.users.update_one({'email': session['email']}, {'$inc': {'balance': -float(money)}})
                return redirect("/users")
            else:
                return render_template('sendMoney.html', error="Not enough balance" , selectedUser=selectedUser , currentUser=currentUser , users=users)
    else:
        return redirect("/login")


@app.route('/')
def home():
     return redirect("/login")