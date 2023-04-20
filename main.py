from flask import *
from flask_mail import *
from flask_mysqldb import MySQL
from random import *
from datetime import timedelta
from MySQLdb import Binary
import datetime
import base64
import re
import configparser

app = Flask(__name__)
app.secret_key = "abc123"


config = configparser.ConfigParser()
config.read('config.ini')

host = config.get('database','host')
user = config.get('database','user')
port = config.get('database','port')
db = config.get('database','db')
server = config.get('mail','server')
username = config.get('mail','username')
mailport = config.get('mail','mailport')
password = config.get('mail','password')

app.secret_key="keyvalue"
app.config["MYSQL_HOST"] = host
app.config["MYSQL_USER"] = user
app.config["MYSQL_PORT"] = int(port)
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = db
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

mysql = MySQL(app)

app.config["MAIL_SERVER"] = server
app.config["MAIL_USERNAME"] = username
app.config["MAIL_PORT"] = int(mailport)
app.config["MAIL_PASSWORD"] = password
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USE_TLS"] = False
mail = Mail(app)

otp = randint(000000,999999)

@app.route("/")
def homep():
    return render_template("overseas.html")

@app.route("/userflash")
def userflash():
    return render_template("userflash.html")

@app.route("/adduserflash")
def adduserflash():
    return render_template("adduserflash.html")
@app.route("/adminflash")
def adminflash():
    return render_template("adminflash.html")

@app.route("/home")
def home():
    return render_template('overseas.html')


@app.route("/country",methods= ['GET','POST'])
def country():
    if 'name' in session:
        if request.method == "POST":
            country = request.form['country']
            print(country)
            cur = mysql.connection.cursor()
            r = cur.execute("select * from usertable where country = %s", (country,))
            mysql.connection.commit()
            cur.close()
            if r > 0:
                result = cur.fetchall()
                print(result)
                return render_template("users.html", result=result)
            else:
                error = "No Student was Found"
                return render_template("users.html", error=error)

        return render_template('country.html')
    else:
        return redirect(url_for("admin_login"))


@app.route("/admindashboard")
def admindashboard():
    if 'name' in session:
        return render_template("admindashboard.html")
    else:
        return redirect(url_for("admin_login"))
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")



@app.route("/notifications")
def notifications():
    if 'email' in session:
        return render_template("notifications.html")
    else:
        return redirect(url_for("admin_login"))



@app.route("/approved")
def approved():
    if 'email' in session:
        email = session['email']
        b = 'Approved'
        cur = mysql.connection.cursor()
        r = cur.execute(
            'SELECT university_applied,country,specialization,year,month FROM universityapplied where email=%s and status=%s',
            (email, b,))
        print(r)
        mysql.connection.commit()
        if r > 0:
            result = cur.fetchall()
            print(result)
            return render_template("approved.html", result=result)
        else:
            flash('no unversities are approved')
            return render_template("approved.html")
        cur.close()
        return render_template("approved.html")
    else:
        return redirect(url_for("login"))



@app.route("/newedit/<string:university_applied>", methods=['GET','POST'])
def newedit(university_applied):
    if request.method == "POST":
        universityapplied = request.form['universityapplied']
        print(universityapplied)
        status = request.form['status']
        cur = mysql.connection.cursor()
        z = cur.execute(
            'UPDATE universityapplied SET university_applied = %s , status = %s  WHERE university_applied = %s',
            [universityapplied, status, university_applied])
        mysql.connection.commit()
        if z >= 0:
            flash("updated successfully")
            return redirect(url_for("applied"))
        else:
            error = "oops something went wrong"
            return render_template("newedit.html", error=error)
        cur.close()

    cur2 = mysql.connection.cursor()
    u = cur2.execute("select * from universityapplied where university_applied = %s", (university_applied,))
    mysql.connection.commit()
    re = cur2.fetchall()
    print(re)
    cur2.close()
    return render_template("newedit.html", re=re)


