import pyrebase
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import seaborn as sns
from matplotlib import pyplot as plt

class DBModule:
    def __init__(self):
        firebaseConfig = {
            "apiKey": "AIzaSyBFIpc30kRLllfUs710cbbGZTasFXEYXPk",
            "authDomain": "vita-d7ca1.firebaseapp.com",
            "databaseURL": "https://vita-d7ca1-default-rtdb.firebaseio.com",
            "projectId": "vita-d7ca1",
            "storageBucket": "vita-d7ca1.appspot.com",
            "messagingSenderId": "860961095524",
            "appId": "1:860961095524:web:fdddb042dab3b2d7fec471",
            "measurementId": "G-MRS6WFXE9C"
        }
        firebase = pyrebase.initialize_app(firebaseConfig)
        self.db = firebase.database()

    def login(self, uid, pwd):
        users = self.db.child("User").get().val()
        try:
            userinfo = users[uid]
            if userinfo["pw"] == pwd:
                return True
            else:
                return False
        except:
            return False

    def user_detail(self, uid):
        usage_list = []
        name_list = []
        category_list=[]
        date = self.db.child("Calendar").child(uid).get()
        for k, v in date.val().items():

            for i in range(len(self.db.child("Calendar").child(uid).child().get().val())):
                category = self.db.child("Calendar").child(uid).child(k).get()

            for k2, v2 in category.val().items():
                if None in v2:
                    v2 = {'1': v2[-1]}

                for j in range(len(self.db.child("Calendar").child(uid).child(k).child().get().val())):
                    num = v2

                for k3, v3 in num.items():

                    for n in range(len(k3)):
                        cost = v3

                        for k4, v4 in cost.items():
                            usage_list.append(v4)
                            name_list.append(uid)
                            category_list.append(k2)

        usage_list = list(map(int, usage_list))
        usage = sum(usage_list)
        # usage_list = list(map(string, usage_list))

        result = pd.DataFrame()

        result['name'] = name_list
        result['category'] = category_list
        result['cost'] = usage_list

        result.loc[result['name'] == uid, 'name'] = 1

        ucategory = result['category'].mode()[0]

        x = result[['name']]
        y = result[['cost']]

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=10)
        model = LinearRegression()
        model.fit(x_train, y_train)
        y_predict = model.predict(x_test)

        mse = mean_squared_error(y_test, y_predict)
        mse ** 0.5
        y_predict = y_predict[0]
        return ucategory, usage, (y_predict)

    def users_consumption(self, uid):

        User = self.db.child("User").get()
        Username_list = []
        for k, v in User.val().items():
            Username_list.append(k)

        user_jender = ''
        for key, value in User.val().items():
            if key == uid:
                for jender_k, jender_v in value.items():
                    if jender_k == 'gen':
                        user_jender = jender_v

        user_job = ''
        for key, value in User.val().items():
            if key == uid:
                for job_k, job_v in value.items():
                    if job_k == 'job':
                        user_job = job_v

        calendar = self.db.child("Calendar").get()

        name_list = []
        category_list = []
        cost_list = []
        date_list = []
        count = -1

        gender_list = []
        job_list = []

        for k, v in calendar.val().items():
            count = count + 1
            if Username_list[count] in k:
                date = self.db.child("Calendar").child(Username_list[count]).get()
                for k2, v2 in date.val().items():
                    category = self.db.child("Calendar").child(Username_list[count]).child(k2).get()
                    for k3, v3 in category.val().items():
                        if None in v3:
                            v3 = {'1': v3[-1]}
                        for i in range(
                                len(self.db.child("Calendar").child(Username_list[count]).child(k2).child(k3).get().val())):
                            num = v3
                        for k4, v4 in num.items():

                            for n in range(len(k4)):
                                cost = v4

                                value = self.db.child("User").child(k).get().val()

                                for k6, v6 in value.items():
                                    if k6 == 'gen':
                                        gender_list.append(v6)
                                    if k6 == 'job':
                                        job_list.append(v6)

                                for k5, v5 in cost.items():
                                    name_list.append(k)
                                    cost_list.append(v5)
                                    category_list.append(k3)
                                    date_list.append(k2)

        cost_list = list(map(int, cost_list))
        df = pd.DataFrame()
        df['name'] = name_list
        df['date'] = date_list
        df['category'] = category_list
        df['cost'] = cost_list
        df['gender'] = gender_list
        df['job'] = job_list

        #나와 같은 조건의 유저 이번달 카테고리 사용빈도
        condition = (df['gender'] == user_jender) & (df['job'] == user_job)
        category_frequency = df[condition]['category'].mode()[0]

        today = datetime.today()
        before_one_month = today - relativedelta(months=1)
        months_ago = before_one_month.strftime("%Y-%m")
        time = datetime.today().strftime("%Y-%m")
        dataFilter = df['date'].str.contains(months_ago)
        consumption = df[dataFilter]
        #category_frequency = consumption[condition]['category'].mode()[0]
        condition2 = (consumption['gender'] == user_jender) & (consumption['job'] == user_job)
        # 나와 같은 조건의 유저 저번달 사용금액
        users_consum_sum = consumption[condition2]['cost'].sum()
        # 나의 저번달 사용금액
        u_consumption = consumption['name'] == uid
        uconsum_sum = consumption[u_consumption]['cost'].sum()
        # 나와 같은 조건의 유저 저번달 사용빈도
        users_lastmonth_freq = consumption[condition2]['date']
        users_lastmonth_freq = len(list(set(users_lastmonth_freq)))
        # 나의 저번달 사용 빈도
        u_lastmonth_freq = consumption[u_consumption]['date']
        u_lastmonth_freq = len(list(set(u_lastmonth_freq)))

        if users_lastmonth_freq == 0:
            users_lastmonth_freq = 0
        else:
            users_lastmonth_freq = round(30 / users_lastmonth_freq)
        if u_lastmonth_freq == 0:
            u_lastmonth_freq = 0
        else:
            u_lastmonth_freq = round(30 / u_lastmonth_freq)

        if users_lastmonth_freq == 0:
            users_average_consum = 0
        else:
            users_average_consum = users_consum_sum / users_lastmonth_freq

        if u_lastmonth_freq == 0:
            u_average_consum = 0
        else:
            u_average_consum = uconsum_sum / u_lastmonth_freq


        #카테고리 연관분석

        my_df = df['name'] == uid
        ucategory = df[my_df]['category'].mode()[0]

        clist = ['금융', '미용&뷰티', '문구&디지털', '통신', '식비', '의류&잡화', '경조사', '취미&여가', '문화', '교육', '주거&생활', '건강', '교통']
        Association_category_list = clist
        Association_name_list = []
        for v in name_list:
            if v not in Association_name_list:
                Association_name_list.append(v)
        Association_name_list = list(set(name_list))
        category = pd.DataFrame(index=Association_name_list, columns=Association_category_list)
        category.fillna(0, inplace=True)
        for i in range(len(Association_name_list)):
            my_category = df[df['name'] == Association_name_list[i]]['category'].values
            for j in range(len(my_category)):
                category.loc[Association_name_list[i]][my_category[j]] = category.loc[Association_name_list[i]][
                                                                             my_category[j]] + 1


        condition1 = category.corr()[ucategory][0:clist.index(ucategory)]
        condition2 = category.corr()[ucategory][clist.index(ucategory) + 1:len(clist)]
        maxvalue = pd.concat([condition1, condition2]).max()

        temp_v = pd.concat([condition1, condition2]) == maxvalue
        temp_list = pd.concat([condition1, condition2])[temp_v].index.tolist()

        # 이번달& 지난달 최대 지출 날짜

        today = datetime.today()
        before_one_month = today - relativedelta(months=1)
        months_ago = before_one_month.strftime("%Y-%m")

        time = datetime.today().strftime("%Y-%m")
        dataFilter = df['date'].str.contains(time)
        result_thismonth = df[dataFilter]
        dataFilter = df['date'].str.contains(months_ago)
        result_lastmonth = df[dataFilter]

        u_lastmonth = result_lastmonth['name'] == uid
        u_thismonth = result_thismonth['name'] == uid

        lastmonth_list = result_lastmonth[u_lastmonth]['date'].unique().tolist()
        thismonth_list = result_thismonth[u_thismonth]['date'].unique().tolist()

        if len(lastmonth_list) == 0 and len(thismonth_list) == 0:
            print(lastmonth_list)
            print(thismonth_list)

        if len(lastmonth_list) != 0 and len(thismonth_list) != 0:
            lastmonth_result = result_lastmonth[u_lastmonth]
            thismonth_result = result_thismonth[u_thismonth]

            lastmonth_cost_list = []
            thismonth_cost_list = []
            for i in range(len(lastmonth_list)):
                lastmonth_cost_list.append(
                    lastmonth_result[result_lastmonth[u_lastmonth]['date'] == lastmonth_list[i]]['cost'].sum())

            for i in range(len(thismonth_list)):
                thismonth_cost_list.append(
                    thismonth_result[result_thismonth[u_thismonth]['date'] == thismonth_list[i]]['cost'].sum())

            lastmonth_max_index = [index for index, item in enumerate(lastmonth_cost_list) if
                                   item == max(thismonth_cost_list)]
            thismonth_max_index = [index for index, item in enumerate(thismonth_cost_list) if
                                   item == max(thismonth_cost_list)]

            if len(lastmonth_max_index) == 0:
                lastmonth_max_index = (lastmonth_cost_list.index(max(lastmonth_cost_list)))

            if len(thismonth_max_index) == 0:
                thismonth_max_index = (thismonth_cost_list.index(max(thismonth_cost_list)))

            if isinstance(lastmonth_max_index, list) == False:
                max_index = []
                max_index.append(lastmonth_max_index)
                lastmonth_max_index = max_index

            if isinstance(thismonth_max_index, list) == False:
                max_index = []
                max_index.append(thismonth_max_index)
                thismonth_max_index = max_index

            lastmonth_result = []
            thismonth_result = []

            for i in range(len(lastmonth_max_index)):
                lastmonth_result.append(lastmonth_list[lastmonth_max_index[i]])

            for i in range(len(thismonth_max_index)):
                thismonth_result.append(thismonth_list[thismonth_max_index[i]])

            lastmonth_list.clear()
            lastmonth_list = lastmonth_result

            thismonth_list.clear()
            thismonth_list = thismonth_result

        #카테고리별 지출 top3

        my_df = df['name'] == uid
        print(my_df)
        dict_data = df[my_df]['category'].value_counts(ascending=False)
        dict_data = pd.Series(dict_data)
        category_unique = (df[my_df]['category'].value_counts(ascending=False).unique())

        if len(dict_data.index) >= 3:
            for i in range(3):
                print(dict_data.index[i])
        else:
            for i in range(len(dict_data.index)):
                print(dict_data.index[i])

        category_freq = pd.DataFrame()
        category_freq['category'] = dict_data.index
        category_freq['count'] = dict_data.values

        print(category_freq)

        cate = []

        if len(category_unique) < 3:
            for i in range(len(category_unique)):
                cate.extend(str(i + 1) + "위" +category_freq['category'][category_freq['count'] == category_unique[i]])
        else :
            for i in range(3):
                cate.extend(str(i + 1) + "위" +category_freq['category'][category_freq['count'] == category_unique[i]])

        # 이번년도 사용금액 그래프

        thisyear = datetime.today().strftime("%Y")
        dataFilter = df['date'].str.contains(thisyear)
        result_thisyearconsump = df[dataFilter]
        thisyearconsump = result_thisyearconsump['name'] == uid
        thisyearconsump = result_thisyearconsump[thisyearconsump]

        thisyearlist = thisyearconsump['date'].unique()
        for i in range(len(thisyearlist)):
            thisyearlist[i] = thisyearlist[i][:-3]
        result = []
        for value in thisyearlist:
            if value not in result:
                result.append(value)
        print(result)
        print(thisyearlist)

        thisyear_costsum = []
        for i in range(len(result)):
            dataFilter = df['date'].str.contains(result[i])
            result_sum = df[dataFilter]
            thisyear_result_sum = result_sum['name'] == uid
            thisyear_costsum.append(result_sum[thisyear_result_sum]['cost'].sum())

        print(thisyear_costsum)

        #plt.plot(result, thisyear_costsum)
        #plt.show()

        return category_frequency, users_lastmonth_freq, users_average_consum, u_lastmonth_freq, u_average_consum, lastmonth_list, thismonth_list, cate, temp_list