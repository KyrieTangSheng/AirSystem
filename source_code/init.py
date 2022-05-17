#Project by Kyrie & Flora

#Import Flask library and other packages
from re import L
from tracemalloc import start
from flask import Flask, render_template, request, session, url_for, redirect
#Import for hashing password
from hashlib import md5
from graphviz import render
import pymysql.cursors
import datetime

#Initialize the app
#Including the path for css
app = Flask(__name__,
                static_url_path="/",
                static_folder="static")

#Configure MySQL
#Using database airsystem
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airsystem',
                        )

#--------------------------------------------------------------------------------------------------
#Hello Page
#Define a route to hello function
@app.route('/')
def hello():
    #default usertype here
    session["usertype"] = "public"
    return render_template('index.html')

#--------------------------------------------------------------------------------------------------
#Login
#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#seperate login page for different type of users
@app.route('/login_c')
def login_c():
    return render_template('login_c.html')

@app.route('/login_s')
def login_s():
    return render_template('login_s.html')

@app.route('/login_b')
def login_b():
    return render_template('login_b.html')


#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    usertype = request.form['usertype']
    #hash password
    md5_pw = md5(password.encode('utf8')).hexdigest()
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    if usertype == "customer":
        query = 'SELECT * FROM customer WHERE email = %s and password = %s'
        cursor.execute(query, (username, md5_pw))
    elif usertype == "booking_agent":
        query = 'SELECT * FROM booking_agent WHERE email = %s and password = %s'
        cursor.execute(query, (username, md5_pw))
    elif usertype == "staff":
        query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
        cursor.execute(query, (username, md5_pw))
    #stores the results in a variable
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        session['usertype'] = usertype
        if usertype == "booking_agent":
            return redirect(url_for('home_b'))
        elif usertype == "customer":
            return redirect(url_for('home_c'))
        else:
            session['company'] = data[5]
            session['Admin'] = 0
            session['Operator'] = 0
            return redirect(url_for('home_s'))
    else:
        #returns an error message to the html page
        error = 'Error: Invalid login or username'
        return render_template('login.html', error=error)


#--------------------------------------------------------------------------------------------------
#Register
#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/register_c')
def register_c():
	return render_template('register_c.html')

@app.route('/register_b')
def register_b():
	return render_template('register_b.html')

@app.route('/register_s')
def register_s():
	return render_template('register_s.html')


#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    #hashing password
    md5_pw = md5(password.encode('utf8')).hexdigest()
    usertype = request.form['usertype']

	#cursor used to send queries
    cursor = conn.cursor()

	#executes query
    if usertype == 'booking_agent':
        query = 'SELECT * FROM booking_agent WHERE email = %s'
        cursor.execute(query, (username))
    elif usertype == 'customer':
        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, (username))
    elif usertype == 'staff':
        query = 'SELECT * FROM airline_staff WHERE username = %s'
        cursor.execute(query, (username))

	#stores the results in a variable
    data = cursor.fetchone()

    error = None
    if(data):
	    #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        if usertype == 'booking_agent':
            ins = 'INSERT INTO booking_agent VALUES(%s, %s, %s)'
            booking_id = request.form['booking_agent_id']
            cursor.execute(ins, (username, md5_pw,booking_id))


        elif usertype == 'customer':
            ins = "INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            name = request.form['name']
            building_number = request.form['building_number']
            street = request.form['street']
            city = request.form['city']
            state = request.form['state']
            phone_number = request.form['phone_number']
            passport_number = request.form['passport_number']
            passport_expiration = request.form['passport_expiration']
            passport_country = request.form['passport_country']
            date_of_birth = request.form['date_of_birth']
            cursor.execute(ins,(username, name, md5_pw, building_number,street, city, state,phone_number, passport_number,  passport_expiration, passport_country, date_of_birth))
        elif usertype == 'staff':
            airlineName = request.form['airline_name']
            #Check if the airline exists
            query = 'SELECT * FROM airline WHERE airline_name = %s'
            cursor.execute(query, (airlineName))
            data1 = cursor.fetchone()
            if (not data1):
                error = "No such Airline existing in the system!"
                return render_template('register.html',error = error)
            ins = "INSERT INTO airline_staff VALUES(%s, %s, %s,%s, %s, %s)"
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            date_of_birth = request.form['date_of_birth']
            airline_name = request.form['airline_name']
            cursor.execute(ins,(username, md5_pw, first_name, last_name, date_of_birth, airline_name))

        conn.commit()
        cursor.close()
        return render_template('index.html',error = 'Successfully Registered!')


#--------------------------------------------------------------------------------------------------
# Homes
# create different homes for different types of users

# Booking agent's Home
@app.route('/home_b', methods = ['GET', 'POST'])
def home_b():
    username = session['username']
    usertype = session['usertype']
    # company = session['airline_name']
    return render_template('home_b.html', username = username, usertype = usertype)


# Customer's Home
@app.route('/home_c', methods = ['GET', 'POST'])
def home_c():
    username = session['username']
    usertype = session['usertype']
    return render_template('home_c.html', username = username, usertype = usertype)


# Airline staff's Home
@app.route('/home_s', methods = ['GET', 'POST'])
def home_s():
    username = session['username']
    usertype = session['usertype']
    company = session['company']

    cursor = conn.cursor()
    #check if the staff has Admin permission
    admin_permission = "Admin"
    query = "SELECT * FROM \
        airline_staff NATURAL JOIN permission\
        WHERE username = %s AND permission_type = %s  "
    cursor.execute(query,(username,admin_permission))
    data1 = cursor.fetchone()
    #Check if the staff has Operator permission
    operator_permission = "Operator"
    query = "SELECT * FROM \
        airline_staff NATURAL JOIN permission\
        WHERE username = %s AND permission_type = %s  "
    cursor.execute(query,(username,operator_permission))
    data2 = cursor.fetchone()
    cursor.close()

    session['Admin'] = 1 if data1 else 0
    session['Operator'] = 1 if data2 else 0
    Admin = session['Admin']
    Operator = session["Operator"]

    return render_template('home_s.html', username = username, usertype = usertype, company = company,Admin=Admin,Operator=Operator)

