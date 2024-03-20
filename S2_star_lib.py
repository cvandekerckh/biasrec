# (A) LOAD SQLITE MODULE
import sqlite3
DBFILE = "stars.db"

# (B) HELPER - EXECUTE SQL QUERY
def query(sql, data):
  conn = sqlite3.connect(DBFILE)
  cursor = conn.cursor()
  cursor.execute(sql, data)
  conn.commit()
  conn.close()


# (C) HELPER - FETCH
def fetch(sql, data=[]):
  conn = sqlite3.connect(DBFILE)
  cursor = conn.cursor()
  cursor.execute(sql, data)
  results = cursor.fetchone()
  conn.close()
  return results

# (D) SAVE/UPDATE USER STAR RATING
def save(pid, uid, stars):
  rat = get(pid, uid)
  if rat is None :
    query(
      "INSERT INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES (?,?,?)",
      [pid, uid, stars]
    )
  else : 
    query(
    "REPLACE INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES (?,?,?)",
    [pid, uid, stars]
    )
  return True

def insert (pid, uid, stars):
  rat = get(pid, uid)
  if rat is None :
    query(
      "INSERT INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES (?,?,?)",
      [pid, uid, stars]
    )
  else : 
    query(
    "REPLACE INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES (?,?,?)",
    [pid, uid, stars]
    )
  return True


# (E) GET USER STAR RATING FOR PRODUCT
def get(pid, uid):
  res = fetch(
    "SELECT * FROM `star_rating` WHERE `product_id`=? AND `user_id`=?",
    [pid, uid]
  )
  return 0 if res is None else res[2]

# (F) GET AVERAGE RATING FOR PRODUCT
def avg(pid):
  res = fetch("""
    SELECT ROUND(AVG(`rating`), 2) `avg`, COUNT(`user_id`) `num`
    FROM `star_rating`
    WHERE `product_id`=?""", [pid])
  return (0, 0) if res[0] is None else res

