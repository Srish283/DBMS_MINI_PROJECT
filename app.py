from flask import Flask,flash,render_template,request,g, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy,event
from forms import  LoginForm, RegistrationForm
from flask_mail import Mail
import json, os, math
from datetime import datetime,timedelta,date
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from sqlalchemy.engine import Engine






app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SQLALCHEMY_ECHO']=True
app.config["SECRET_KEY"] = "thisismysecretkey#"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

#admin = Admin(app)



@event.listens_for(Engine,"connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
  cursor=dbapi_connection.cursor()
  cursor.execute("PRAGMA foreign_keys=ON")
  cursor.close()






class User(UserMixin,db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(125),unique=True,nullable=False)
    firstname=db.Column(db.String(64),index=True,unique=True,nullable=False)
    lastname=db.Column(db.String(64))
    number=db.Column(db.Integer, unique=True)
    password_hash = db.Column(db.String(128))
    package=db.relationship('Package',backref=db.backref('pkgs'),lazy='dynamic')
    payment=db.relationship('Payment',backref=db.backref('pay'),lazy='dynamic')
    hotel=db.relationship('Hotel',backref=db.backref('hotl'),lazy='dynamic')
    transp=db.relationship('Transport',backref=db.backref('trans'),lazy='dynamic')
    
   

    def __repr__(self): 
            return '<User {}>'.format(self.username)

    def set_password(self, password):
            self.password_hash = generate_password_hash(password) 

    def check_password(self, password):
            return check_password_hash(self.password_hash, password)   

    


class Contact(db.Model):
    __tablename__="contact"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80),nullable=False)
    name=db.Column(db.String(12), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(320), nullable=False)
    date = db.Column(db.Integer, nullable=True)
    

class Feedback(db.Model):
    __tablename__="feedback"
    id = db.Column(db.Integer, primary_key=True)
    
    username=db.Column(db.String(64),index=True,unique=True,nullable=False)
    email = db.Column(db.String(80),nullable=False)
    scale=db.Column(db.String(64))
    rating=db.Column(db.String(64))
    feedback=db.Column(db.String(320))
    

class Package(db.Model):
    __tablename__="package"
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(80),nullable=False)
    package_name=db.Column(db.String(80), nullable=False)
    place=db.Column(db.String(80),nullable=False)
    numOfDays=db.Column(db.String(80), nullable=False)
    estimated_cost=db.Column(db.String(80), nullable=False)
    date_booked=db.Column(db.String(80),default = datetime.now,nullable=False)
    userid=db.Column(db.Integer, db.ForeignKey('user.id',onupdate="cascade"))
    




class Hotel(db.Model):
    __tablename__="hotel"
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(80),nullable=False)
    checkin_date=db.Column(db.String(80),default = datetime.date, nullable=False)
    checkout_date=db.Column(db.String(80),default = datetime.date, nullable=False)
    place=db.Column(db.String(80), nullable=False)
    cost=db.Column(db.String(80), nullable=False)
    star_type=db.Column(db.String(80), nullable=False)
    userid=db.Column(db.Integer,db.ForeignKey('user.id',onupdate="cascade"))


class Transport(db.Model):
    __tablename__="transport"
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(80),nullable=False)
    mode_of_transport=db.Column(db.String(80), nullable=False)
    trvcost=db.Column(db.String(80),nullable=False)
    start_date=db.Column(db.String(80),default = datetime.date, nullable=False)
    boarding_place=db.Column(db.String(80), nullable=False)
    place=db.Column(db.String(80), nullable=False)
    boarding_time=db.Column(db.String(80), nullable=False,default = datetime.time)
    userid=db.Column(db.Integer, db.ForeignKey('user.id',onupdate="cascade"))
    


class Payment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(80),nullable=False)
    total_amount=db.Column(db.String(80),nullable=False)
    bookedpack=db.Column(db.String(80),nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.id',onupdate="cascade"))
    
    

db.create_all()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    usr=User.query.all()
    packg=Package.query.all()
    hotl=Hotel.query.all()
    trans=Transport.query.all()
    cont=Contact.query.all()
    feedb=Feedback.query.all()
    paym=Payment.query.all()
    return render_template('dashboard.html',usr=usr,packg=packg,hotl=hotl,cont=cont,feedb=feedb,paym=paym,trans=trans)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)  

@app.route('/signup',methods=['GET','POST'])
def signup():
    form = RegistrationForm(csrf_enabled=False)
    
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data, email=form.email.data, lastname=form.lastname.data, number=form.number.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', title='Signup', form=form)   


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