#--------------------------------------------------------------------------------------------------
# Public Information
@app.route('/public_info', methods = ["GET", "POST"])
def public_info():
    usertype = session['usertype']
    return render_template('public_info.html', usertype = usertype)

#--------------------------------------------------------------------------------------------------
#Search for flights
@app.route('/search_flights', methods = ["GET", "POST"])
def search_flights():
    #get information
    choice = request.form["city_or_airport"]
    dep = request.form["departure"]
    arr = request.form["arrival"]
    date = request.form["date"]

    usertype = session['usertype']

    cursor = conn.cursor()

    cities = queryfor("airport_city")
    airports = queryfor("airport_name")

    if ((dep not in cities) or (arr not in cities)) and choice == "city":
        error1 = "The city name is incorrect, please fill in again."
        return render_template('public_info.html',  error = error1, usertype = usertype)

    if ((dep not in airports) or (arr not in airports)) and choice == "airport":
        error1 = "The airport name is incorrect, please fill in again."
        return render_template('public_info.html',  error = error1, usertype = usertype)

    message = "There is no corresponding flight info."
    if choice == "city":

        data1 = search_c(date, dep, arr)
        if data1:
            return render_template('public_flight_info.html', rows=data1, usertype = usertype)

    else:
        data2 = search_a(date, dep, arr)
        if data2:
            return render_template('public_flight_info.html', rows=data2, usertype = usertype)
    return render_template("public_info.html", message = message, usertype = usertype)

def search_c(date, dep, arr):
    date = "%"+date+"%"
    usertype = session['usertype']

    cursor = conn.cursor()
    search = 'SELECT * from flight\
             where status = "upcoming" and departure_time like %s\
              and departure_airport in \
              (select airport_name from airport where airport_city = %s)\
               and arrival_airport in (select airport_name from airport where airport_city = %s)'
    cursor.execute(search,(date, dep, arr))
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return data

def search_a(date, dep, arr):
    date = "%"+date+"%"
    usertype = session['usertype']
    cursor = conn.cursor()
    search = 'SELECT * from flight where status = "upcoming" and departure_time \
                like %s and departure_airport = %s and arrival_airport = %s'
    cursor.execute(search,(date, dep, arr))
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return data

def queryfor(s):
    usertype = session['usertype']

    cursor = conn.cursor()
    query = "SELECT "+s+" from airport"
    cursor.execute(query)
    xdata = cursor.fetchall()
    x = []
    for i in xdata:
        x.append(i[0])
    return x

#--------------------------------------------------------------------------------------------------
#Find flight status
@app.route('/find_status', methods = ["GET", "POST"])
def find_status():
    choice = request.form["dep_or_arr"]
    flight_num = request.form["flight_num"]
    date = request.form["date"]
    usertype = session['usertype']

    #dep case
    if choice == "dep":
        data1 = dep_status(date, flight_num)

        if data1:
            return render_template('public_flight_info2.html', rows=data1, usertype = usertype)

    #arr case
    if choice == "arr":
        data2 = arr_status(date, flight_num)
        if data2:
            return render_template('public_flight_info2.html', rows=data2, usertype = usertype)

    message = "There is no corresponding flight info."
    return render_template("public_info.html", message = message, usertype = usertype)


def dep_status(date, flight_num):
    cursor = conn.cursor()
    date = "%" + date + "%"
    query = "select airline_name, flight_num, STATUS from flight where departure_time like %s and flight_num = %s"
    cursor.execute(query,(date, flight_num))
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return data

def arr_status(date, flight_num):
    cursor = conn.cursor()
    date = "%" + date + "%"
    query = "select airline_name, flight_num, STATUS from flight where \
        arrival_time like %s and flight_num = %s"
    cursor.execute(query,(date, flight_num))
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return data

#--------------------------------------------------------------------------------------------------
#View my flight (c, b, s)
#The default message will automatically show when opening the page.
@app.route('/view_my_flight', methods = ["GET", "POST"])
def view_my_flight():
    username = session['username']
    usertype = session["usertype"]
    message = 'You have no upcoming flights.'
    if usertype == "customer":
        data = view_c()
    elif usertype == "booking_agent":
        data = view_b()
    elif usertype == "staff":
        data = view_s()

    if data:
        return render_template('view_my_flight.html', flight_info=data, usertype=usertype)

    return render_template('view_my_flight.html', message=message, flight_info=data, usertype=usertype)


def view_c():
    username = session['username']
    usertype = session["usertype"]
    cursor = conn.cursor()
    query = "Select * from flight\
         where status = 'upcoming' and flight_num in \
            (select flight_num from (purchases join ticket using(ticket_id)) where customer_email = %s)"
    cursor.execute(query,(username,))
    data = cursor.fetchall()
    return data

def view_b():
    username = session['username']
    usertype = session["usertype"]
    cursor = conn.cursor()
    query = "Select * from flight\
         where status = 'upcoming' and flight_num in \
            (select flight_num from (purchases join ticket using(ticket_id)) join booking_agent\
            using(booking_agent_id) where booking_agent.email = %s)"
    cursor.execute(query,(username,))
    data = cursor.fetchall()
    return data

