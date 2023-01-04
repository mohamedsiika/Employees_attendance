import sqlite3
import pandas as pd
from datetime import datetime,timedelta
class Read_db():
    def __init__(self):
        self.conn=sqlite3.connect('attendance.db')
        #self.get_tables()

    
    
    def get_attendance(self,employee_code,date):

        cur=self.conn.cursor()

        cur.execute(
        "SElECT ActionTime,Action FROM AttendanceActions\
        WHERE AttendanceId = (SELECT A.ID FROM Attendance AS A\
        WHERE (A.employee = ? and A.day=?))",(employee_code,date)
        )

        records=cur.fetchall()
        checkin_time=None
        checkout_time=None
        duration='0'


        if records==[]:
            return {"attended":False,"duration":'0'}


        for action in records:
            if action[1]=="CheckIn":
                checkin_time=action[0]
            if action[1]=="CheckOut":
                checkout_time=action[0]

            if checkin_time and checkout_time:
                
                print(checkin_time,checkout_time)

                time1 = datetime.strptime(checkin_time, '%Y-%m-%d %I:%M %p')
                time2 = datetime.strptime(checkout_time, '%Y-%m-%d %I:%M %p')

                duration = time2 - time1
                checkin_time=None
                checkout_time=None

        return {"attended":True,"duration":str(duration)}
        

if __name__=="__main__":
    x=Read_db()
    print(x.get_attendance("EMP03","2020-04-01"))


        