# login route
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm(csrf_enabled=False)
    if form.validate_on_submit():
        if form.email.data =='admin@gmail.com' and form.password.data=='admin1234':
            session['user']='Admin'
            return redirect(url_for('dashboard'))
        else:
    # Query for user email 
            user = User.query.filter_by(email=form.email.data).first()
        # check if a user was found and the form password matches here:
            if user and user.check_password(form.password.data):
        
        # login user here:
                
                login_user(user, remember=form.remember.data)
                render_template('index.html',current_user=user)
                next_page = url_for('index')
                flash('Login Successfully ')
                return redirect(next_page) if next_page else redirect(url_for('index', _external=True, _scheme='https'))
                
            else:
                flash('Invalid Credentials!!')
                return redirect(url_for('login',_external=True))

    return render_template('login.html', form=form)    
   


@app.route('/about')
@login_required
def about():
    return render_template('about.html')



@app.route('/contact',methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
            '''Add entry to the database'''
            email = request.form.get('email')
            name = request.form.get('name')
            phone = request.form.get('phone')
            message = request.form.get('message')
            try:
                contactme = Contact(email = email,name=name, phone_num = phone, msg = message, date= datetime.now() )
                db.session.add(contactme)
                db.session.commit()
                flash('We will get in touch soon!')
            except:
                flash('Sorry Could not contact us...Please try again!! ')
    return render_template('contact.html')
        

@app.route('/index')
@login_required
def index():
    return render_template('index.html')



@app.route('/package',methods=['GET','POST'])
@login_required
def package():
    if(request.method=='POST'):
        if request.form['submit_button'] == 'Delhi':
            package_name='Delhi Package'
            place='Delhi'
            numOfDays=10
            estimated_cost=20000
            
        elif request.form['submit_button'] == 'Mumbai':
            package_name='Mumbai Package'
            place='Mumbai'
            numOfDays=10
            estimated_cost=23000
        elif request.form['submit_button'] == 'Bangalore':
            package_name='Bangalore Package'
            place='Bangalore'
            numOfDays=10
            estimated_cost=17500
            
        elif request.form['submit_button'] == 'Agra':
            package_name='Agra Package'
            place='Agra'
            numOfDays=8
            estimated_cost=13000
        elif request.form['submit_button'] == 'Amritsar':
            package_name='Amritsar Package'
            place='Amritsar'
            numOfDays=8
            estimated_cost=8000
            
        elif request.form['submit_button'] == 'Chennai':
            package_name='Chennai Package'
            place='Chennai'
            numOfDays=8
            estimated_cost=10000
        elif request.form['submit_button'] == 'Hedrabad':
            package_name='Hedrabad Package'
            place='Hedrabad'
            numOfDays=8
            estimated_cost=9000
            
        elif request.form['submit_button'] == 'Gujrat':
            package_name='Gujrat Package'
            place='Gujrat'
            numOfDays=8
            estimated_cost=7000
        elif request.form['submit_button'] == 'Mysore':
            package_name='Mysore Package'
            place='Mysore'
            numOfDays=5
            estimated_cost=5100
        elif request.form['submit_button'] == 'Dehradun':
            package_name='Dehradun Package'
            place='Dehradun'
            numOfDays=5
            estimated_cost=5000
        elif request.form['submit_button'] == 'Goa':
            package_name='Goa Package'
            place='Goa'
            numOfDays=5
            estimated_cost=5400
        elif request.form['submit_button'] == 'Jaipur':
            package_name='Jaipur Package'
            place='Jaipur'
            numOfDays=10
            estimated_cost=10500
        elif request.form['submit_button'] == 'Kashmir':
            package_name='Kashmir Package'
            place='Kashmir'
            numOfDays=8
            estimated_cost=11000
            
        elif request.form['submit_button'] == 'Kerela':
            package_name='Kerela Package'
            place='Kerela'
            numOfDays=8
            estimated_cost=7300
        elif request.form['submit_button'] == 'Bhopal':
            package_name='Bhopal Package'
            place='Bhopal'
            numOfDays=5
            estimated_cost=5750
            
        elif request.form['submit_button'] == 'Kullu Manali':
            package_name='Manali Package'
            place='Kullu Manali'
            numOfDays=10
            estimated_cost=8200
            
        elif request.form['submit_button'] == 'Ooty':
            package_name='Ooty Package'
            place='Ooty'
            numOfDays=4
            estimated_cost=4800
        elif request.form['submit_button'] == 'Orrissa':
            package_name='Orrissa Package'
            place='Orrissa'
            numOfDays=6
            estimated_cost=5900
            
        elif request.form['submit_button'] == 'Sikkim':
            package_name='Sikkim Package'
            place='Sikkim'
            numOfDays=5
            estimated_cost=6800
        else:
            package_name='Shimla Package'
            place='Shimla'
            numOfDays=8
            estimated_cost=9000
            
        
        try:
            entry=Package(email=current_user.email,package_name=package_name,place=place,numOfDays=numOfDays,estimated_cost=estimated_cost,date_booked=datetime.today().strftime('%Y-%m-%d %H:%M:%S'),pkgs=current_user)
            db.session.add(entry)
            db.session.commit()

            flash('Travel Package is added')
            return redirect(url_for('hotel',_external=True))
        except:
            flash('There was problem adding package')

    
    return render_template('package.html')


@app.route('/hotel',methods=['GET','POST'])
@login_required
def hotel():
    if(request.method=='POST'):
            '''Add entry to the database'''
            pk_days=db.session.query(Package).filter(current_user.email==Package.email).all()
            checkin_date = request.form.get('startdate')
            pn,pl=[],[]

            
            #iterate through package
            for i in  pk_days:
                pn.append(i.numOfDays)
                pl.append(i.place)
            

            i=0
            while i< len(pn):
                if i==len(pn)-1: 
                    pdays=pn[i]
                    place=pl[i]
                    break
                else:
                    i+=1

            
            today = date.today()
            try:
                startdate=datetime.strptime(checkin_date, '%Y-%m-%d').date()
                if startdate >= today:
                    checkin_date=startdate
                    checkout_date= startdate + timedelta(int(pdays))
                    cost= request.form.get('cost')
                    star_type=request.form.get('example')
                else:
                    raise Exception
                
                accomandation = Hotel(email = current_user.email,checkin_date=checkin_date, checkout_date =checkout_date,place=place, cost= cost,star_type=star_type,hotl=current_user )
                db.session.add(accomandation)
                db.session.commit()
                flash('Travel Accomandation data added ')
                return redirect(url_for('transport',_external=True))
            except:
                flash('Accomandation could not be added check details Entered')
    
    return render_template('hotel.html') 

@app.route('/transport',methods=['GET','POST'])
@login_required
def transport():
    if(request.method=='POST'):
            pn=[]
            pkg=db.session.query(Package).filter(Package.email==current_user.email).all()
            transportmode = request.form.get('Mode of Travel')
            if transportmode=='Flight':
                cost=7000
            elif transportmode=='Bus':
                cost=1000
            elif transportmode=='Train':
                cost=700
            else:
                cost=1000
            startdate= request.form.get('s_date')
            boarding_place= request.form.get('myCountry')
            boarding_time=request.form.get('r_time')

            today = date.today()
            #iterate through package
            for i in  pkg:
                pn.append(i.place)
            

            i=0
            while i< len(pn):
                if i==len(pn)-1: 
                    p=pn[i]
                    break
                else:
                    i+=1


            
            try: 
                startdate=datetime.strptime(startdate, '%Y-%m-%d').date()
                if startdate >= today:
                    start_date=startdate
                else:
                    raise Exception

                transport=Transport(email=current_user.email,mode_of_transport=transportmode,trvcost=cost,start_date=start_date,boarding_place=boarding_place,place=p,boarding_time=boarding_time,trans=current_user)
                db.session.add(transport)
                db.session.commit()
                flash('Transportation Details is added ')
                return redirect(url_for('payment',_external=True))
            except:
                flash('Transportation could not be added check details Entered')
    

    return render_template('transport.html') 

@app.route('/PayFeed',methods=['GET','POST'])
@login_required
def payment():
    
    if(request.method=='POST'):
        
        pkg=db.session.query(Package).filter(Package.email==current_user.email).all()
        hotl=db.session.query(Hotel).filter(Hotel.email==current_user.email).all()    
        trans=db.session.query(Transport).filter(Transport.email==current_user.email).all() 

        lp,lh,lt,pn=[],[],[],[]  # list for costs

        #iterate through package
        for i in  pkg:
            lp.append(i.estimated_cost)
            pn.append(i.package_name)
            

        #iterate through Hotel
        for i in  hotl:
            lh.append(i.cost)
        
        #iterate through Transport
        for i in  trans:
            lt.append(i.trvcost)
            
        i=0
        while i< len(lh):
            if i==len(lh)-1:
                amt1=int(lp[i])
                amt2= int(lh[i])
                amt3=int(lt[i]) 
                p=pn[i]
                
                break
            else:
                i+=1

        totl = amt1 + amt2 + amt3
        
        
        try:
            ent=Payment(email=current_user.email,total_amount=totl,bookedpack=p,pay=current_user)
            db.session.add(ent)
            db.session.commit()

            flash('Payment Successfully Confirmed')
            return render_template('payment.html',amt1=amt1,amt2=amt2,amt3=amt3,totl=totl)
        except:
            flash('There was problem in making payment')

    pkg=db.session.query(Package).filter(Package.email==current_user.email).all()
    hotl=db.session.query(Hotel).filter(Hotel.email==current_user.email).all()    
    trans=db.session.query(Transport).filter(Transport.email==current_user.email).all() 


    lp,lh,lt=[],[],[]  # list for costs

    #iterate through package
    for i in  pkg:
        lp.append(i.estimated_cost)
        

    #iterate through Hotel
    for i in  hotl:
        lh.append(i.cost)
       


    #iterate through Transport
    for i in  trans:
        lt.append(i.trvcost)
        

    i=0

    while i< len(lh):
        if i==len(lh)-1:
            amt1=int(lp[i])
            amt2= int(lh[i])
            amt3=int(lt[i]) 
            
            break
        else:
            i+=1

    totl = amt1 + amt2 + amt3        
    
    return render_template('payment.html',amt1=amt1,amt2=amt2,amt3=amt3,totl=totl)



@app.route('/feedback',methods=['GET','POST'])

def feedback():
    if(request.method=='POST'):
        name=request.form.get('username')
        email=request.form.get('email')
        scale=request.form.get('scale')
        rate=request.form.get('rating')
        msg=request.form.get('subject')

        try:
            feed=Feedback(username=name,email=email,scale=scale,rating=rate,feedback=msg)
            db.session.add(feed)
            db.session.commit()
            flash('Thank you for the Feedback :) ')
        except:
            flash('There was Problem adding Feedback')        

    return render_template('feedback.html')




@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))    


