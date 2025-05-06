
# pip imports flask , flask_login, flask_login

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import datetime
import re


app = Flask(__name__)
app.secret_key = 'thisIsSecret' # would change for publication
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
	def __init__(self, id, email, password):
		self.id = id
		self.email = email
		self.password = password
		self.authenticated = False
		def is_active(self):
			return self.is_active()
		def is_anonymous(self):
			return False
		def is_authenticated(self):
			return self.authenticated
		def is_active(self):
			return True
		def get_id(self):
			return self.id

@login_manager.user_loader
def load_user(user_id):
	conn = sqlite3.connect('main.db')
	curs = conn.cursor()
	curs.execute("SELECT * from User where userID = (?)",(user_id,))
	row = curs.fetchone()
	if row is None:
		return None
	else:
		return User(int(row[0]), row[1], row[2])



@app.route('/')
@app.route('/home')
@app.route('/index')
def home():
	return render_template('index.html')


# Product routes
@app.route('/products/<product_type>')
def products(product_type):
	conn = sqlite3.connect('main.db')
	curs = conn.cursor()
	query = 'select productID, name, company, price, type, photoURL from Product where type = (?)'
	curs.execute(query, (product_type,))
	products = curs.fetchall()
	conn.close()

	if product_type == 'Solarpanel':
		strtype = 'Solar Panels'
	if product_type == 'EVcharger':
		strtype = 'EV Chargers'
	if product_type == 'HEMS':
		strtype = 'Home EMS\'s'

	return render_template('products.html', products=products, type=strtype)

@app.route('/product-details/<product_id>', methods=['GET', 'POST'])
def product_details(product_id):
	if request.method == 'GET':
		conn = sqlite3.connect('main.db')
		curs = conn.cursor()
		query = 'select * from Product where productID = (?)'
		curs.execute(query, (product_id,))
		product = curs.fetchone()
		conn.close()

		return render_template('product-details.html', product=product)

	if request.method == 'POST':
		session['product_data'] = product_id

		appointType = request.form.get('appoint')

		if appointType == 'consult':
			return redirect(url_for('conDateTime'))
		
		elif appointType == 'install':
			return redirect(url_for('inDateTime'))
	return render_template('product-details.html')



# Carbon footprint routes
@app.route('/reduce-carbon-footprint')
def reduceFootprint():
	return render_template('reduce-footprint.html')

@app.route('/calculate-carbon-footprint')
def calculateFootprint():
	return render_template('calculate-footprint.html')


# Energy usage routes
@app.route('/calculate-energy-usage')
def calculateUsage():
	conn = sqlite3.connect('main.db')
	curs = conn.cursor()
	query = 'select applianceID, name, avgWatts, avgTime from Appliance'
	curs.execute(query)
	appliances = curs.fetchall()
	conn.close()
	return render_template('calculate-usage.html', appliances=appliances)

@app.route('/calculate-energy-usage', methods=['GET', 'POST'])
def calculateUsage_post():
	total_energy = 0

	for key in request.form.keys():
		if key.startswith("minor-result"):
			total_energy += float(request.form[key]) if request.form[key] else 0

	return render_template('usage-results.html', total_energy=total_energy)

@app.route('/track-energy-usage')
@login_required
def trackUsage():
	return render_template('track-usage.html')

@app.route('/usage-results')
def usageResults():
	return render_template('usage-results.html')



# account routes
@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	conn = sqlite3.connect('main.db')
	curs = conn.cursor()
	email = request.form['email']
	
	curs.execute('select userID, email, password from User where email = (?)', (email,))
	row = curs.fetchone()
	if row == None:
		flash('Email or password was incorrect', 'error')
		return render_template('login.html')
	
	
	conn.close()

	row = list(row)

	liUser = User(int(row[0]), row[1], row[2])

	password = request.form['password']

	match = bcrypt.check_password_hash(liUser.password, password)

	if liUser.email == email and match:
		login_user(liUser, remember=request.form.get('rememberMe'))
		flash('Successfully logged in', 'success')
		return redirect(url_for('home'))
	else:
		flash('Email or password was incorrect', 'error')
		return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Successfully logged out', 'success')
	return redirect(url_for('home'))


