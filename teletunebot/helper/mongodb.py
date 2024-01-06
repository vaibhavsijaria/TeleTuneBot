from teletunebot import clientdb

def get_collection(db_name,col_name):
    db = clientdb[db_name]
    return db[col_name]