@app.route("/travellerInfo")
@login_required
def travellerInfo():
    lp,lh,lt=[],[],[]
    pn,pd=[],[]
    cin,cout=[],[]
    tm,tb,bm=[],[],[]
    pkg=db.session.query(Package).filter(Package.email==current_user.email).all()
    hotl=db.session.query(Hotel).filter(Hotel.email==current_user.email).all() 
    trans=db.session.query(Transport).filter(Transport.email==current_user.email).all() 

    #iterate through package
    for i in  pkg:
        lp.append(i.estimated_cost)
        pn.append(i.package_name)
        pd.append(i.numOfDays)

    #iterate through Hotel
    for i in  hotl:
        lh.append(i.cost)
        cin.append(i.checkin_date)
        cout.append(i.checkout_date)
    


    #iterate through Transport
    for i in  trans:
        lt.append(i.trvcost)
        tm.append(i.mode_of_transport)
        tb.append(i.boarding_place)
        bm.append(i.boarding_time)

    i=0

    while i< len(lh):
        if i==len(lh)-1:
            amt1=int(lp[i])
            amt2= int(lh[i])
            amt3=int(lt[i]) 
            ckot=cout[i]
            ckin=cin[i]
            pname=pn[i]
            pdays=pd[i]
            transb,transm,transt=tb[i],tm[i],bm[i]
            break
        else:
            i+=1

    totl = amt1 + amt2 + amt3 


    
    return render_template('travellerInfo.html',boardp=transb,boardtm=transt,tranmode=transm,ckod=ckot,ckid=ckin,pname=pname,pdays=pdays,user=current_user,total=totl,trans=trans,amt1=amt1,amt2=amt2,amt3=amt3)


