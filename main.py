from flask import Flask, url_for, render_template, redirect, request, session
import os
import stripe
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask_session import sessions
from datetime import timedelta
import secrets


current_dir = os.path.dirname(os.path.realpath(__file__))
credentials_file_path = os.path.join(current_dir, 'eliSweets.json')
cred = credentials.Certificate(credentials_file_path)
firebase_admin.initialize_app(cred)


db = firestore.client()


app = Flask(__name__)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30).total_seconds()
app.secret_key = secrets.token_hex(8)



@app.route('/', methods=["GET"])
def Home():
    return render_template('Landing.html')


@app.route('/adminLogin', methods=["GET"])
def LoginAdmin():
    return render_template('LoginAdmin.html')


@app.route('/shop', methods=["GET"])
def Shop():
    return render_template('Shop.html')


@app.route('/authAdmin', methods=['POST'])

def Auth_Admin():
    if request.method == "POST":
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        user_ref = db.collection('Users')
        query = user_ref.where('email', '==', email).where('password', '==',password).get()
    if not query:
        return render_template('LoginAdmin.html',error="Invalid email or password")
    
    session['email'] = email
    return redirect(url_for('dashboard'))
    # return render_template('AdmindashBoard.html')




@app.route('/dashboard', methods=["GET"])
def dashboard():
    if 'email' in session:
        return render_template('dashboard.html')
    
    else:
        return redirect(url_for('LoginAdmin'))




@app.route('/logout', methods=['GET', 'POST'])
def LogOut():
    session.clear()
    return render_template('Landing.html')



app.run(host='0.0.0.0', port=5000, debug=True)
