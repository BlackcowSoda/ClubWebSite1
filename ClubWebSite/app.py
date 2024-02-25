from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import pymysql
import time
import random
import string
import os


# 데이터베이스 연결 설정
conn_ClubDB = pymysql.connect(
    host='localhost',   # 호스트 이름
    user='root',        # MySQL 사용자 이름
    port=3306,
    password='0622',    # MySQL 비밀번호
    db='ClubDB',        # 사용할 데이터베이스 이름
    charset='utf8'      # 문자 인코딩 설정
)
cursor = conn_ClubDB.cursor(pymysql.cursors.DictCursor)

app = Flask(__name__)
#Session(app)
#app.secret_key = 'KSJOYDA'
#app.secret_key = os.urandom(24)
app.config['logged_in'] = None
app.config['Successful_application'] = False  # 세션 저장 방식 설정
app.config['UserName'] = ''
app.config['DarkMode'] = False
app.config['SECRET_KEY'] = 'KSJOYDA'  # 암호화를 위한 시크릿 키 설정

def application_INSERT(Class_Number, Name, Phone_Number, Code, Reason, Special):
    sql = "INSERT INTO APPLICATION (CLASS_NUMBER, NAME, PHONE_NUMBER, CODE, REASON, SPECIAL) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (Class_Number, Name, Phone_Number, Code, Reason, Special))
    conn_ClubDB.commit()

Successful_application = False
Admin = False

letters_lowercase = string.ascii_lowercase
#stack = 0
def codeGenerator(code):
    codeArrange = [] 
    #global stack
    for i in range(0, random.randrange(10, 20)):
        randomstr = random.choice(letters_lowercase)
        codeArrange.append(randomstr)
        print(codeArrange)
    code = ''.join(map(str, codeArrange))

    #code = "nlzgmlhpncyblpnn"
    #if stack >= 3: #
    #    code = "aaaaaab"

    print("Code1: {}".format(code))
    cursor.execute("SELECT * FROM application WHERE CODE = %s", (code))
    Code_DuplicationConfirm = cursor.fetchall()
    if Code_DuplicationConfirm:
        #stack += 1
        return codeGenerator(code)
    print("최종코드:" + code)
    return code

@app.route('/', methods=['GET', 'POST'])
def index():
    user_ip = request.remote_addr
    print("Ip: \033[95mHI:{}\033[0m".format(user_ip))

    if request.method == 'POST':
        #if request.form.get('login'):
            #return redirect('/login')
    
        if request.form.get('DarkMode'):
            session['DarkMode'] = True
            print(session['DarkMode'])

    return render_template('index.html') #class_logo=f"static/images/Logo.png"

@app.route('/set_dark_mode', methods=['POST'])
def set_dark_mode():
    DarkMode = request.json.get('DarkMode')
    session['DarkMode'] = DarkMode
    return '', 204


@app.route('/application', methods=['GET', 'POST'])
def application():
    if Successful_application in session and Successful_application == False or not Successful_application in session:    
        if request.method == 'POST':
            print("저장 성공")
            global Code
            Code = None
            Code = codeGenerator(Code)

            Class_Number = request.form.get('student_id')
            Name = request.form.get('name')
            Phone_Number = request.form.get('phone')
            Code = Code
            print(f"코드는: {Code}")
            Reason = request.form.get('motivation')
            Special = request.form.get('note')

            application_INSERT(Class_Number, Name, Phone_Number, Code, Reason, Special)

            if request.form.get('application_Success1'):
                return redirect('/application_Success')

            return redirect('/application_Success')
        return render_template('application.html')
    else:
        return render_template('/')

@app.route('/application_Success', methods=['GET', 'POST'])
def application_Success1():
    global Successful_application
    Successful_application = True
    session['Successful_application'] = True
    return render_template('application_success.html', Code=Code, Successful_application=Successful_application)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        Class_NumberG = request.form.get('student_idG')
        NameG = request.form.get('nameG')
        cursor.execute('INSERT INTO GUEST (CLASS_NUMBER, NAME) VALUES (%s, %s)', (Class_NumberG, NameG))
        conn_ClubDB.commit()
        if request.form.get('id') == 'registerF':
            return redirect('/login')
        return redirect('/register_success')
    return render_template('register.html')

@app.route('/register_success', methods=['GET', 'POST'])
def register_success():
    Guest_Code = "sijqwdsp"
    return render_template('register_success.html', Code=Guest_Code)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_code = request.form.get('code')
        cursor.execute("SELECT * FROM application WHERE CODE = %s", (user_code))
        global Successful_application

        if user_code == 'sijqwdsp':
            print("게스트가 로그인했습니다")
            Successful_application=False
            session['Successful_application'] = False
            session['logged_in'] = 'Guest'
            return redirect('/main1')
        
        if user_code == 'aaaaaaaa':
            print('\033[1m\033[91m어드민이 로그인했습니다\033[0m')
            global Admin
            Admin = True
            session['Successful_application'] = False
            session['logged_in'] = True
            session['UserName'] = 'Admin'
            return redirect('/main1')

        user_info = (cursor.fetchone())
        if user_info:
            print("코드 : \033[1m\033[91m{}\033[0m 님이 로그인하셨습니다".format(user_code))
            Successful_application=True
            session['Successful_application'] = True
            session['logged_in'] = True  # 사용자가 로그인했음을 세션에 저장
            user_name = user_info['NAME']  # 첫 번째 레코드의 이름 필드를 가져옴
            session['UserName'] = user_name
            print(session['UserName'])
            return redirect('/main1')
        else:
            print("올바르지 않은 코드입니다")
            flash("올바르지 않은 코드입니다")
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    session.pop('Successful_application', None)
    session.pop('logged_in', None)
    session.pop('UserName', None)
    return redirect('/')

@app.route('/main1', methods=['GET', 'POST'])
def main1():
    if 'logged_in' in session:
        if request.method == 'POST':
            if request.form.get('/logout'):
                return redirect('/logout')
            
        return render_template('main1.html', Successful_application=Successful_application, Admin=Admin)
    else:
        flash("로그인해 주십시오")
        print("로그인해 주십시오")
        return redirect('/login')

@app.route('/applications', methods=['GET', 'POST'])
def applications():
    if 'UserName' in session and session['UserName'] == 'Admin':
        # 데이터베이스에서 지원서 정보를 가져옵니다.
        cursor.execute("SELECT * FROM APPLICATION")
        applications = cursor.fetchall()
        #cursor.close()
        
        # 가져온 지원서 정보를 템플릿에 전달하여 표시합니다.
        return render_template('applications.html', applications=applications)
    else:
        flash("관리자 권한이 필요합니다")
        print("관리자 권한이 필요합니다")
        return redirect('/login')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'logged_in' in session:
        return render_template('contact.html')
    else:
        flash("로그인해 주십시오")
        print("로그인해 주십시오")
        return redirect('/login')
    
@app.route('/session_show')
def session_show():
    print(session)
    return redirect('/')

@app.route('/session_clear')
def session_clear():
    print(f"초기화전 세션: {session}")
    session.clear()
    print("초기화된 세션: {}".format(session))
    return redirect('/')


if __name__ == '__main__':


    print('''서버가 시작되었습니다!
    "http://localhost:25565/"\n, http://14.51.87.66:25565/\n 으로 접속해주세요!
    ''')

    app.run(host='0.0.0.0',port=25565, debug=True)