from flask import Flask, render_template, request,redirect,url_for,jsonify,send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import siaskynet as skynet
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import shutil

client = skynet.SkynetClient()

app=Flask(__name__)
app.secret_key="secreeet"
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///dbdir/sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= True

#app.permanent_session_lifetime=

db = SQLAlchemy(app)

class users(db.Model,UserMixin):
    id =db.Column("id",db.Integer,primary_key=True)
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(100))
    links =db.relationship('Links',backref="email")
    def __init__(self,email,password):
        self.email = email
        self.password=password
     
class Links(db.Model):
  id = db.Column('id',db.Integer,primary_key=True)
  link =db.Column(db.String(255))
  owner_id =db.Column(db.Integer,db.ForeignKey(users.id))

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))
app.debug = True
@app.route('/',methods=['GET','POST'])
def home():


    return render_template('index.html')

@app.route("/login",methods=['POST','GET'])
def login():
  if request.method =="POST":
    email = request.form['email']
    pas= request.form['password']
    found_user = users.query.filter_by(email=email).first()
    if found_user:
      if check_password_hash(found_user.password,pas):
        login_user(found_user)
        print(current_user.email)
        return redirect('upload')

  return render_template('login.html')

@app.route('/signup',methods=['POST','GET'])
def signup():
  msg=""
  if request.method == "POST":
      email =request.form['email']
      pas =request.form['password']
      checkif =users.query.filter_by(email=email).first()
      if checkif:
        msg = "already exist"
      else:
        hashed_password =generate_password_hash(pas,method='sha256')
        new_user= users(email=email,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

  return render_template('signup.html',msg=msg)  




@app.route('/logout')
@login_required
def logout():
  logout_user
  return redirect(url_for('home'))



@app.route('/upload',methods=['POST','GET']) 
@login_required   
def upload():

    rlinks=Links.query.filter_by(owner_id=current_user.email).order_by(desc(Links.id)).all()
  
    lin = [x.link for x in rlinks]
  
    if request.method == 'POST': 
      f= request.files['file1']
      print(f.filename)
      path =f.filename
      f.save(path)
      skylink = client.upload_file(path)
      limb = "https://siasky.net"+skylink.strip("sia:")
      data=Links(link=limb,owner_id=current_user.email)
      db.session.add(data)
      db.session.commit()
             
    return render_template('upload.html',lin=lin)
@app.route('/exten',methods=["GET","POST"])
@login_required
def exten():
  script ="""
    fetch('https://ghostyfiles.manpreetsingh12.repl.co/api?user={fname}')
    .then(data => data.json())
    .then(Data => {{
        const link1 = Data['links'][0];
        const link2 = Data['links'][1];
        const link3 = Data['links'][2];
        const link4 = Data['links'][3];
        const link5 = Data['links'][4];
        document.getElementById("a").href = link1
        document.getElementById("b").href = link2
        document.getElementById("c").href = link3
        document.getElementById("d").href = link4
        document.getElementById("e").href = link5
    }})    
   """
  if request.method=="POST":
    #exten = request.form['gen']
    script =script.format(fname = current_user.email)
    fil =open('/home/runner/ghostyfiles/exten/script.js',"w",encoding='utf-8')
    fil.write(script)
    fil.close()
    shutil.make_archive('extention', 'zip','exten')
    return send_file('extention.zip', as_attachment=True)
  return render_template('extension.html')



@app.route('/api',methods=["GET"])
def api():
  user =request.args.get('user')
  rlinks=Links.query.filter_by(owner_id=user).order_by(desc(Links.id)).all()
  lin = [x.link for x in rlinks]
  return jsonify({'links':lin})



if __name__ == '__main__':
  db.create_all()
  from waitress import serve
  serve(app, host="0.0.0.0", port=8080)