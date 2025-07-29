from flask import Flask,render_template,request,flash,redirect,session
from werkzeug.utils import secure_filename
from flask_mail import Mail,Message
import os

app=Flask(__name__)
app.secret_key="123"

app.config["PIC"]="static/applications/uname/profile_pic"
app.config["RESUME"]="static/applications/uname/resume"
app.config["ID"]="static/applications/uname/id_proof"

app.config['MAIL_USERNAME'] = 'madhanthangavelu04@gmail.com'
app.config['MAIL_PASSWORD'] = 'tnag axdk ltme evvy'
app.config['MAIL_USE_TLS'] = True   
app.config['MAIL_USE_SSL'] = False 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587  

mail=Mail(app)
users={}

class Info:
    def __init__(self,uname,umail,upass):
        self.uname=uname
        self.umail=umail
        self.upass=upass

@app.route("/",methods=["POST","GET"])
def login():
    if request.method=="POST":
        uname=request.form.get('uname')
        upass=request.form.get('upass')

        if uname in users and users[uname].upass == upass:
            session['uname']=users[uname].uname
            session['umail']=users[uname].umail
            session["user"] = users[uname].uname
            flash("Login Successfull", "success")
            return redirect('/upload')  
        else:
            flash("Mismatch Credentials", "danger")
            return redirect('/')  
                    
    return render_template("Login.html")

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method=="POST":
        uname=request.form.get('uname')
        umail=request.form.get('umail')
        upass=request.form.get('upass')
        users[uname]=Info(uname,umail,upass)
        flash("Registeration Completed","success")
        return redirect("/")  
    
    return render_template("Register.html")

allowed_ex=['jpeg','jpg','pdf']
def allowed_extension(file):
    return '.' in file and file.rsplit('.',1)[1].lower() in allowed_ex

@app.route("/upload",methods=['POST','GET'])
def upload():
    if request.method=="POST":

        if 'user' not in session:
            flash("Unauthorised Access","Danger")
            return redirect("/")   
            
        flash("Login Successfull","success")
        uname=session.get('uname')
        umail=session.get('umail')       
        saved_filenames=[]
        
        profile=request.files.get('photo')
        if profile and profile.filename != '' and allowed_extension(profile.filename):
            filename= secure_filename(profile.filename)
            saved_filenames.append(filename)
            os.makedirs(app.config["PIC"].replace("uname", uname),exist_ok=True)
            path1=os.path.join(app.config["PIC"].replace("uname", uname),filename)
            profile.save(path1)
    
        resume=request.files.get('resume')
        if resume and resume.filename != '' and allowed_extension(resume.filename):
            filename=secure_filename(resume.filename)
            saved_filenames.append(filename)
            os.makedirs(app.config["RESUME"].replace("uname", uname),exist_ok=True)
            path2=os.path.join(app.config["RESUME"].replace("uname", uname),filename)
            resume.save(path2)

        files=request.files.getlist('files[]')
        for file in files:
            if file and file.filename!='' and allowed_extension(file.filename):
                filename=secure_filename(file.filename)
                saved_filenames.append(filename)
                os.makedirs(app.config["ID"].replace("uname", uname),exist_ok=True)
                path3=os.path.join(app.config["ID"].replace("uname", uname),filename)
                file.save(path3)
                
        msg=Message(subject='CONFIRMATION MAIL',sender='madhanthangavelu04@gmail.com',recipients=[umail])
        msg.body=f"""
        Hello {uname},
        We have received the files you uploaded below:
        {','.join(saved_filenames)}

        We'll Update you within two Business days

        Thank you,
        Inaiwazhi
        """
        mail.send(msg)
        return redirect('dashboard')
    
    return render_template("upload.html")

@app.route("/dashboard")
def dashboard():
    flash("You will receive a confirmation mail from our side","success")
    imageList=[]
    pic_dir=app.config["PIC"].replace("uname", session['uname'])
    res_dir=app.config["RESUME"].replace("uname", session['uname'])
    id_dir=app.config["ID"].replace("uname", session['uname'])

    for folder in [pic_dir,res_dir,id_dir]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.rsplit('.',1)[1].lower() in allowed_ex:
                    imageList.append(os.path.join(folder,file).replace("\\", "/").replace("static",""))

    return(render_template("dashboard.html",data=imageList))

@app.route("/logout")
def logout():
    session.clear()  # Clears all session data
    flash("Logged out successfully", "info")
    return redirect("/")

if __name__=='__main__':
    app.run(debug=True)