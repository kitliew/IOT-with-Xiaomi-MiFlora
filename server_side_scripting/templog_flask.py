from flask import Flask, render_template
import MySQLdb

app = Flask(__name__)


class Database:
        def __init__(self):
                host = "localhost"
                user = "kitxi"
                password = "kittransformation"
                db = "templog"

                self.con = MySQLdb.connect(host=host, user=user, password=password, db=db)
                self.cur = self.con.cursor()

        def list_templog(self):
                self.cur.execute("SELECT Date,Time,Temperature FROM tempatinterrupt")
                result = self.cur.fetchall()

                return result


@app.route("/")
def templog():

        def db_query():
                db=Database()
                templ=db.list_templog()

                return templ

        result = db_query()
        return render_template("templog.html", result=result)

if __name__=="__main__":
	app.run(debug=True, host ="127.0.0.0")