def view_s():
    username = session['username']
    usertype = session["usertype"]
    cursor = conn.cursor()
    query = query = "Select * from flight\
         where status = 'upcoming' and airline_name = \
            (select airline_name from airline_staff where username = %s) and departure_time <= date_add(now(),INTERVAL 30 DAY)"
    cursor.execute(query,(username,))
    data = cursor.fetchall()
    return data

#This is for specific searching based on airport/city or range of date.
@app.route('/view_my_flight_specific', methods = ["GET", "POST"])
def view_my_flight_s():
    username = session['username']
    usertype = session["usertype"]
    start = request.form["start"]
    end = request.form["end"]
    if start != "" and end != "":
        have_date = True
    else:
        have_date = False

    d_name = request.form["d_name"]
    a_name = request.form["a_name"]

    cities = queryfor("airport_city")

    if not d_name and not a_name:
        have_city = False
    elif d_name in cities and a_name in cities:
        have_city = True
    else:
        message = "Invalid city name"
        return render_template('view_my_flight.html', message=message, usertype=usertype)

    data, data1, data2 = (), (), ()

    if have_date:
        data1 = querybydate(start, end)

    if have_city:
        d_name = "%" + d_name + "%"
        a_name = "%" + a_name + "%"
        data2 = querybycity(d_name, a_name)

    if not have_date and not have_city:
        message = 'Please put in specifc information to search'
        return render_template('view_my_flight.html', message=message, usertype=usertype)
    else:
        if have_city:
            if have_date:
                data = []
                for i in list(data1):
                    if i in list(data2):
                        data.append(i)
            else:
                data = data2
        else:
            data = data1


    if data == () or data == []:
        message = 'You have no corresponding upcoming flights.'
        return render_template('view_my_flight.html', message=message, usertype=usertype)
    return render_template('view_my_flight.html', flight_info=data, usertype=usertype)

def querybydate(start, end):
    cursor = conn.cursor()
    querymap = {"customer": "Select * from flight\
         where (departure_time between %s and %s) and flight_num in \
            (select flight_num from (purchases join ticket using(ticket_id)) where customer_email = %s)",
            "booking_agent": "Select * from flight\
         where (departure_time between %s and %s) and flight_num in \
            (select flight_num from (purchases join ticket using(ticket_id))\
             join booking_agent using(booking_agent_id) where \
                booking_agent.email = %s)",
                "staff": "Select * from flight\
         where (departure_time between %s and %s) and airline_name = \
            (select airline_name from airline_staff where username = %s)"
    }
    username = session['username']
    usertype = session["usertype"]
    query = querymap[usertype]
    cursor.execute(query,(start, end, username))
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    print(data)
    return data

def querybycity(d_name, a_name):
    cursor = conn.cursor()
    querymap = {"customer": "Select * from flight\
         where departure_airport in (select airport_name from airport \
            where airport_city like %s) \
            and arrival_airport in \
            (select airport_name from airport where airport_city like %s) and flight_num in \
            (select flight_num from (purchases join ticket using(ticket_id)) where customer_email = %s)",
            "booking_agent": "Select * from flight\
         where departure_airport in (select airport_name from airport \
            where airport_city like %s) and arrival_airport in \
            (select airport_name from airport where airport_city like %s) \
            and flight_num in \
            (select flight_num from (purchases join ticket using(ticket_id)) join booking_agent using(booking_agent_id) where \
            booking_agent.email = %s)",
                "staff": "Select * from flight\
         where departure_airport in (select airport_name from airport \
            where airport_city like %s) \
            and arrival_airport in (select airport_name from airport where airport_city like %s) and airline_name = \
            (select airline_name from airline_staff where username = %s)"}
    username = session['username']
    usertype = session["usertype"]
    query = querymap[usertype]
    cursor.execute(query,(d_name, a_name, username))
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return data

#----------------------Airline Staff Functions------------------
#--------------------------------------------------------------
#Get permissions
@app.route('/get_admin', methods = ["GET", "POST"])
def get_admin():
    username = session["username"]
    usertype = session['usertype']
    company = session['company']
    cursor = conn.cursor()
    ins = "INSERT INTO permission VALUES (%s,%s)"
    cursor.execute(ins,(username,"Admin"))
    conn.commit()
    cursor.close()
    session['Admin'] = 1
    return render_template('home_s.html', username = username, usertype = usertype, company = company,Admin=1,Operator=session['Operator'])

@app.route('/get_operator', methods = ["GET", "POST"])
def get_operator():
    username = session["username"]
    usertype = session['usertype']
    company = session['company']
    cursor = conn.cursor()
    ins = "INSERT INTO permission VALUES (%s,%s)"
    cursor.execute(ins,(username,"Operator"))
    conn.commit()
    cursor.close()
    session['Operator'] = 1
    return render_template('home_s.html', username = username, usertype = usertype, company = company,Admin=session["Admin"],Operator=1)

##For customers to get refund
@app.route('/cancel_flight', methods = ["GET", "POST"])
def cancel_flight():
    username = session['username']
    usertype = session['usertype']
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    cursor = conn.cursor()
    req = "SELECT * FROM purchases NATURAL JOIN ticket \
                WHERE customer_email = %s AND airline_name = %s AND flight_num = %s"
    cursor.execute(req,(username,airline_name,flight_num))
    data = cursor.fetchone()
    if data:
        ticket_id = data[0]
    else:
        ticket_id = -100

    de = "DELETE\
        FROM purchases \
        WHERE ticket_id = %s"
    cursor.execute(de,(ticket_id))
    conn.commit()

    de = "DELETE \
        FROM ticket \
        WHERE ticket_id = %s"
    cursor.execute(de,(ticket_id))
    conn.commit()
    cursor.close()
    return render_template('home_c.html', username = username, usertype = usertype)