@app.route('/delete/package/<int:id>')
def delete(id):
    if ('user' in session and session['user'] == 'Admin'):
        deletePkg= Package.query.get_or_404(id)
        try:
            db.session.delete(deletePkg)
            db.session.commit()
            flash('Package Info successfully Deleted')
            return redirect('/dashboard')
        except:
            return 'There was an issue to delete task'

@app.route('/delete/transport/<int:id>')
def deleteT(id):
    if ('user' in session and session['user'] == 'Admin'):
        deletetrns= Transport.query.get_or_404(id)
        try:
            db.session.delete(deletetrns)
            db.session.commit()
            flash('Transportation info successfully deleted ')
            return redirect('/dashboard')
        except:
            return 'There was an issue to delete task'

@app.route('/delete/contact/<int:id>')
def deleteC(id):
    if ('user' in session and session['user'] == 'Admin'):
        deleteCont=Contact.query.get_or_404(id)
        try:
            db.session.delete(deleteCont)
            db.session.commit()
            flash('Issue resolved')
            return redirect('/dashboard')
        except:
            return 'There was an issue to delete task'

@app.route('/delete/payment/<int:id>')
def deletePm(id):
    if ('user' in session and session['user'] == 'Admin'):
        deletePay=Payment.query.get_or_404(id)
        try:
            db.session.delete(deletePay)
            db.session.commit()
            flash('Payment tansaction successfully deleted')
            return redirect('/dashboard')
        except:
            return 'There was an issue to delete task'


