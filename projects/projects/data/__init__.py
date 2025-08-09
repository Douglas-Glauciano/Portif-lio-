def __init__(self, db_path='database.db'):
    self.db_path = db_path
    self.conn = None
    self.initialize_database() 