# For airline staff to view customers in a certain flight
@app.route('/all_customers', methods = ["GET", "POST"])
def all_customers():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session['company']
    flight_num = request.form['flight_num']
    cursor = conn.cursor()
    check = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s"
    cursor.execute(check,(airline_name, flight_num))
    flights = cursor.fetchone()
    if (not flights):
        return render_template('view_customers.html',error = "No Such Flight",username = username, usertype=usertype)
    query = "SELECT c.email, c.name \
        FROM customer as c, ticket as t, purchases as p\
        WHERE c.email = p.customer_email AND t.ticket_id = p.ticket_id AND t.airline_name = %s AND t.flight_num = %s "
    cursor.execute(query,(airline_name, flight_num))
    customers = cursor.fetchall()
    cursor.close()
    return render_template('view_customers.html', error = "" , customers = customers, airline_name = airline_name, flight_num = flight_num, username = username, usertype=usertype)

#-------------------------------------------------------------------------------------------------
#For Airline Staff to create new flights
@app.route('/new_flight')
def new_flight():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    permission = session["Admin"]
    data = view_s()
    return render_template('new_flight.html',flight_info = data,message = "", username = username, usertype = usertype, airline_name = airline_name, permission = permission)

@app.route('/create_flight', methods = ["GET", "POST"])
def create_flight():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    permission = session["Admin"]
    flight_num = request.form["flight_num"]
    departure_airport = request.form["departure_airport"]
    departure_time = request.form["dep_time"]
    arrival_airport = request.form["arrival_airport"]
    arrival_time = request.form["arr_time"]
    price = request.form["price"]
    status = request.form["status"]
    airplane_id = request.form["airplane_id"]
    cursor = conn.cursor()
    try:
        ins = "INSERT INTO flight VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(ins, (airline_name,flight_num,departure_airport,departure_time,arrival_airport, arrival_time,price,status,airplane_id))
        conn.commit()
        message = "Successfully Created A New Airline"
    except:
        message = "Failed to Create. Please double-check the information you entered"
    cursor.close()
    data = view_s()
    return render_template('new_flight.html',flight_info=data,message = message, username = username, usertype = usertype, airline_name = airline_name, permission = permission)





#For Airline Staff to change the status of a flight
@app.route('/change_status', methods = ["GET", "POST"])
def change_status():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    flight_num = request.form['flight_num']
    status = request.form['status']
    cursor = conn.cursor()
    #check if the flight exists
    query = "SELECT * FROM flight WHERE flight_num = %s"
    cursor.execute(query, (flight_num))
    data = cursor.fetchone()
    if data:
        update = "UPDATE flight SET status = %s WHERE flight_num = %s AND airline_name = %s"
        cursor.execute(update,(status,flight_num,airline_name))
        conn.commit()
        changed = 1
    else:
        changed = 2
    cursor.close()
    return render_template('home_s.html',changed = changed, username = username, usertype = usertype, company = airline_name,Admin=session["Admin"],Operator=session["Operator"])

#For Airline Staff to add a new airplane
@app.route('/add_airplane', methods = ["GET", "POST"])
def add_airplane():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    airplane_id = request.form['airplane_id']
    seats = request.form['seats']
    cursor = conn.cursor()
    #Check if the airplane id already exists
    query = "SELECT * FROM airplane WHERE airplane_id = %s"
    cursor.execute(query,(airplane_id))
    data = cursor.fetchone()
    if data:
        newPlane = 2
    else:
        ins = "INSERT INTO airplane VALUES (%s,%s,%s)"
        cursor.execute(ins,(airline_name,airplane_id,seats))
        conn.commit()
        newPlane = 1
    cursor.close()
    return render_template('home_s.html',newPlane = newPlane, username = username, usertype = usertype, company = airline_name,Admin=session["Admin"],Operator=session["Operator"])

#For Airline Staff to add a new airport
@app.route('/add_airport', methods = ["GET", "POST"])
def add_airport():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    airport_name = request.form['airport_name']
    airport_city = request.form['airport_city']
    cursor = conn.cursor()
    #Check if the airport name already exists
    query = "SELECT * FROM airport WHERE airport_name = %s"
    cursor.execute(query,(airport_name))
    data = cursor.fetchone()
    if (data):
        newPort = 2
    else:
        ins = "INSERT INTO airport VALUES (%s,%s)"
        cursor.execute(ins,(airport_name,airport_city))
        conn.commit()
        newPort = 1
    cursor.close()
    return render_template('home_s.html',newPort = newPort, username = username, usertype = usertype, company = airline_name,Admin=session["Admin"],Operator=session["Operator"])

#For Airline Staff to view top booking agents
@app.route('/view_top_ba', methods = ["GET", "POST"])
def view_top_ba():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    cursor = conn.cursor()
    ##Get top sales from last month
    query = "SELECT email, booking_agent_id, count(ticket_id) as sales\
        FROM (booking_agent NATURAL JOIN ticket NATURAL JOIN purchases)\
        WHERE airline_name = %s AND DateDiff(CURDATE(), purchase_date) <= 30 \
        GROUP BY email, booking_agent_id\
        ORDER BY sales DESC"
    cursor.execute(query,(airline_name))
    last_30_sales = cursor.fetchall()
    ##Get top sales from last year
    query = "SELECT email, booking_agent_id, count(ticket_id) as sales\
        FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket\
        WHERE airline_name = %s AND DateDiff(CURDATE(), purchase_date) <= 365 \
        GROUP BY email, booking_agent_id\
        ORDER BY sales DESC"
    cursor.execute(query,(airline_name))
    last_365_sales = cursor.fetchall()
    ##Get top commissions from last year
    query = "SELECT email, booking_agent_id, sum(price)*0.1 as commission \
        FROM ((booking_agent NATURAL JOIN purchases) NATURAL JOIN ticket) NATURAL JOIN flight\
        WHERE airline_name = %s AND DateDiff(CURDATE(), purchase_date) <= 365 \
        GROUP BY email, booking_agent_id\
        ORDER BY commission DESC"
    cursor.execute(query,(airline_name))
    last_365_commission = cursor.fetchall()
    cursor.close()
    return render_template('view_booking_agents.html',usertype = usertype,last_30_sales = last_30_sales,last_365_sales = last_365_sales, last_365_commission=last_365_commission)

