import sqlite3
from datetime import datetime,timedelta
import pytz
import json

class Read_db():
    def __init__(self):
        self.conn=sqlite3.connect('attendance.db') #set the connection with the databse
        self.cur=self.conn.cursor() #set the cursor
        self.cairo_tz = pytz.timezone('Africa/Cairo') #cairo time zone
        self.utc_tz = pytz.timezone('UTC') #utc time zone

    def get_attendance(self,employee_code,date):
        """
        :param employee_code: e.g EMPO1
        :param date: the day we are inquire about eg. 2020-04-01
        :return: return dictionary of attendace(bool) and the duration of attendance(str)
        """

        #this query returns the action type and the action time that matches the employee code and the date
        # you can see the output in the data_exploration notebook


        self.cur.execute(
        "SElECT ActionTime,Action FROM AttendanceActions\
        WHERE AttendanceId = (SELECT A.ID FROM Attendance AS A\
        WHERE (A.employee = ? and A.day=?))",(employee_code,date)
        )


        records=self.cur.fetchall()
        checkin_time=[] #stores all the checkin times
        checkout_time=[] #stores all the checkout times
        duration=timedelta() #to calculate the summation of differences between checkin and checkout times


        if records==[]: #if no records found so there is no attendance
            final={"attended":False,"duration":'0'}


        else:

            for action in records:
                if action[1]=="CheckIn":
                    checkin_time.append(action[0])
                elif action[1]=="CheckOut":
                    checkout_time.append(action[0])


            """
            if the employee checked out without check in this means he checked in the previous day 
            so we need to add a check in at the start of the day which is 12:00 AM 
            and vice versa if he checked in without checking out we need to add the a check out at the start of the next day
            
            """


            if len(checkin_time)<len(checkout_time):
                day_start=date+" 12:00 AM"
                checkin_time.insert(0,day_start)

            elif len(checkin_time)>len(checkout_time):
                day_end=str(datetime.strptime(date, '%Y-%m-%d')+timedelta(days=1))
                day_end=day_end[:11]+" 12:00 AM"
                checkout_time.append(day_end)


            for i in range(len(checkin_time)): # calculate duration spent
                time1 = datetime.strptime(checkin_time[i], '%Y-%m-%d %I:%M %p')
                time2 = datetime.strptime(checkout_time[i], '%Y-%m-%d %I:%M %p')
                duration += time2 - time1


            final={"attended":True,"duration":str(duration)}

        file = open("get_attendance_output_example.txt", "w")
        file.write(employee_code+' '+date+'\n'+str(final))

        return final
    
    
    def attednance_history(self,employee_code):
        """
        :param employee_code: eg. EMPO1
        :return: a json output of the history of attendance of this employee.
        """

        # this query is for getting all the employee records of attendance (day, time, action)
        # you can see example in the Database_exploration notebook

        self.cur.execute(
            "SELECT A.day ,AA.Action,AA.ActionTime\
            FROM AttendanceActions AS AA\
            INNER JOIN Attendance AS A\
            ON A.Id=AA.AttendanceId\
            Where A.employee ==?", (employee_code,)
        )

        records=self.cur.fetchall()
        output=[]
        days={"date":"","actions":[]}


        for record in records:
            #convert the time from cairo to Utc timezone
            dt=datetime.strptime(record[2],'%Y-%m-%d %I:%M %p')
            cairo_time=self.cairo_tz.localize(dt)
            utc_time = cairo_time.astimezone(self.utc_tz).isoformat()

            """
            if the day is new we make a new dictionary that contains the date and list of actions 
            but if we saved this day before we will append the action to the list of actions 
            Note: that I am saving the date in cairo time zone but the time of the action is in utc time zone
            """
            
            if record[0]==days["date"]:
                days["actions"].append({"action":record[1],"time":str(utc_time)})
            else:
                output.append(days)
                days={"date":record[0] ,"actions":[{"action":record[1],"time":str(utc_time)}]}

        output.pop(0)
        output.append(days)

        final=json.dumps({"days":output},indent=4) #convert it to json

        file=open("attendance_history_output.txt","w")
        file.write(final)
        return final


    
        

if __name__=="__main__":
    x=Read_db()
    print(x.get_attendance('EMP01','2020-04-03'))
    print(x.attednance_history("EMP01"))



        
