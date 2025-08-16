"""DB connection helper using flask-mysql and dict cursor."""
from flaskext.mysql import MySQL
from pymysql import cursors

# Return rows as dictionaries
db = MySQL(cursorclass=cursors.DictCursor)