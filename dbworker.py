import aiosqlite
import sqlite3
import time
import subprocess




CONFIG={}
DBCONNECT="data.sqlite"

class User:
    def __init__(self):
        self.id = None
        self.tgid = None
        self.subscription = None
        self.trial_subscription = True
        self.registered = False
        self.username = None
        self.fullname = None

    @classmethod
    async def GetInfo(cls, tgid):
        self = User()
        self.tgid = tgid
        db = await aiosqlite.connect(DBCONNECT)
        db.row_factory = sqlite3.Row
        c = await db.execute(f"SELECT * FROM userss where tgid=?",(tgid,))
        log = await c.fetchone()
        await c.close()
        await db.close()
        if not log is None:
            self.id = log["id"]
            self.subscription = log["subscription"]
            self.trial_subscription = log["banned"]
            self.registered = True
            self.username = log["username"]
            self.fullname = log["fullname"]
        else:
            self.registered = False

        return self


    async def PaymentInfo(self):
        db = await aiosqlite.connect(DBCONNECT)
        db.row_factory = sqlite3.Row
        c = await db.execute(f"SELECT * FROM payments where tgid=?", (self.tgid,))
        log = await c.fetchone()
        await c.close()
        await db.close()
        return log

    async def CancelPayment(self):
        db = await aiosqlite.connect(DBCONNECT)
        await db.execute(f"DELETE FROM payments where tgid=?",
                         (self.tgid,))
        await db.commit()

    async def NewPay(self,bill_id,summ,time_to_add,mesid):
        pay_info = await self.PaymentInfo()
        #print(pay_info)
        if pay_info is None:
            db = await aiosqlite.connect(DBCONNECT)
            await db.execute(f"INSERT INTO payments (tgid,bill_id,amount,time_to_add,mesid) values (?,?,?,?,?)",
                             (self.tgid, str(bill_id),summ,int(time_to_add),str(mesid)))
            await db.commit()



    async def GetAllPaymentsInWork(self):
        db = await aiosqlite.connect(DBCONNECT)
        db.row_factory = sqlite3.Row
        c = await db.execute(f"SELECT * FROM payments")
        log = await c.fetchall()
        await c.close()
        await db.close()
        return log

    async def Adduser(self,username,full_name):
        if self.registered == False:
            db = await aiosqlite.connect(DBCONNECT)
            await db.execute(f"INSERT INTO userss (tgid,subscription,username,fullname) values (?,?,?,?)", (self.tgid,str(int(time.time())+int(CONFIG['trial_period'])),str(username),str(full_name)))
            await db.commit()
            check=subprocess.call(f'./addusertovpn.sh {str(self.tgid)}',shell=True)
            #print(check)
            self.registered = True


    async def GetAllUsers(self):
        db = await aiosqlite.connect(DBCONNECT)
        db.row_factory = sqlite3.Row
        c = await db.execute(f"SELECT * FROM userss")
        log = await c.fetchall()
        await c.close()
        await db.close()
        return log

    async def GetAllUsersWithSub(self):
        db = await aiosqlite.connect(DBCONNECT)
        db.row_factory = sqlite3.Row
        c = await db.execute(f"SELECT * FROM userss where subscription > ?",(str(int(time.time())),))
        log = await c.fetchall()
        await c.close()
        await db.close()
        return log




    async def CheckNewNickname(self,message):
        try:
            username = "@" + str(message.from_user.username)
        except:
            username = str(message.from_user.id)

        if message.from_user.full_name!=self.fullname or username!=self.username:
            db = await aiosqlite.connect(DBCONNECT)
            db.row_factory = sqlite3.Row
            await db.execute(f"Update userss set username = ?, fullname = ? where id = ?", (username,message.from_user.full_name,self.id))
            await db.commit()