@app.route('/sign-up')
def signUp():
	return render_template('sign-up.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def signUp_post():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	fname = request.form.get('fname')
	sname = request.form.get('sname')
	email = request.form.get('email')
	phone = request.form.get('phone')
	addrLine = request.form.get('addrline')
	townCity = request.form.get('towncity')
	county = request.form.get('county')
	postcode = request.form.get('postcode')

	password1 = request.form.get('password1')
	password2 = request.form.get('password2')

	specialpattern = r'[!@#$%^&*(),.?":{}|<>=]' # Disallow these
	passwordpattern = r'(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}' # Format for valid password

	# check if any input is empty
	if fname == '' or sname == '' or email == '' or phone == '' or addrLine == '' or townCity == '' or county == '' or postcode == '' or password1 == '' or password2 == '':
		flash('All inputs are required', 'error')

	# check passwords match
	if password1 != '' and password1 != password2:
		flash("Passwords must match", 'error')

	# check password is > 8 char, has capital, has lowercase, has number and no spec char
	if re.search(passwordpattern, password1) == None or re.search(specialpattern, password1) != None:
		flash('Password must be at least 8 characters long, have 1 uppercase letter, have 1 lowercase letter and 1 number and no special characters', 'error')

	# check fname is between 3-30 char and doesnt have special char
	if len(fname) < 3 or len(fname) > 30 or re.search(specialpattern, fname) != None:
		flash('Firstname must be between 3-30 letters long', 'error')

 	# check sname is between 3-50 char
	if len(sname) < 3 or len(sname) > 50 or re.search(specialpattern, sname) != None:
		flash('Surname must be between 3-50 letters long', 'error')

	# check email is less than 60 char
	if len(email) > 60:
		flash('Email must be less than 60 characters long', 'error')
    
    # check phone is equal to 11 char and starts with 0 and only contains numbers
	if len(phone) != 11:
		flash('Phone number must be 11 characters long', 'error')

	if len(phone) == 11 and re.search("[0-9]", phone) == None:
		flash('Phone number must be only numbers', 'error')

	if len(phone) == 11 and phone[0] != '0':
		flash('Phone number must start with a \'0\'', 'error')
	

    # check addrline is less than 255 char
	if len(addrLine) > 255 or re.search(specialpattern, addrLine) != None:
		flash('Address line must be less than 255 letters and numbers long', 'error')

    # check towncity is less than 255 char
	if len(townCity) > 255 or re.search(specialpattern, townCity) != None:
		flash('Town/City must be less than 255 letters long', 'error')

    # check county is less than 50 char
	if len(county) > 50 or re.search(specialpattern, county) != None:
		flash('County must be less than 50 letters long', 'error')

    # check postcode is 6-8 char
	if len(postcode) < 6 or len(postcode) > 8:
		flash('Postcode must be between 6-8 characters long', 'error')
	

	else:
		hashedPassword = bcrypt.generate_password_hash(password1)

		conn = sqlite3.connect('main.db')
		curs = conn.cursor()
		try:
			query = 'insert into User (firstname, surname,email, phoneNumber,addressLine, townCity,county, postcode,password) values (?,?,?,?,?,?,?,?,?)'

			curs.execute(query, (fname, sname, email, phone, addrLine, townCity, county, postcode, hashedPassword))

		except:
			conn.rollback()
		
		finally:
			conn.commit()
			conn.close()

		flash('Successfully created account. Please log in', 'success')
		return redirect(url_for('login'))
	
	return render_template('sign-up.html')



# appointment routes
@app.route('/installation-step1')
def inDateTime():
	return render_template('in-date-time.html')

@app.route('/installation-step1', methods=['GET', 'POST'])
def inDateTime_post():
	now = datetime.now()

	date = request.form.get('date')
	time = request.form['time']

	date_obj = datetime.strptime(date, "%Y-%m-%d")


	if date == None or time == None:
		flash('Inputs are required', 'error')
	
	if date_obj < now:
		flash('Date must be in the future', 'error')
		
	
	else:
		session['date'] = date
		session['time'] = time

		return redirect(url_for('inIdentifyDetails'))
	
	return render_template('in-date-time.html')


@app.route('/installation-step2')
def inIdentifyDetails():
	return render_template('in-identifying-details.html')

@app.route('/installation-step2', methods=['GET', 'POST'])
def inIdentifyDetails_post():

	fname = request.form.get('fname')
	sname = request.form.get('sname')
	email = request.form.get('email')
	phone = request.form.get('phone')
	addrLine = request.form.get('addrline')
	townCity = request.form.get('towncity')
	county = request.form.get('county')
	postcode = request.form.get('postcode')

	specialpattern = r'[!@#$%^&*(),.?":{}|<>=]' # Disallow these

	# check if any input is empty
	if fname == '' or sname == '' or email == '' or phone == '' or addrLine == '' or townCity == '' or county == '' or postcode == '':
		flash('All inputs are required', 'error')

	# check fname is between 3-30 char and doesnt have special char
	if len(fname) < 3 or len(fname) > 30 or re.search(specialpattern, fname) != None:
		flash('Firstname must be between 3-30 letters long', 'error')

 	# check sname is between 3-50 char
	if len(sname) < 3 or len(sname) > 50 or re.search(specialpattern, sname) != None:
		flash('Surname must be between 3-50 letters long', 'error')

	# check email is less than 60 char
	if len(email) > 60:
		flash('Email must be less than 60 characters long', 'error')
    
    # check phone is equal to 11 char and starts with 0 and only numbers
	if len(phone) != 11:
		flash('Phone number must be 11 characters long', 'error')

	if len(phone) == 11 and re.search("[0-9]", phone) == None:
		flash('Phone number must be only numbers', 'error')

	if len(phone) == 11 and phone[0] != '0':
		flash('Phone number must start with a \'0\'', 'error')
	

    # check addrline is less than 255 char
	if len(addrLine) > 255 or re.search(specialpattern, addrLine) != None:
		flash('Address line must be less than 255 letters and numbers long', 'error')

    # check towncity is less than 255 char
	if len(townCity) > 255 or re.search(specialpattern, townCity) != None:
		flash('Town/City must be less than 255 letters long', 'error')

    # check county is less than 50 char
	if len(county) > 50 or re.search(specialpattern, county) != None:
		flash('County must be less than 50 letters long', 'error')

    # check postcode is 6-8 char
	if len(postcode) < 6 or len(postcode) > 8 :
		flash('Postcode must be between 6-8 characters long', 'error')

	else:
		session['fname'] = request.form['fname']
		session['sname'] = request.form['sname']
		session['email'] = request.form['email']
		session['phone'] = request.form['phone']
		session['addrline'] = request.form['addrline']
		session['towncity'] = request.form['towncity']
		session['county'] = request.form['county']
		session['postcode'] = request.form['postcode']

		return redirect(url_for('inCardDetails'))
	return render_template('in-identifying-details.html')


@app.route('/installation-step3')
def inCardDetails():
	return render_template('in-card-details.html')

@app.route('/installation-step3', methods=['GET','POST'])
def inCardDetails_post():
	# this pages form inputs
	nameCard = request.form.get('namecard')
	cardNum = request.form.get('cardnum')
	secCode = request.form.get('seccode')
	expDate = request.form.get('expdate')
	
	# the product id for installing
	productid = session.get('product_data')

	# the date and time of the appointment
	date = session.get('date')
	time = session.get('time')
	
	# details of user
	fname = session.get('fname')
	sname = session.get('sname')
	email = session.get('email')
	phone = session.get('phone')
	addrLine = session.get('addrline')
	townCity = session.get('towncity')
	county = session.get('county')
	postcode = session.get('postcode')

	now = datetime.now()
	date_obj = datetime.strptime(expDate, "%Y-%m")
	print(now, date_obj)

	specialpattern = r'[!@#$%^&*(),.?":{}|<>=]' # Disallow these

	# presence check
	if nameCard == '' or cardNum == '' or secCode == '' or expDate == '':
		flash('All inputs are required', 'error')

	# check if nameCard is less than 90 and no special characters
	if len(nameCard) > 90 or re.search(specialpattern, nameCard) != None:
		flash('Name on card must be less than 90 letters long', 'error')

	# check if card num is equal to 16 char and is only numbers
	if len(cardNum) != 16 or re.search("[0-9]", cardNum) == None:
		flash('Card number must be 16 numbers long', 'error')

	if len(secCode) < 3 or len(secCode) > 4 or re.search("[0-9]", secCode) == None:
		flash('Security code must be 3-4 numbers long', 'error')

	if date_obj < now:
		flash('Date must be in the future', 'error')
	
	else:
		conn = sqlite3.connect('main.db')
		curs = conn.cursor()

		try:
			userQuery = 'insert into User (firstname, surname, email, phoneNumber, addressLine, townCity, county, postcode) values (?,?,?,?,?,?,?,?)'
			curs.execute(userQuery, (fname, sname, email, phone, addrLine, townCity, county, postcode))
			print('Success 1')
			
			userid = curs.lastrowid

			paymentQuery = 'insert into Payment (userID, nameOnCard, number, securityCode, expiryDate) values (?,?,?,?,?)'
			curs.execute(paymentQuery, (userid, nameCard, cardNum, secCode, expDate))
			print('Success 2')
			payid = curs.lastrowid

			installquery = 'insert into Installation (userID, productID, paymentID, date, time, status) values (?,?,?,?,?,?)'
			curs.execute(installquery, (userid, productid, payid, date, time, 'Paid'))
			print('Success 3')
		except:
			conn.rollback()
		finally:
			conn.commit()
			conn.close()

		flash('Successfully scheduled installation', 'success')
		return redirect(url_for('success'))
	return render_template('in-card-details.html')



@app.route('/consultation-step1')
def conDateTime():
	return render_template('con-date-time.html')

@app.route('/consultation-step1', methods=['GET', 'POST'])
def conDateTime_post():
	now = datetime.now()

	date = request.form.get('date')
	time = request.form['time']

	date_obj = datetime.strptime(date, "%Y-%m-%d")

	if date == None or time == None:
		flash('Inputs are required', 'error')
	
	if date_obj < now:
		flash('Date must be in the future', 'error')
	
	else:
		session['date'] = date
		session['time'] = time

		return redirect(url_for('conIdentifyDetails'))
	return render_template('con-date-time.html')


@app.route('/consultation-step2')
def conIdentifyDetails():
	return render_template('con-identifying-details.html')

@app.route('/consultation-step2', methods=['GET', 'POST'])
def conIdentifyDetails_post():
	productid = session.get('product_data')

	date = session.get('date')
	time = session.get('time')

	fname = request.form.get('fname')
	sname = request.form.get('sname')
	email = request.form.get('email')
	phone = request.form.get('phone')
	addrLine = request.form.get('addrline')
	townCity = request.form.get('towncity')
	county = request.form.get('county')
	postcode = request.form.get('postcode')

	specialpattern = r'[!@#$%^&*(),.?":{}|<>=]' # Disallow these

	# check if any input is empty
	if fname == '' or sname == '' or email == '' or phone == '' or addrLine == '' or townCity == '' or county == '' or postcode == '':
		flash('All inputs are required', 'error')

	# check fname is between 3-30 char and doesnt have special char
	if len(fname) < 3 or len(fname) > 30 or re.search(specialpattern, fname) != None:
		flash('Firstname must be between 3-30 letters long', 'error')

 	# check sname is between 3-50 char
	if len(sname) < 3 or len(sname) > 50 or re.search(specialpattern, sname) != None:
		flash('Surname must be between 3-50 letters long', 'error')

	# check email is less than 60 char
	if len(email) > 60:
		flash('Email must be less than 60 characters long', 'error')
    
    # check phone is equal to 11 char and starts with 0
	if len(phone) != 11:
		flash('Phone number must be 11 characters long', 'error')

	if len(phone) == 11 and re.search("[0-9]", phone) == None:
		flash('Phone number must be only numbers', 'error')

	if len(phone) == 11 and phone[0] != '0':
		flash('Phone number must start with a \'0\'', 'error')
	

    # check addrline is less than 255 char
	if len(addrLine) > 255 or re.search(specialpattern, addrLine) != None:
		flash('Address line must be less than 255 letters and numbers long', 'error')

    # check towncity is less than 255 char
	if len(townCity) > 255 or re.search(specialpattern, townCity) != None:
		flash('Town/City must be less than 255 letters long', 'error')

    # check county is less than 50 char
	if len(county) > 50 or re.search(specialpattern, county) != None:
		flash('County must be less than 50 letters long', 'error')

    # check postcode is 6-8 char
	if len(postcode) < 6 or len(postcode) > 8 :
		flash('Postcode must be between 6-8 characters long', 'error')

	
	else:
		conn = sqlite3.connect('main.db')
		curs = conn.cursor()

		try:
			userQuery = 'insert into User (firstname, surname, email, phoneNumber, addressLine, townCity, county, postcode) values (?,?,?,?,?,?,?,?)'
			curs.execute(userQuery, (fname, sname, email, phone, addrLine, townCity, county, postcode))
				
			userid = curs.lastrowid

			consultquery = 'insert into Consultation (userID, productID, date, time, status) values (?,?,?,?,?)'
			curs.execute(consultquery, (userid, productid, date, time, 'Booked'))

		except:
			conn.rollback()

		finally:
			conn.commit()
			conn.close()

		flash('Successfully scheduled consultation', 'success')
		return redirect(url_for('success'))
	
	return render_template('con-identifying-details.html')


@app.route('/manage-appointments')
@login_required
def manageAppointment():
	conn = sqlite3.connect('main.db')
	curs = conn.cursor()
	user_id = current_user.get_id()
	query = '''SELECT userID, date, time, name, status 
	FROM Consultation
	INNER JOIN Product On Product.productID = Consultation.productID
	WHERE userID = (?)'''
	curs.execute(query, (user_id,))
	appointments = curs.fetchall()
	return render_template('manage-appointment.html', appointments=appointments)



# other
@app.route('/settings')
def settings():
	return render_template('settings.html')

@app.route('/success')
def success():
	return render_template('conformation.html')

@app.route('/policies')
def policies():
	return render_template('privacy-cookie.html')



if __name__ == '__main__':
	app.run(debug=True)