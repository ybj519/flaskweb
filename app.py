from flask import Flask,redirect,render_template,url_for,request,session
from DB import DBModule

app = Flask(__name__)
app.secret_key = "weggkfk!dfkwwgegvg"
DB = DBModule()

@app.route("/")
def index():
    if "uid" in session:
        user = session["uid"]
    else:
        user = "Login"
    return render_template("index.html", user = user)

@app.route("/logout")
def logout():
    if "uid" in session:
        session.pop("uid")
        return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))

@app.route("/login")
def login():
    if "uid" in session:
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/login_done", methods=["get"])
def login_done():
    uid = request.args.get("id")
    pwd = request.args.get("pwd")
    if DB.login(uid, pwd):
        session["uid"] = uid
        return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))

@app.route("/user/<string:uid>")
def user_posts(uid):
    u_category, u_usage, u_predict = DB.user_detail(uid)

    return render_template("mypage.html", uid=uid, ucategory=u_category, usage=u_usage, predict_usage=u_predict)

@app.route("/detail/<string:uid>")
def posts_detail(uid):
    category, users_thismonth_freq, users_average_consum, u_thismonth_freq, u_average_consum,lastmonth_list, thismonth_list, cate, temp_list = DB.users_consumption(uid)

    if len(lastmonth_list) == 0:
        del lastmonth_list
        lastmonth_list = "저번달 소비내역 없음"
    if len(thismonth_list) == 0:
        del thismonth_list
        thismonth_list = "이번달 소비내역 없음"

    if users_thismonth_freq == 0 or users_average_consum == 0 or u_thismonth_freq == 0 or u_average_consum == 0:
        length = 0
        message = "정보없음"
    else:
        length = 1

    if u_thismonth_freq != 0 and users_thismonth_freq != 0 and u_average_consum != 0 and users_average_consum != 0:
        if u_thismonth_freq > users_thismonth_freq and u_average_consum > users_average_consum:
            message = "당신은 아무것도 하지 않아도 통장 잔고가 남아나지 않는 소비습관을 가지고 있습니다. 자잘한 소비를 줄이도록 하세요"
        if u_thismonth_freq > users_thismonth_freq and u_average_consum <= users_average_consum:
            message = "당신은 자린고비형 소비습관을 가지고 있습니다. 칭찬합니다."
        if u_thismonth_freq <= users_thismonth_freq and u_average_consum <= users_average_consum:
            message = "당신은 한번에 flex하는 경향이 강하군요 큰 돈을 쓰지 않도록 유의하세요"
        if u_thismonth_freq <= users_thismonth_freq and u_average_consum > users_average_consum:
            message = "당신은 심각한 수준의 소비중독 상태입니다."

    return render_template("detail.html", uid=uid, category=category, usersfreq = users_thismonth_freq , usersconsum = users_average_consum , ufreq = u_thismonth_freq, uconsum = u_average_consum, lastmax = lastmonth_list, thismax = thismonth_list, length = length, cate = cate,templist=temp_list,msg = message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

