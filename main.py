from flask import *
from flask_mail import *
from flask_mysqldb import MySQL
from random import *


app = Flask(__name__)

# Connect to the database

app.secret_key = "abc123"

app = Flask(__name__)
app.secret_key = "abc123"

app.secret_key="keyvalue"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PORT"] = 3308
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="project"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql = MySQL(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USERNAME"] = "jayanthkaruparti.CCBPian00101@gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_PASSWORD"] = "wdhobdfeamlgwthh"
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





@app.route("/adminflash")
def adminflash():
    return render_template("adminflash.html")



@app.route("/home")
def home():
    return render_template('overseas.html')

@app.route("/adintake")
def adintake():
    return render_template('adintake.html')


@app.route("/country")
def country():
    return render_template('country.html')

@app.route("/adcountry")
def adcountry():
    return render_template('adcountry.html')

@app.route("/admindashboard")
def admindashboard():
    return render_template("admindashboard.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/sregister', methods=['GET','POST'])
def sregister():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        cur = mysql.connection.cursor()
        c = cur.execute("insert into superadmintable(name,password) values(%s,%s)",(name,password))
        mysql.connection.commit()
        if c>0:
            flash("Admin Register successfull")
            return redirect(url_for("superlogin"))
        else:
            error = "oops something went wrong"
            return render_template("superadmin.html",error = error)

        cur.close()


    return render_template("sregister.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/superadmin")
def superadmin():
    return render_template("superadmin.html")

@app.route("/notifications")
def notifications():
    return render_template("notifications.html")

@app.route("/universitiesapplied")
def universitiesapplied():
    return render_template("universitiesapplied.html")

@app.route("/universitiesapproved")
def universitiesapproved():
    return render_template("universitiesapproved.html")

@app.route("/adprofile")
def adprofile():
    return render_template("adprofile.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/student")
def student():
    return render_template("student.html")

@app.route("/studentstatus")
def studentstatus():
    return render_template("studentstatus.html")

@app.route('/forgotpasswordpage',methods=['GET','POST'])
def forgotpasswordpage():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor()
        c = cur.execute('select email from usertable where email = %s',(email,))
        mysql.connection.cursor()
        if c>0:
            result = cur.fetchone()
            print(result)
            email = result['email']
            session.permanent = True
            session['email'] = email
            flash("check for OTP")
            msg = Message('subject', sender="jayanthkaruparti.CCBPian00101@gmail.com", recipients=[email])
            msg.body = "THIS IS YOUR OTP" + str(otp)
            mail.send(msg)
            return redirect(url_for('fpsend'))
        else:
            error = "oops something went wrong"
            return render_template("forgotpasswordpage.html",error = 'error')
        cur.close()
    return render_template("forgotpasswordpage.html")
@app.route("/fpsend")
def fpsend():
    return render_template("fpsend.html")

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
                return redirect(url_for("login"))
            else:
                error = "oops something went wrong"
                return render_template("updatepassword.html",error = error)
            cur.close()
    return render_template("updatepassword.html")


@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        fathername = request.form['fathername']
        contact = request.form['contact']
        email = request.form['email']
        msg = Message('subject', sender="jayanthkaruparti.CCBPian00101@gmail.com", recipients=[email])
        msg.body = "THIS IS YOUR OTP" + str(otp)
        mail.send(msg)
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        passport = request.form['passport']
        qualification = request.form['qualification']
        location = request.form['location']
        country=request.form['country']
        gender = request.form['gender']
        maritial = request.form['maritial']
        reference = request.form['reference']
        cur = mysql.connection.cursor()
        br = cur.execute('insert into usertable(fullname,fathername,contact,email,password,passport,country,qualification,location,gender,maritial,reference) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(fullname,fathername,contact,email,password,passport,country,qualification,location,gender,maritial,reference))
        mysql.connection.commit()
        if br > 0 :
            if password == confirmpassword:
                flash("Registration successful check for otp ")
                return redirect(url_for("userflash"))
            else:
                error = "something went wrong"
                return render_template("register.html",error = error)
        else:
            error = "oops something went wrong"
            return render_template("overseas.html",error = error)
        cur.close()
    return render_template("register.html")

@app.route("/admin_register",methods=['GET','POST'])
def admin_register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        br=cur.execute("insert into admintable(email,password) values(%s,%s)",(email,password))
        mysql.connection.commit()
        if br>0:
            flash("Admin Register successfull")
            return redirect(url_for("admin_register"))
        else:
            error = "oops something went wrong"
            return render_template("admin_register.html")

        cur.close()

    return render_template("admin_register.html")

@app.route('/login', methods=['GET','POST'])
def login():
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
            session['email'] = email
            password1 = result['password']
            if username1 == email and password1 == password:
                flash("successful logged in")
                return redirect(url_for("student"))
            else:
                error = "oops!something went wrong"
                return render_template("login.html", error=error)
        else:
            error = "oops something went wrong"
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
        email = request.form['email']
        password = request.form['password']
        print(email)
        print(password)
        cur = mysql.connection.cursor()
        c = cur.execute('select password,email from admintable where  password = %s and email =%s',(password,email))
        mysql.connection.commit()
        if c > 0:
            result = cur.fetchone()
            print(result)
            username1 = result['email']
            session.permanent = True
            session['email'] = email
            password1 = result['password']
            if username1 == email and password1 == password:
                flash("successful logged in")
                return redirect(url_for("admindashboard"))
            else:
                error = "oops!something went wrong"
                return render_template("register.html", error=error)
        else:
            error = "oops something went wrong"
            return render_template("admin_login.html", error=error)
    else:
        if 'email' in session:
            email = session["email"]
            return redirect(url_for('admindashboard'))
        else:
            return render_template('admin_login.html')

        cur.close()
    return render_template("admin_login.html")

@app.route('/superlogin', methods=['GET','POST'])
def superlogin():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        cur = mysql.connection.cursor()
        c = cur.execute('select password,name from superadmintable where  password = %s and name =%s',(password,name))
        mysql.connection.commit()
        if c > 0:
            result = cur.fetchone()
            print(result)
            username1 = result['name']
            session.permanent = True
            session['name'] = name
            password1 = result['password']
            if username1 == name and password1 == password:
                flash("successful logged in")
                return redirect(url_for("superadmin"))
            else:
                error = "oops!something went wrong"
                return render_template("superlogin.html", error=error)
        else:
            error = "oops something went wrong"
            return render_template("superlogin.html", error=error)
    else:
        if 'name' in session:
            name = session["name"]
            return redirect(url_for('superadmin'))
        else:
            return render_template('superlogin.html')

        cur.close()
    return render_template("super_login.html")


@app.route("/addadmin",methods=['GET','POST'])
def addadmin():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin':
            return redirect(url_for("admin_register"))
        else:
            return "Wrong password"
    return render_template('addadmin.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/slogout")
def slogout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/validate',methods=['POST'])
def validate():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        return redirect(url_for("login"))

    else:
        error = "wrong OTP"
        return render_template("send.html", error=error)


@app.route("/send")
def send():
    return render_template("send.html")

@app.route("/dbfetch")
def user():
    cur = mysql.connection.cursor()
    r = cur.execute('select * from usertable')
    mysql.connection.commit()
    if r>0:
        re = cur.fetchall()
        print(re)
        return render_template("dbfetch.html",result=re)
    cur.close()
    return render_template("dbfetch.html")

@app.route("/addbfetch")
def users():
    cur = mysql.connection.cursor()
    r = cur.execute('select * from usertable')
    mysql.connection.commit()
    if r>0:
        re = cur.fetchall()
        print(re)
        return render_template("addbfetch.html",result=re)
    cur.close()
    return render_template("addbfetch.html")

@app.route('/intake',methods=['POST','GET'])
def intake():
    if request.method == "POST":
        country = request.form['country']
        print(country)
        cur = mysql.connection.cursor()
        r = cur.execute("select * from usertable where country = %s",(country,))
        mysql.connection.commit()
        if r>0:
            result = cur.fetchall()
            print(result)
            return render_template("dbfetch.html", result=result)
        else:
            error = "No Student was Found"
            return render_template("dbfetch.html", error=error)
        cur.close()
    return render_template("intake.html")

@app.route("/delete/<string:email>")
def delete(email):
    cur = mysql.connection.cursor()
    print(email)
    r = cur.execute("delete from usertable where email = %s", (email,))
    mysql.connection.commit()
    print(r)
    if r>0:
        flash("Deleted successfully")
        r = cur.execute("select * from usertable")
        admin = cur.fetchall()
        print(admin)
        return render_template("dbfetch.html", result=admin)
    return render_template("dbfetch.html")


if __name__ == "__main__":
    app.run(debug="True")