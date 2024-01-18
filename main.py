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



@app.route('/shop', methods=["GET"])
def Shop():
    return render_template('Shop.html')

# ---------BELOW ALL ADMIN --------


@app.route('/adminLogin', methods=["GET"])
def LoginAdmin():
    return render_template('LoginAdmin.html')



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
        
        return render_template('Dashboard.html')
    
    else:
        return redirect(url_for('LoginAdmin'))




@app.route('/logout', methods=['GET', 'POST'])
def LogOut():
    session.clear()
    return render_template('Landing.html')

@app.route('/listOrder', methods=["GET", "POST"])
def ListOrder():
    if 'email' in session:
        return render_template('OrderList.html')
    else:
        return redirect('/adminLogin')


@app.route('/addOrder', methods=["GET", "POST"])
def AddOrder():
    if 'email' in session:
        return render_template('AddOrder.html')

    else:
        return redirect('/adminLogin')

@app.route('/products', methods=['GET', "POST"])
def Products():
    if 'email' in session:
        allProducts = GetAllProducts()
        return render_template('Products.html', products=allProducts, len=len(allProducts))
    else:
        return redirect('/adminLogin')


@app.route('/addProduct', methods=["GET"])
def RenderProduct():
    if 'email' in session:
        return render_template('AddProduct.html')

    else:
        return redirect('/adminLogin')


#add Product to database firestore
@app.route('/addProduct', methods=["POST"])
def AddProduct():
    if 'email' in session:
        if request.method == "POST":
            productName = request.form.get('productName')
            productPrice = float(request.form.get('productPrice'))
            productDescription = request.form.get('productDescription')
            productImage = request.form.get('productImage')

            product_data = {
                'ProductName': productName,
                'ProductPrice': productPrice,
                'ProductDescription': productDescription,
                'ProductImage': productImage
            }

            product_ref = db.collection('Products')
            product_ref.add(product_data)

            return redirect('/products')

    else:
        return redirect('/adminLogin')


        

def GetAllProducts():
    allProducts = db.collection('Products')
    products = []
    for doc in allProducts.stream():
        products.append(doc.to_dict())

    return products
    




app.run(host='0.0.0.0', port=5000, debug=True)