#For Airline Staff to view most frequent customers
@app.route('/view_top_c', methods = ["GET", "POST"])
def view_top_c():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    cursor = conn.cursor()
    query = "SELECT email, name, count(purchases.ticket_id) as sales\
        FROM customer, ticket, purchases\
        WHERE airline_name = %s AND customer.email = purchases.customer_email\
        AND purchases.ticket_id = ticket.ticket_id AND DateDiff(CURDATE(), purchase_date) <= 365 \
        GROUP BY email, name \
        ORDER BY sales DESC"
    cursor.execute(query,(airline_name))
    last_365_purchase = cursor.fetchall()
    cursor.close()
    return render_template('view_top_customers.html',usertype=usertype,last_365_purchase = last_365_purchase)

#For Airline Staff to see all flights of a particular customer has on that airline
@app.route('/view_specific_c', methods = ["GET", "POST"])
def view_specific_c():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    customer_email = request.form['customer_email']
    cursor = conn.cursor()
    query = "SELECT flight_num, departure_airport, departure_time, arrival_airport, arrival_time,status,price\
        FROM flight NATURAL JOIN purchases NATURAL JOIN ticket\
        WHERE customer_email = %s AND airline_name = %s"
    cursor.execute(query,(customer_email,airline_name))
    info = cursor.fetchall()
    cursor.close()
    return render_template('view_specific_c.html',usertype=usertype,customer_email=customer_email,info=info)

#For Airline Staff to see the general sales report
@app.route('/view_report', methods = ["GET", "POST"])
def view_report():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    cursor = conn.cursor()
    #Get stats over the past 30 days
    query = "SELECT count(*) FROM ticket NATURAL JOIN purchases\
        WHERE airline_name = %s AND DateDiff(CURDATE(), purchase_date) <= 30"
    cursor.execute(query,(airline_name))
    sales_30 = cursor.fetchone()[0]
    #Get stats over the past 365 days
    query = "SELECT count(*) FROM ticket NATURAL JOIN purchases\
        WHERE airline_name = %s AND DateDiff(CURDATE(), purchase_date) <= 365"
    cursor.execute(query,(airline_name))
    sales_365 = cursor.fetchone()[0]
    #Get monthwise stats for last 12 months
    today = str(datetime.date.today())
    curr_year = int(today[:4])
    curr_month = int(today[5:7])
    years = [str(curr_year - 1) for i in range(12-curr_month)] + [str(curr_year) for i in range(curr_month)]
    months = [str(i) if i >= 10 else "0"+str(i) for i in range(curr_month+1,13)] + [str(i) if i >= 10 else "0"+str(i) for i in range(1,curr_month+1)]
    yms = [years[i]+"-"+months[i]+"-%" for i in range(12)]
    query = "SELECT count(*) FROM ticket NATURAL JOIN purchases\
        WHERE airline_name = %s AND purchase_date LIKE %s"
    monthwise_stats = []
    for ym in yms:
        cursor.execute(query,(airline_name,ym))
        monthwise_stats.append(cursor.fetchone()[0])
    return render_template('view_report.html',total=sum(monthwise_stats),yms=yms,usertype=usertype,sales_30=sales_30,sales_365=sales_365,monthwise_stats=tuple(monthwise_stats))

#For Airline Staff to see the specific date range's sales report
@app.route('/view_specific_report', methods = ["GET", "POST"])
def view_specific_report():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    cursor = conn.cursor()
    query = "SELECT count(*) FROM ticket NATURAL JOIN purchases\
        WHERE airline_name = %s AND purchase_date BETWEEN %s AND %s"
    cursor.execute(query,(airline_name,start_date,end_date))
    number = cursor.fetchone()[0]
    return render_template('view_report.html',specific = 1,usertype=usertype,number=number,start_date=start_date,end_date=end_date)

#For Airline Staff to see Comparison of Revenues
@app.route('/compare_rev', methods = ["GET", "POST"])
def compare_rev():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    cursor = conn.cursor()
    #Get direct revenue last month
    query = "SELECT sum(price)\
        FROM flight NATURAL JOIN ticket NATURAL JOIN purchases\
        WHERE airline_name = %s AND booking_agent_id is Null AND DateDiff(CURDATE(), purchase_date) <= 30"
    cursor.execute(query,(airline_name))
    dir_30 = cursor.fetchone()[0]
    dir_30 = dir_30 if dir_30 is not None else 0
    #Get indirect revenue last month
    query = "SELECT 0.9*sum(price)\
        FROM flight NATURAL JOIN ticket NATURAL JOIN purchases\
        WHERE airline_name = %s AND booking_agent_id is not Null AND DateDiff(CURDATE(), purchase_date) <= 30"
    cursor.execute(query,(airline_name))
    indir_30 = cursor.fetchone()[0]
    indir_30 = indir_30 if indir_30 is not None else 0
    #Get direct revenue last year
    query = "SELECT sum(price)\
        FROM flight NATURAL JOIN ticket NATURAL JOIN purchases\
        WHERE airline_name = %s AND booking_agent_id is Null AND DateDiff(CURDATE(), purchase_date) <= 365"
    cursor.execute(query,(airline_name))
    dir_365 = cursor.fetchone()[0]
    dir_365 = dir_365 if dir_365 is not None else 0
    #Get indirect revenue last year
    query = "SELECT 0.9*sum(price)\
        FROM flight NATURAL JOIN ticket NATURAL JOIN purchases\
        WHERE airline_name = %s AND booking_agent_id is not Null AND DateDiff(CURDATE(), purchase_date) <= 365"
    cursor.execute(query,(airline_name))
    indir_365 = cursor.fetchone()[0]
    indir_365 = indir_365 if indir_365 is not None else 0
    cursor.close()
    return render_template('compare_revenue.html',usertype=usertype,dir_30=dir_30,dir_365=dir_365,indir_30=indir_30,indir_365=indir_365)