@app.route("/adduniversity",methods=['GET','POST'])
def adduniversity():
    if 'email' in session:
        today = datetime.date.today()
        return render_template('adduniversity.html', today=today)
    else:
        return redirect(url_for("login"))


@app.route("/sadduniversity",methods=['GET','POST'])
def sadduniversity():
    if 'email' in session:
        if request.method == 'POST':
            universityapplied = request.form['universityapplied']
            country = request.form['country']
            specialization = request.form['specialization']
            status = request.form['status']
            email = session['email']
            year = request.form['year']
            month = request.form['month']
            today = datetime.date.today()
            '''selected_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            if selected_date < today - datetime.timedelta(days=1):
                return "Please select a date that is equal to or greater than today."'''
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM universityapplied WHERE id = %s", (id,))
            user = cur.fetchone()
            if user:
                flash('university already exists', 'error')
                return redirect(url_for('adduniversity'))
            b = cur.execute(
                "insert into universityapplied(university_applied,country,specialization,status,email,year,month) values(%s,%s,%s,%s,%s,%s,%s)",
                (universityapplied, country, specialization, status, email,year,month))
            mysql.connection.commit()
            if b > 0:
                flash("Hey your adding university is success")
                return render_template('applied.html')
            else:
                flash('ERROR:Given month and year are not greater than current month and year.')
                return render_template('adduniversity.html')
            cur.close()
        return render_template('adduniversity.html', today=today)
    else:
        return redirect(url_for("admin_login"))


@app.route('/applied')
def applied():
    if 'email' in session:
        email = session['email']
        cur = mysql.connection.cursor()
        r = cur.execute("select * from universityapplied where email=%s", (email,))
        print(r)
        mysql.connection.commit()
        if r > 0:
            re = cur.fetchall()
            print(re)
            return render_template("applied.html",result=re)
        cur.close()
        return render_template("applied.html")
    else:
        return redirect(url_for('login'))



@app.route("/adprofile")
def adprofile():
    if 'email' in session:
        return render_template("adprofile.html")
    else:
        return  redirect(url_for("admin_login"))




@app.route("/student")
def student():
    if 'email' in session:
        return render_template("student.html")
    else:
        return redirect(url_for("login"))

@app.route("/adstudent")
def adstudent():
    if 'email' in session:
        return render_template("adstudent.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/status",methods=['GET','POST'])
def status():
    if 'email' in session:
        email = session['email']
        today=datetime.date.today()
        cur = mysql.connection.cursor()
        r = cur.execute("select * from studentstatus where email=%s", (email,))
        print(r)
        mysql.connection.commit()
        if r > 0:
            re = cur.fetchall()
            print(re)
            return render_template("status.html", result=re)
        cur.close()
        return render_template("status.html",today=today)
    else:
        return redirect(url_for("login"))

@app.route('/ssedit',methods=['GET','POST'])
def ssedit():
    if 'email' in session:
        if request.method == 'POST':
            financials = request.form['financials']
            biometric = request.form['biometric']
            visa = request.form['visa']
            financialstatus = request.form['financialstatus']
            biometricstatus = request.form['biometricstatus']
            visastatus = request.form['visastatus']
            email = session['email']
            cur = mysql.connection.cursor()
            b = cur.execute("INSERT into studentstatus(financials,biometric,visa,financialstatus,biometricstatus,visastatus,email) values(%s,%s,%s,%s,%s,%s,%s)",
                            (financials, biometric, visa, financialstatus,biometricstatus,visastatus,email,))
            mysql.connection.commit()
            if b > 0:
                flash("Hey your adding university is success")
                return redirect(url_for("status"))
            else:
                flash('ERROR:Given month and year are not greater than current month and year.')
                return render_template('sfetch.html')
            cur.close()
        return render_template('sfetch.html')
    else:
        return redirect(url_for("login"))

