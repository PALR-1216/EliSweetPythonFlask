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
    # get all my products here
    allProduct = GetAllActiveProducts()
    print(allProduct)


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
            selectOption = request.form.get('OptionSelect')

            product_data = {
                'ProductName': productName,
                'ProductPrice': productPrice,
                'ProductDescription': productDescription,
                'ProductImage': productImage,
                'selectOption':selectOption
            }

            product_ref = db.collection('Products')
            product_ref.add(product_data)

            return redirect('/products')

    else:
        return redirect('/adminLogin')


@app.route('/editProduct/<productID>')
def EditProduct(productID):
    if 'email' in session:
        product_details = Get_product_details(productID)
        if product_details:
            return render_template('EditProduct.html', product_details=product_details, ID=productID)



    else:
        return redirect('/adminLogin')


@app.route('/updateProduct/<id>', methods=["POST"])
def UpdateProduct(id):
    if 'email' in session:
        if request.method == "POST":
            productName = request.form.get('productName')
            productPrice = float(request.form.get('productPrice'))
            productDescription = request.form.get('productDescription')
            productImage = request.form.get('productImage')
            selectOption = request.form.get('OptionSelect')

            product_data = {
                'ProductName': productName,
                'ProductPrice': productPrice,
                'ProductDescription': productDescription,
                'ProductImage': productImage,
                'selectOption':selectOption
            }
            product_ref = db.collection('Products').document(id)
            product_ref.update(product_data)

            return redirect('/products')




    else:
        return redirect('/adminLogin')

@app.route('/deleteProduct/<id>', methods=["GET"])
def DeleteProduct(id):
    if 'email' in session:
        product_details = Get_product_details(id)
        if product_details:
            return render_template('VerifyDelete.html', id=id, product_details = product_details)
            


    else:
        return redirect('/adminLogin')



            
@app.route('/deleteProductID/<id>', methods=["GET"])
def DeleteID(id):
    # delete product in firestore
    if 'email' in session:
        product_ref = db.collection('Products').document(id)
        product_ref.delete()
        return redirect('/products')

    else:
        return redirect('/adminLogin')


def GetAllProducts():
    allProducts = db.collection('Products')
    products = []
    for doc in allProducts.stream():
        product_data = doc.to_dict()
        # Add document ID to the dictionary
        product_data['id'] = doc.id
        products.append(product_data)

    return products

def GetAllActiveProducts():
    allProducts = db.collection('Products').where('selectOption', '==', 'Active')
    products = []
    for doc in allProducts.get():
        product_data = doc.to_dict()
        products.append(product_data)
    return products


def Get_product_details(ID):
    product_ref = db.collection('Products').document(ID)
    product_doc = product_ref.stream()
    if product_doc.exists:
        product_data = product_doc.to_dict()
        return product_data
    else:
        return None 



app.run(host='0.0.0.0', port=3000, debug=True)