#For Airline Staff to see the 3 most popular destinations over the last three months
@app.route('/view_pop_dest', methods = ["GET", "POST"])
def view_pop_dest():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    cursor = conn.cursor()
    #Get most popular cities over last 3 months
    query = "SELECT airport.airport_city, count(ticket.ticket_id) as totalnum\
        FROM ticket NATURAL JOIN flight, airport \
        WHERE flight.airline_name = %s AND flight.arrival_airport = airport.airport_name \
            AND DateDiff(CURDATE(), flight.arrival_time) <= 90 \
        GROUP BY airport.airport_city\
        ORDER BY totalnum DESC"
    cursor.execute(query,(airline_name))
    rank_90 = cursor.fetchall()
    #Get most popular cities over last 12 months
    query = "SELECT airport.airport_city, count(ticket.ticket_id) as totalnum\
        FROM ticket NATURAL JOIN flight, airport \
        WHERE flight.airline_name = %s AND flight.arrival_airport = airport.airport_name \
            AND DateDiff(CURDATE(), flight.arrival_time) <= 365 \
        GROUP BY airport.airport_city\
        ORDER BY totalnum DESC"
    cursor.execute(query,(airline_name))
    rank_365 = cursor.fetchall()
    cursor.close()
    return render_template("view_pop_dest.html",rank_90 = rank_90,rank_365=rank_365,usertype=usertype)

#For Airline Staff to grant permission:
@app.route('/grant_permission', methods = ["GET", "POST"])
def grant_permission():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    staff_username = request.form["staff_username"]
    type = request.form["type"]
    cursor = conn.cursor()
    #Check if the staff belongs to the same Airline
    query = "SELECT * FROM airline_staff WHERE username = %s AND airline_name = %s"
    cursor.execute(query,(staff_username,airline_name))
    data = cursor.fetchone()
    if data:
        ins = "INSERT INTO permission VALUES (%s,%s)"
        try:
            cursor.execute(ins,(staff_username,type))
            conn.commit()
            grant = 1
        except:
            grant = 2
    else:
        grant = 2
    cursor.close()
    return render_template('home_s.html', grant = grant, username = username, usertype = usertype, company = airline_name,Admin=session['Admin'],Operator=session['Operator'])

#For Airline Staff to cancel permission:
@app.route('/cancel_permission', methods = ["GET", "POST"])
def cancel_permission():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    staff_username = request.form["staff_username"]
    type = request.form["type"]
    cursor = conn.cursor()
    #Check if the staff belongs to the same Airline
    query = "SELECT * FROM airline_staff WHERE username = %s AND airline_name = %s"
    cursor.execute(query,(staff_username,airline_name))
    data = cursor.fetchone()
    if data:
        upd = "DELETE FROM permission WHERE username = %s AND permission_type = %s"
        try:
            cursor.execute(upd,(staff_username,type))
            conn.commit()
            cancelled = 1
        except:
            cancelled = 2
    else:
        grant = 2
    cursor.close()
    return render_template('home_s.html', cancelled = cancelled, username = username, usertype = usertype, company = airline_name,Admin=session['Admin'],Operator=session['Operator'])


#For Airline Staff to Add Booking Agents:
@app.route('/add_ba', methods = ["GET", "POST"])
def add_ba():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    agent_email = request.form["agent_email"]
    cursor = conn.cursor()
    ins = "INSERT INTO booking_agent_work_for VALUES (%s,%s)"
    try:
        cursor.execute(ins,(agent_email,airline_name))
        conn.commit()
        added_ba = 1
    except:
        added_ba = 2
    cursor.close()
    return render_template('home_s.html', added_ba=added_ba, username = username, usertype = usertype, company = airline_name,Admin=session['Admin'],Operator=session['Operator'])

#For Airline Staff to Remove Booking Agents:
@app.route('/remove_ba', methods = ["GET", "POST"])
def remove_ba():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["company"]
    agent_email = request.form["agent_email"]
    cursor = conn.cursor()
    upd = "DELETE FROM booking_agent_work_for where email = %s AND airline_name = %s"
    try:
        cursor.execute(upd,(agent_email,airline_name))
        conn.commit()
        removed_ba = 1
    except:
        removed_ba = 2
    cursor.close()
    return render_template('home_s.html', removed_ba=removed_ba, username = username, usertype = usertype, company = airline_name,Admin=session['Admin'],Operator=session['Operator'])




#--------------------------------------------------------------------------------------------------
#Search for flights & purchase tickets (c, b)
@app.route('/purchase')
def purchase():
    username = session["username"]
    usertype = session["usertype"]
    return render_template('purchase.html', username = username, usertype = usertype)