@app.route("/forgotpasswordpage",methods=['GET','POST'])
def forgotpasswordpage():
        if request.method == 'POST':
            email = request.form['email']
            cur = mysql.connection.cursor()
            c = cur.execute('select email from usertable where email = %s', (email,))
            mysql.connection.commit()
            if c > 0:
                result = cur.fetchone()
                print(result)
                email = result['email']
                session.permanent = True
                session['email'] = email
                flash("check for OTP")
                msg = Message('subject', sender="saicharansuraram@gmail", recipients=[email])
                msg.body = "THIS IS YOUR OTP FOR FORGOT PASSWORD " + str(otp)
                mail.send(msg)
                return redirect(url_for('fpsend'))
            else:
                error = "oops something went wrong"
                return render_template("forgotpasswordpage.html", error=error)
            cur.close()
        return render_template("forgotpasswordpage.html")

@app.route('/resend_otp', methods=['GET', 'POST'])
def resend_otp():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor()
        r = cur.execute("SELECT email FROM usertable WHERE email = %s", (email,))
        mysql.connection.commit()
        if r>0:
            msg = Message('subject', sender="karupartijayanth143@gmail.com", recipients=[email])
            msg.body = "THIS IS YOUR OTP " + str(otp)
            mail.send(msg)
            return redirect(url_for('send'))
        cur.close()
    return render_template('resend_otp.html')


@app.route("/fpsend")
def fpsend():
    if 'email' in session:
        return render_template("fpsend.html")
    else:
        return redirect(url_for("login"))
@app.route('/fpvalidate',methods=['POST'])
def fpvalidate():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        return redirect(url_for("updatepassword"))
    else:
        error = "wrong OTP"
    return render_template("fpsend.html", error=error)


@app.route('/updatepassword',methods=['GET','POST'])
def updatepassword():
    if request.method == 'POST':
        newpassword = request.form['newpassword']
        confirmpassword = request.form['confirmpassword']
        email = session['email']
        if newpassword == confirmpassword:
            cur = mysql.connection.cursor()
            a = cur.execute('UPDATE usertable SET password = %s WHERE email = %s', [newpassword, email])
            mysql.connection.commit()

            if a > 0:
                flash("password updated successfully")
                session.clear()
                return redirect(url_for('home'))
            else:
                error = "oops something went wrong"
                return render_template("updatepassword.html", error=error)

        else:
            error = "password and confirm password should be same"
            return render_template("updatepassword.html", error=error)
        cur.close()
    return render_template("updatepassword.html")

