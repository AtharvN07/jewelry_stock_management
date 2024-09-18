from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from werkzeug.utils import secure_filename
from barcode import Code128
from barcode.writer import ImageWriter

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'atharv'

# File upload folder
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration (ensure your MySQL server is running and credentials are correct)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="jewelry_manageme"
)

# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user from database
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']  # Store user id in session
            return redirect(url_for('add_item'))  # Redirect to add_item page
        else:
            # Invalid credentials, reload the login page with error message
            return render_template('login.html', error="Invalid Credentials")

    # Render the login page if it's a GET request
    return render_template('login.html')

# Add Item Page
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user_id' in session:  # Ensure user is logged in
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            photo = request.files['photo']
            barcode = request.form['barcode']

            # Save the photo to the specified upload folder
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Insert the new item into the database
            cursor = db.cursor()
            cursor.execute('INSERT INTO items (name, price, barcode, photo) VALUES (%s, %s, %s, %s)',
                           (name, price, barcode, filename))
            db.commit()

            # Generate and save the barcode image
            barcode_image = Code128(barcode, writer=ImageWriter())
            barcode_image.save(os.path.join(app.config['UPLOAD_FOLDER'], barcode))

            # Redirect to the billing page after adding the item
            return redirect(url_for('billing'))

        # Render the add_item page for GET requests
        return render_template('add_item.html')

    # If the user is not logged in, redirect to the login page
    return redirect(url_for('login'))

# Billing Page
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if 'user_id' in session:  # Ensure user is logged in
        if request.method == 'POST':
            barcode = request.form['barcode']
            quantity = int(request.form['quantity'])

            # Fetch the item based on the barcode
            cursor = db.cursor(dictionary=True)
            cursor.execute('SELECT * FROM items WHERE barcode=%s', (barcode,))
            item = cursor.fetchone()

            if item:
                subtotal = item['price'] * quantity
                total = subtotal  # Add any discounts or taxes as needed

                # Insert the transaction into the database
                cursor.execute('INSERT INTO transactions (item_id, quantity, subtotal, total) VALUES (%s, %s, %s, %s)',
                               (item['id'], quantity, subtotal, total))
                db.commit()

                # Return the billing page with item and total details
                return render_template('billing.html', item=item, quantity=quantity, subtotal=subtotal, total=total)

        # Render the empty billing page for GET requests
        return render_template('billing.html')

    # If the user is not logged in, redirect to the login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