@app.route('/search_flights_p', methods = ["GET", "POST"])
def search_flights_p():
    #get information

    choice = request.form["city_or_airport"]
    dep = request.form["departure"]
    arr = request.form["arrival"]
    date = request.form["date"]
    username = session["username"]
    usertype = session["usertype"]

    cursor = conn.cursor()
    workfor = None
    if usertype == "booking_agent":

        queryworkfor = "SELECT distinct airline_name from booking_agent_work_for where email = %s"
        cursor.execute(queryworkfor,(username))
        workfordata = cursor.fetchall()
        workfor = []
        for i in workfordata:
            workfor.append(i[0])

    cities = queryfor("airport_city")
    airports = queryfor("airport_name")

    if ((dep not in cities) or (arr not in cities)) and choice == "city":
        error1 = "The city name is incorrect, please fill in again."
        return render_template('purchase.html',  error = error1, usertype = usertype, workfor = workfor)

    if ((dep not in airports) or (arr not in airports)) and choice == "airport":
        error1 = "The airport name is incorrect, please fill in again."
        return render_template('purchase.html', error = error1, usertype = usertype, workfor = workfor)
    message = "There is no corresponding flight info."
    if choice == "city":
        data1 = search_c(date, dep, arr)
        if data1:
            return render_template("purchase.html", flight_info = data1, usertype = usertype, workfor = workfor)

    else:
        data2 = search_a(date, dep, arr)
        if data2:
            return render_template("purchase.html", flight_info = data2, usertype = usertype, workfor = workfor)
    return render_template("purchase.html", message = message, usertype = usertype, workfor = workfor)


@app.route('/purchasing', methods = ["GET", "POST"])
def purchasing():
    airline_name = request.form["airline_name"]
    flight_num = request.form["flight_num"]
    session["airline_name"] = airline_name
    session["flight_num"] = flight_num
    message1 = "The ticket of this flight is sold out. Please choose other flights."
    username = session["username"]
    usertype = session["usertype"]

    seat = get_seat(airline_name, flight_num)
    ticket = get_ticket(airline_name, flight_num)

    if ticket >= seat:
        session.pop('airline_name')
        session.pop('flight_num')
        return render_template("purchase.html", usertype = usertype, message1 = message1)

    return render_template("purchase_confirm.html", usertype = usertype, airline_name = airline_name, flight_num = flight_num)

def get_seat(airline_name, flight_num):
    cursor = conn.cursor()
    seatcount = "select seats from airplane natural join flight where flight.airline_name = %s and flight.flight_num = %s"
    cursor.execute(seatcount,(airline_name, flight_num))
    seat = cursor.fetchone()
    cursor.close()
    return seat[0]

def get_ticket(airline_name, flight_num):
    cursor = conn.cursor()
    ticketcount = "select count(*) from ticket where airline_name = %s and flight_num = %s"
    cursor.execute(ticketcount,(airline_name, flight_num))
    ticket = cursor.fetchone()
    cursor.close()
    return ticket[0]

@app.route('/confirm', methods = ["GET", "POST"])
def confirm():
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["airline_name"]
    flight_num = session["flight_num"]
    if usertype == "booking_agent":
        customer_email = request.form["customer_email"]

    #generate ticket_id
    cursor = conn.cursor()
    query_ticket_id = "SELECT MAX(ticket_id) + 1 FROM ticket;"
    cursor.execute(query_ticket_id)
    ticket_id = cursor.fetchall()
    ticket_id = ticket_id[0][0]
    conn.commit()
    cursor.close()

    if usertype == "customer":
        confirm_c(ticket_id, airline_name, flight_num)
    else:
        confirm_b(ticket_id, airline_name, flight_num, customer_email)

    session.pop('airline_name')
    session.pop('flight_num')
    message = "Successfully Purchased!"
    return render_template("purchase_confirm.html", message = message, usertype = usertype, airline_name = airline_name, flight_num = flight_num)

def confirm_c(ticket_id, airline_name, flight_num):
    username = session["username"]
    usertype = session["usertype"]
    cursor = conn.cursor()
    q1 = "Insert into ticket (ticket_id, airline_name, flight_num) values(%s, %s, %s)"
    q2 = "Insert into purchases (ticket_id, customer_email, purchase_date) values(%s, %s, CURDATE())"
    cursor.execute(q1,(ticket_id, airline_name, flight_num))
    conn.commit()
    cursor.execute(q2,(ticket_id, username))
    conn.commit()
    cursor.close()
    return True

def confirm_b(ticket_id, airline_name, flight_num,customer_email):
    username = session["username"]
    usertype = session["usertype"]
    cursor = conn.cursor()
    query = "select booking_agent_id from booking_agent where email = %s"
    q1 = "Insert into ticket (ticket_id, airline_name, flight_num) values(%s, %s, %s)"
    q2 = "Insert into purchases (ticket_id, customer_email, booking_agent_id, purchase_date) values(%s, %s, %s, CURDATE())"
    cursor.execute(query,(username,))
    booking_agent_id = cursor.fetchone()
    cursor.execute(q1,(ticket_id, airline_name, flight_num))
    conn.commit()
    cursor.execute(q2,(ticket_id, customer_email, booking_agent_id[0]))
    conn.commit()
    cursor.close()
    return True

#--------------------------------------------------------------------------------------------------


# Track my spending (c)
@app.route('/spending')
def spending():
    return render_template('spending.html')

@app.route('/spend', methods = ["GET", "POST"])
def spend():
    username = session["username"]
    usertype = session["usertype"]
    start = request.form["start"]
    end = request.form['end']
    choice = request.form["choice"]
    cursor = conn.cursor()

    # default
    if choice == "default":
        a, b = spend_def(12, 6)

        return render_template('spending.html', spending = a, spent = b)

    elif choice == "specify":
        a, b = spend_spe(start, end)

    return render_template('spending.html', spending = a, spent = b)