@app.route('/delete/feedback/<int:id>')
def deleteF(id):
    if ('user' in session and session['user'] == 'Admin'):
        deleteFeed=Feedback.query.get_or_404(id)
        try:
            db.session.delete(deleteFeed)
            db.session.commit()
            flash('Feedback Taken into Consideration')
            return redirect('/dashboard')
            
        except:
            return 'There was an issue to delete task'

@app.route('/delete/hotel/<int:id>')
def deleteH(id):
    if ('user' in session and session['user'] == 'Admin'):
        deleteHotl=Hotel.query.get_or_404(id)
        try:
            db.session.delete(deleteHotl)
            db.session.commit()
            flash('Accomandation info  successful Deleted')
            return redirect('/dashboard')
        except:
            return 'There was an issue to delete task'




@app.route("/edit/package/<int:id>", methods = ['GET', 'POST'])
def editP(id):
    if ('user' in session and session['user'] == 'Admin'):
        if request.method == 'POST':
            package_name = request.form.get('pkname')
            cost = request.form.get('cost')
            number_days = request.form.get('numdays')

            if id:
                post = Package.query.filter(Package.id ==id).first()
                post.package_name =package_name 
                post.estimated_cost=cost
                post.numOfDays=number_days
                
                db.session.commit()
                flash("Package Updated!")
                return redirect('/edit/package/'+str(id))

        post = Package.query.filter(Package.id==id).first()
        return render_template('edit_package.html', post=post,id=id)

        

@app.route("/edit/hotel/<int:id>", methods = ['GET', 'POST'])
def editH(id):
    if ('user' in session and session['user'] == 'Admin'):
        
        if request.method == 'POST':
            checkin_date = request.form.get('checkin')
            cost = request.form.get('cost')
            star_type = request.form.get('star')
            

            if id:
                post = Hotel.query.filter(Hotel.id == id).first()
                post.checkin_data = checkin_date
                post.cost = cost
                post.star_type = star_type

                pk_days=db.session.query(Package).filter(id==Package.id).first()
            
                pdays=pk_days.numOfDays
                checkout_date= datetime.strptime(checkin_date, '%Y-%m-%d').date() + timedelta(int(pdays))
                post.chechout_date= checkout_date

                db.session.commit()
                flash("Resort Updated!")
                
                return redirect('/edit/hotel/'+str(id))
        post = Hotel.query.filter(Hotel.id ==id).first()
        pos=['1 Star','2 Star','3 Star','4 Star','5 Star']
        return render_template('edit_hotel.html', post=post, id=id,pos=pos)


@app.route("/edit/transport/<int:id>", methods = ['GET', 'POST'])
def editT(id):
    if ('user' in session and session['user'] == 'Admin'):
        if request.method == 'POST':
            mode_of_transport = request.form.get('mode_transport')
            trvcost = request.form.get('trvcost')
            boarding_place = request.form.get('myCountry')
            boarding_time= request.form.get('boarding_time')

            if id:
                post = Transport.query.filter(Transport.id ==id).first()
                post.mode_of_transport=mode_of_transport
                post.trvcost=trvcost
                post.boarding_place=boarding_place
                post.boarding_time=boarding_time
                
                db.session.commit()
                flash("Transport Updated!")
                return redirect('/edit/transport/'+str(id))

        pos=['Bus','Train','Flight','Cruise']
        post = Transport.query.filter(Transport.id==id).first()
        return render_template('edit_transport.html', post=post,pos=pos, id=id)


if __name__=="__main__":
    app.run(debug=True)
    