@app.route('/signup',methods=['GET','POST'])
def signup():
    today = datetime.date.today()
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        image = request.form['image']
        image_data = base64.b64decode(image)
        image_data = base64.b64encode(image_data)
        fullname = request.form['fullname']
        fathername = request.form['fathername']
        contact = request.form['contact']
        email = request.form['email']
        msg = Message('subject', sender="karupartijayanth143@gmail.com", recipients=[email])
        msg.body = "THIS IS YOUR OTP" + str(otp)
        mail.send(msg)
        dob = request.form['dob']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        passport = request.form['passport']
        qualification = request.form['qualification']
        location = request.form['location']
        country = request.form['country']
        gender = request.form['gender']
        maritial = request.form['maritial']
        reference = request.form['reference']
        # Validations
        if not fullname.replace(' ', '').isalpha():
            flash('Full name must contain only alphabet letters and spaces', 'error')
            return redirect(url_for('register'))
        if not fathername.replace(' ', '').isalpha():
            flash('Father name must contain only alphabet letters', 'error')
            return redirect(url_for('register'))
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address format', 'error')
            return redirect(url_for('register'))
        if len(contact) != 10 or not contact.isdigit():
            flash('Contact must be a 10-digit number', 'error')
            return redirect(url_for('register'))
        dob_datetime = datetime.datetime.strptime(dob, '%Y-%m-%d')
        if dob_datetime > datetime.datetime.now() - datetime.timedelta(days=15 * 365):
            flash('Date of birth must be at least 15 years ago', 'error')
            return redirect(url_for('register'))
        if password != confirmpassword:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        if len(passport) != 12 or not any(c.isalnum() for c in passport):
            flash('Passport must contain exactly 12 characters and at least one letter or digit', 'error')
            return redirect(url_for('register'))
        if not country.replace(' ', '').isalpha():
            flash('Country must contain only alphabet letters', 'error')
            return redirect(url_for('register'))
        if not location.replace(' ', '').isalpha():
            flash('Location must contain only alphabet letters', 'error')
            return redirect(url_for('register'))
            # Check if email already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usertable WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
                flash('Email address already exists', 'error')
                return render_template("register.html", fullname=fullname, fathername=fathername, contact=contact,
                                       email=email, dob=dob, passport=passport, qualification=qualification,
                                       location=location, country=country, gender=gender, maritial=maritial,
                                       reference=reference)

        # Insert user data into database
        query = """INSERT INTO usertable (fullname, fathername, contact, email,dob, password,
                passport, country, qualification, location, gender, maritial, reference, image)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""
        values = (
        fullname, fathername, contact, email, dob, password, passport, country, qualification, location, gender,
        maritial, reference, image_data)
        cur.execute(query, values)
        mysql.connection.commit()
        cur.close()
        # Show success message and redirect
        flash('Registration successful', 'success')
        return redirect(url_for('userflash'))
    return render_template('register.html')


@app.route("/admin_register",methods=['GET','POST'])
def admin_register():
    if 'email' in session:
        if request.method == "POST":
            email = request.form['email']
            password = request.form['password']
            cur = mysql.connection.cursor()
            br = cur.execute("insert into admintable(email,password) values(%s,%s)", (email, password))
            mysql.connection.commit()
            if br > 0:
                flash("Admin Register successfull")
                return redirect(url_for("admin_register"))
            else:
                error = "oops something went wrong"
                return render_template("admin_register.html")

            cur.close()

        return render_template("admin_register.html")
    else:
        return redirect(url_for("admin_login"))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        b = cur.execute('select email,password from usertable where email = %s and password = %s and activation_status = true',(email,password))
        mysql.connection.commit()
        if b > 0:
            result = cur.fetchone()
            print(result)
            username1 = result['email']
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=50)
            session['email'] = email
            password1 = result['password']
            if username1 == email and password1 == password:
                flash("successful logged in")
                return redirect(url_for("student"))
            else:
                error = "oops!something went wrong please check email and password"
                return render_template("login.html", error=error)
        else:
            error = "oops something went wrong please check email and password"
            return render_template("login.html",error=error)
    else:
        if 'email' in session:
            email = session["email"]
            return redirect(url_for('student'))
        else:
            return render_template('login.html')
        cur.close()
    return render_template("login.html")

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
        if request.method == 'POST':
            name = request.form['name']
            password = request.form['password']
            print(name)
            print(password)
            cur = mysql.connection.cursor()
            c = cur.execute('select password,name from admintable where  password = %s and name =%s', (password, name))
            mysql.connection.commit()
            if c > 0:
                result = cur.fetchone()
                print(result)
                username1 = result['name']
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=5)
                session['name'] = name
                password1 = result['password']
                if username1 == name and password1 == password:

                    flash("successful logged in")

                    return redirect(url_for("admindashboard"))
                else:
                    error = "oops!something went wrong"
                    return render_template("register.html", error=error)
            else:
                error = "oops something went wrong"
                return render_template("admin_login.html", error=error)
        else:
            if 'name' in session:
                name = session["name"]
                return redirect(url_for('admindashboard'))
            else:
                return render_template('admin_login.html')

            cur.close()
        return render_template("admin_login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/validate',methods=['POST'])
def validate():
    email = request.form['email']
    cur = mysql.connection.cursor()
    r = cur.execute("SELECT email FROM usertable WHERE email = %s and activation_status = false", (email,))
    mysql.connection.commit()
    if r == 0:
        flash("entered email is not correct")
        return render_template("send.html")
    user_otp = request.form['otp']
    if otp == int(user_otp):
        cur = mysql.connection.cursor()
        cur.execute("update usertable set activation_status = true where email=%s",(email,))
        mysql.connection.commit()
        cur.close()
        flash("Successfully Registered")
        return redirect(url_for("login"))
    else:
        flash("wrong OTP")
        return render_template("send.html")
@app.route('/advalidate',methods=['POST'])
def advalidate():
    email = request.form['email']
    cur = mysql.connection.cursor()
    r = cur.execute("SELECT email FROM usertable WHERE email = %s and activation_status = 0 ", (email,))
    mysql.connection.commit()
    if r == 0:
        flash("entered email is not correct")
        return render_template("send.html")
    user_otp = request.form['otp']
    if otp == int(user_otp):
        cur = mysql.connection.cursor()
        cur.execute("update usertable set activation_status = true where email=%s",(email,))
        mysql.connection.commit()
        cur.close()
        flash("Successfully Registered")
        return redirect(url_for("admindashboard"))
    else:
        flash("wrong OTP")
        return render_template("adsend.html")

@app.route("/send")
def send():
    return render_template("send.html")

@app.route("/statusupdate/<string:email>",methods=['GET','POST'])
def statusupdate(email):
    if request.method =="POST":
        financials = request.form['financials']
        biometric = request.form['biometric']
        visa = request.form['visa']
        financialstatus = request.form['financialstatus']
        biometricstatus = request.form['biometricstatus']
        visastatus = request.form['visastatus']

        cur = mysql.connection.cursor()
        a = cur.execute(
            'UPDATE studentstatus SET financials = %s ,biometric=%s,visa=%s,financialstatus =%s ,biometricstatus =%s ,visastatus =%s where email=%s',
            [financials, biometric, visa, financialstatus,biometricstatus,visastatus, email, ])
        mysql.connection.commit()
        if a >= 0:
            flash("updated successfully")
            return redirect(url_for("status"))
        else:
            error = "oops something went wrong"
            return render_template("status.html", error=error)
        cur.close()
    cur2 = mysql.connection.cursor()
    u = cur2.execute("select * from studentstatus where email = %s", (email,))
    re = cur2.fetchall()
    print(re)
    return render_template("statusupdate.html", re=re)

@app.route("/adsend")
def adsend():
    return render_template("adsend.html")

@app.route("/adduser",methods=['GET', 'POST'])
def adduser():
    if 'name' in session:
        if request.method == 'POST':
            # Get form data
            image = request.form['image']
            image_data = base64.b64decode(image)
            image_data = base64.b64encode(image_data)
            fullname = request.form['fullname']
            fathername = request.form['fathername']
            contact = request.form['contact']
            email = request.form['email']
            msg = Message('subject', sender="jayanthkaruparti.CCBPian00101@gmail.com", recipients=[email])
            msg.body = "THIS IS YOUR OTP" + str(otp)
            mail.send(msg)
            dob = request.form['dob']
            password = request.form['password']
            confirmpassword = request.form['confirmpassword']
            passport = request.form['passport']
            qualification = request.form['qualification']
            location = request.form['location']
            country = request.form['country']
            gender = request.form['gender']
            maritial = request.form['maritial']
            reference = request.form['reference']
            if not fullname.replace(' ', '').isalpha():
                flash('Full name must contain only alphabet letters and spaces', 'error')
                return redirect(url_for('adduser'))
            if not fathername.replace(' ', '').isalpha():
                flash('Father name must contain only alphabet letters', 'error')
                return redirect(url_for('adduser'))
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Invalid email address format', 'error')
                return redirect(url_for('adduser'))
            if len(contact) != 10 or not contact.isdigit():
                flash('Contact must be a 10-digit number', 'error')
                return redirect(url_for('adduser'))
            dob_datetime = datetime.datetime.strptime(dob, '%Y-%m-%d')
            if dob_datetime > datetime.datetime.now() - datetime.timedelta(days=15 * 365):
                flash('Date of birth must be at least 15 years ago', 'error')
                return redirect(url_for('adduser'))
            if password != confirmpassword:
                flash('Passwords do not match', 'error')
                return redirect(url_for('adduser'))
            if len(passport) == 8:
                flash('Passport must contain at least 8 letters or digits', 'error')
                return redirect(url_for('adduser'))
            if not country.replace(' ', '').isalpha():
                flash('Country must contain only alphabet letters', 'error')
                return redirect(url_for('adduser'))
            if not location.replace(' ', '').isalpha():
                flash('Location must contain only alphabet letters', 'error')
                return redirect(url_for('adduser'))
            # Check if email already exists
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usertable WHERE email = %s", (email,))
            user = cur.fetchone()
            if user:
                flash('Email address already exists', 'error')
                return redirect(url_for('adduser'))
                # Insert user data into database
            cur.execute(
                "INSERT INTO usertable (fullname, fathername, contact, email,dob, password, passport, country, qualification, location, gender, maritial, reference, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                (
                fullname, fathername, contact, email, dob, password, passport, country, qualification, location, gender,
                maritial, reference, image_data))
            mysql.connection.commit()
            cur.close()
            # Show success message and redirect
            flash('Registration successful, check for otp', 'success')
            return redirect(url_for('adduserflash'))
        return render_template("adduser.html")
    else:
        return redirect(url_for("admin_login"))


@app.route("/users")
def users():
    if 'name' in session:
        cur = mysql.connection.cursor()
        r = cur.execute('select * from usertable')
        mysql.connection.commit()
        if r > 0:
            re = cur.fetchall()
            print(re)
            return render_template("users.html", result=re)
        cur.close()
        return render_template("users.html")
    else:
        return redirect(url_for("admin_login"))


@app.route('/intake',methods=['POST','GET'])
def intake():
    if 'name' in session:
        if request.method == "POST":
            country = request.form['country']
            selected_month = request.form['selected_month']
            selected_year = request.form['selected_year']
            if country == 'none':
                cur = mysql.connection.cursor()
                r = cur.execute("SELECT * FROM universityapplied WHERE MONTH() = %s and YEAR() = %s",
                                (selected_month, selected_year))
                mysql.connection.commit()
            else:
                cur = mysql.connection.cursor()
                r = cur.execute(
                    "SELECT * FROM universityapplied WHERE MONTH = %s and YEAR= %s and country = %s",
                    (selected_month, selected_year, country))
                mysql.connection.commit()
                if r > 0:
                    result = cur.fetchall()
                    print(result)
                    return render_template("intake.html", result=result)
                else:
                    error = "No Student was Found"
                    return render_template("users.html", error=error)
                cur.close()
        return render_template("intake.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/delete/<string:email>")
def delete(email):
    cur = mysql.connection.cursor()
    print(email)
    r = cur.execute("delete from usertable where email = %s", (email,))
    p = cur.execute("delete from files where email = %s", (email,))
    s = cur.execute("delete from studentstatus where email = %s", (email,))
    q = cur.execute("delete from universityapplied where email = %s", (email,))
    mysql.connection.commit()
    print(r)
    if r >= 0 or p >= 0 or s >= 0 or q >= 0:
        flash("Deleted successfully")
        return redirect(url_for("admindashboard"))
        r = cur.execute("select * from usertable")
        admin = cur.fetchall()
        print(admin)
        return render_template("admindashboard.html", result=admin)
    return render_template("users.html")

@app.route("/update/<string:email>", methods=['GET', 'POST'])
def update(email):
    if request.method=="POST":
        fullname = request.form['fullname']
        contact = request.form['contact']
        location = request.form['location']
        qualification = request.form['qualification']
        maritial = request.form['maritial']
        country = request.form['country']
        gender = request.form['gender']
        passport = request.form['passport']
        fathername = request.form['fathername']
        cur = mysql.connection.cursor()
        a = cur.execute(
            'UPDATE usertable SET fullname = %s ,contact=%s,fathername=%s,gender =%s,location=%s,country=%s,passport=%s,qualification=%s ,maritial=%s where email=%s',
            [fullname, contact, fathername, gender, location, country, passport, qualification, maritial, email, ])
        mysql.connection.commit()
        if a >= 0:
            flash("updated successfully")
            return redirect(url_for("admindashboard"))
        else:
            error = "oops something went wrong"
            return render_template("update.html", error=error)
        cur.close()
    cur2 = mysql.connection.cursor()
    u = cur2.execute("select * from usertable where email = %s", (email,))
    re = cur2.fetchall()
    print(re)
    return render_template("update.html", re=re)
@app.route("/studentprofile/<string:email>", methods=['GET','POST'])
def studentprofile(email):
    if request.method == "POST":
        fullname = request.form["fullname"]
        contact = request.form["contact"]
        location = request.form['location']
        passport = request.form["passport"]
        fathername = request.form["fathername"]
        email = session['email']
        cur1 = mysql.connection.cursor()
        r = cur1.execute(
            "update usertable set fullname = %s,contact = %s, location = %s, country = %s,passport = %s,fathername = %s where email = %s",
            [fullname, contact, location, country, passport, fathername, email,])
        mysql.connection.commit()
        print(r)
        if r > 0:
            flash("updated successfully")
            return redirect(url_for("student"))
        else:
            error = "oops something went wrong"
            return render_template("studentprofile.html", error=error)
        cur.close()
    cur2 = mysql.connection.cursor()
    u = cur2.execute("select * from usertable where email = %s", (email,))
    re = cur2.fetchall()
    print(re)
    return render_template("studentprofile.html",re=re)

@app.route('/deactivate/<string:email>',methods=['GET','POST'])
def deactivate(email):
    cur = mysql.connection.cursor()

    r = cur.execute("update usertable set activation_status = false where email=%s",(email,))
    mysql.connection.commit()
    if r > 0:
        flash("user deactivated successfully")
        return render_template("users.html")
    return render_template("users.html")



@app.route('/profile')
def profile():
    if 'email' in session:
        email = session['email']
        cur = mysql.connection.cursor()
        r = cur.execute('select * from usertable where email=%s', [email, ])
        mysql.connection.commit()
        print(r)
        result = cur.fetchall()
        return render_template("profile.html", result=result)
    else:
        return redirect(url_for("login"))

@app.route("/goto/<string:email>", methods=['GET', 'POST'])
def goto(email):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        b = cur.execute('select email,password from usertable where email = %s and password = %s ',(email,password))
        mysql.connection.commit()
        if b > 0:
            result = cur.fetchone()
            print(result)
            username1 = result['email']
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=5)
            session['email'] = email
            password1 = result['password']
            if username1 == email and password1 == password:
                flash("successful logged in")
                return redirect(url_for("student"))
            else:
                error = "oops!something went wrong please check email and password"
                return render_template("login.html", error=error)

        else:
            if 'email' in session:
                email = session["email"]
                return redirect(url_for('student'))
            else:
                return render_template('login.html')
            cur.close()
    cur2 = mysql.connection.cursor()
    u = cur2.execute("select * from usertable where email = %s", (email,))
    re = cur2.fetchall()
    print(re)
    return render_template("goto.html", re=re)
    return render_template("goto.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'email' in session:
        email = session['email']
        if request.method == 'POST':
            file = request.files['file']
            pdf_data = file.read()
            cursor = mysql.connection.cursor()
            query = "INSERT INTO files (filename, pdf,email) VALUES (%s,%s,%s)"
            cursor.execute(query, (file.filename, base64.b64encode(pdf_data), email,))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('view'))
        return render_template('upload.html')
    else:
        return redirect(url_for('login'))


@app.route("/view")
def view():
    if 'email' in session:
        email = session['email']
        cursor = mysql.connection.cursor()
        r = cursor.execute('select * from files where email=%s', [email, ])
        mysql.connection.commit()
        print(r)
        re = cursor.fetchall()
        cursor.close()
        return render_template("view.html", result=re)
    else:
        return redirect(url_for("login"))

@app.route('/download/<filename>')
def download_file(filename):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT pdf FROM files WHERE filename=%s", (filename,))
    pdf_data = cursor.fetchone()['pdf']
    pdf_decoded = base64.b64decode(pdf_data)
    response = make_response(pdf_decoded)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
@app.route('/chatingroom', methods=['GET', 'POST'])
def chatingroom():
    if request.method == 'POST':
        # Get receiver from form
        receiver = request.form['receiver']
        session['receiver'] = receiver
        print(receiver)
        # Redirect to chat page with sender and receiver info
        return redirect(url_for('chat', sender=session['name'], receiver=session['receiver']))
    else:
        # Retrieve all rows from the "users" table
        cur = mysql.connection.cursor()
        r = cur.execute('select * from usertable')

        if r > 0:
            re = cur.fetchall()
            print(re)
            return render_template("cr.html", result=re)
        cur.close()
        return render_template("cr.html")


@app.route("/chat")
def chat():
    # Get sender and receiver from request arguments
    receiver = request.args.get('receiver', '')
    print(receiver)

    # Get the sender from the session
    if 'name' in session:
        sender = session['name']
        print(sender)

    # Retrieve unread messages between sender and receiver from database
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM messages WHERE (sender = %s AND receiver = %s ) OR (sender = %s AND receiver = %s ) ",
        (sender, receiver, receiver, sender))
    messages = cur.fetchall()

    # Mark unread messages as read
    cur.execute("UPDATE messages SET is_read = 1 WHERE sender = %s AND receiver = %s AND is_read = 0",
                (receiver, sender))
    mysql.connection.commit()

    cur.close()

    # Render the chat page with the messages and sender/receiver info
    return render_template('chat.html', messages=messages, sender=sender, receiver=receiver)

@app.route("/schat")
def schat():
    # Get sender and receiver from request arguments
    receiver = request.form.get('receiver', 'genesis')
    print(receiver)
    # Get the sender from the session
    if 'email' in session:
        sender = session['email']
        print(sender)


    # Retrieve messages between sender and receiver from database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM messages WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s) ",
                (sender, receiver, receiver, sender))
    messages = cur.fetchall()
    cur.close()

    ''' # Mark messages as read
    cur = mysql.connection.cursor()
    cur.execute("UPDATE messages SET is_read = 1 WHERE sender = %s AND receiver = %s", (receiver, sender))
    mysql.connection.commit()
    cur.close()'''

    # Render the chat page with the messages and sender/receiver info
    return render_template('schat.html', messages=messages, sender=sender, receiver=receiver)

@app.route('/send_message', methods=['POST'])
def send_message():
    # Get message data from form
    global sender
    if 'name' in session:
        sender = session['name']
    receiver = request.args.get('receiver', '')
    message = request.form['message']

    # Save message to database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)", (sender, receiver, message))
    mysql.connection.commit()
    cur.close()

    return redirect('/chat?receiver=' + receiver)

@app.route('/ssend_message', methods=['POST'])
def ssend_message():
    # Get message data from form
    global sender
    if 'email' in session:
        sender = session['email']
    receiver = request.args.get('receiver', '')
    message = request.form['message']

    # Save message to database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)", (sender, receiver, message))
    mysql.connection.commit()
    cur.close()

    return redirect('/schat?receiver=' + receiver)

if __name__ == "__main__":
    app.run(debug="True")




















































































































































