def spend_def(x, y):
    username = session["username"]
    usertype = session["usertype"]
    cursor = conn.cursor()
    year = "select sum(price) from (purchases natural join ticket) natural join flight where customer_email = %s\
         and purchase_date > date_sub(now(),INTERVAL "+str(x)+" MONTH) AND purchase_date < now()"

    month = "select sum(price), convert(purchase_date, varchar(7)) as S from (purchases natural join ticket) natural join\
         flight where purchases.customer_email = %s and purchase_date > date_sub(now(),INTERVAL "+str(y)+" MONTH) AND purchase_date < now() group by S"
    cursor.execute(year,(username,))
    spending = cursor.fetchone()[0]
    cursor.execute(month,(username,))
    spent = cursor.fetchall()
    return spending, spent

def spend_spe(start,end):
    username = session["username"]
    usertype = session["usertype"]
    cursor = conn.cursor()
    month = "select sum(price) as S from purchases natural join ticket natural join flight where customer_email = %s\
             and purchase_date between %s and %s"

    monthwise = "select sum(price) as S,convert(purchase_date, varchar(7)) as T from purchases natural join ticket natural join\
         flight where purchases.customer_email = %s and purchase_date between %s and %s group by T"
    cursor.execute(month,(username, start, end))
    spending = cursor.fetchone()[0]
    cursor.execute(monthwise,(username, start, end))
    spent = cursor.fetchall()
    return spending, spent

#--------------------------------------------------------------------------------------------------
# View my commission (b)
@app.route('/commission')
def commission():
    return render_template('commission.html')

@app.route('/view_commission', methods = ["GET", "POST"])
def view_commission():
    username = session["username"]
    usertype = session["usertype"]

    cursor = conn.cursor()
    choose = request.form["choose"]
    start = request.form["start"]
    end = request.form["end"]
    # get booking agent ID
    get = "select booking_agent_id from booking_agent where email = %s"
    cursor.execute(get,(username,))
    booking_agent_id = cursor.fetchone()[0]

    #default case
    if choose == "yes":
        a, b, c = com_def(booking_agent_id)

    #specify case
    elif choose == "no":
        a, b, c = com_spe(booking_agent_id, start, end)

    return render_template("commission.html", total_commission = a, average_commission = b, total_ticket = c, username = username)

def com_def(booking_agent_id, x=1):
    username = session["username"]
    usertype = session["usertype"]
    cursor = conn.cursor()
# compute total commission
    com = "SELECT sum(flight.price * 0.1) from flight natural join ticket natural join purchases where booking_agent_id = %s \
            and purchase_date >= date_sub(now(),INTERVAL " + str(x) +" MONTH)"
# compute total ticket sold
    tick = "SELECT count(ticket_id) from ticket natural join purchases where booking_agent_id = %s and \
            purchase_date >= date_sub(now(),INTERVAL "+str(x)+" MONTH)"
    cursor.execute(com,(booking_agent_id,))
    total_commission = cursor.fetchone()[0]
    cursor.execute(tick,(booking_agent_id,))
    total_ticket = cursor.fetchone()[0]

    if total_ticket:
        average_commission = total_commission / total_ticket
    else:
        average_commission = 0
    if total_commission == None:
        total_commission = 0
    if total_ticket == None:
        total_ticket = 0
    return round(total_commission, 2), round(average_commission, 2), round(total_ticket, 2)

def com_spe(booking_agent_id, start, end):
    username = session["username"]
    usertype = session["usertype"]
    cursor = conn.cursor()
# compute total commission
    com = "SELECT sum(flight.price * 0.1) as S from (flight natural join ticket) natural join purchases where booking_agent_id = %s \
            and purchase_date between %s and %s"

# compute total ticket sold
    tick = "SELECT count(ticket_id) as S from ticket natural join purchases where booking_agent_id = %s and \
            purchase_date between %s and %s"

    cursor.execute(com,(booking_agent_id, start, end))
    total_commission = cursor.fetchone()[0]
    cursor.execute(tick,(booking_agent_id, start, end))
    total_ticket = cursor.fetchone()[0]

    if total_ticket:
        average_commission = total_commission / total_ticket
    else:
        average_commission = 0
    if total_commission == None:
        total_commission = 0
    if total_ticket == None:
        total_ticket = 0
    return round(total_commission, 2), round(average_commission, 2), round(total_ticket, 2)

#--------------------------------------------------------------------------------------------------
# View top customers (b)
@app.route('/customers')
def customers():

    username = session["username"]
    usertype = session["usertype"]

    cus1 = top_cust_tickets(6)
    cus2 = top_cust_com(12)
    return render_template('customers.html', customer = cus1, customer_y = cus2)

def top_cust_tickets(x):
    cursor = conn.cursor()

    username = session["username"]
    usertype = session["usertype"]
    q = "select customer_email, name, count(*) as S from (purchases natural join booking_agent) inner join customer on customer_email\
             = customer.email where purchase_date >= date_sub(now(),INTERVAL " + str(x) + " MONTH) and booking_agent.email = %s  \
                 group by customer.email order by S DESC limit 5"
    cursor.execute(q,(username,))
    customer = cursor.fetchall()
    conn.commit()
    cursor.close()

    return customer

def top_cust_com(x):
    cursor = conn.cursor()

    username = session["username"]
    usertype = session["usertype"]
    q = "select customer_email, name, sum(price * 0.1) as S from (purchases natural join ticket natural join flight natural join booking_agent)\
             inner join customer on customer_email = customer.email where purchase_date >= date_sub(now(),INTERVAL " + str(x) + " MONTH) and booking_agent.email = %s \
                 group by customer.email order by S DESC limit 5"

    cursor.execute(q,(username,))
    customer = cursor.fetchall()
    conn.commit()

    cursor.close()
    return customer

#--------------------------------------------------------------------------------------------------
# logout (c, b, s)
@app.route('/logout')
def logout():
    message = "goodbye" + session['username']
    session.pop('username')
    session.pop('usertype')
    return redirect('/login')

#--------------------------------------------------------------------------------------------------
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 3000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 3000, debug = True)
