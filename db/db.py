import sqlite3


class DBmanager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        # 创建联系人表的 SQL 语句
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                wxid TEXT PRIMARY KEY,
                nickname TEXT
            );
        """)
        # 创建群成员表的 SQL 语句
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS group_members (
                wxid TEXT PRIMARY KEY,
                nickname TEXT,
                roomid TEXT
            );
        """)
        self.conn.commit()
    
    def insert_group_member(self, wxid, nickname, roomid):
        # 更新群数据库，如果没有对应表则插入
        insert_sql = 'INSERT OR REPLACE INTO group_members (wxid, nickname, roomid) VALUES (?, ?, ?)'
        self.conn.execute(insert_sql, (wxid, nickname, roomid))
        self.conn.commit()

    def insert_contact(self, wxid, nickname):
        # 个人微信相关表更新，如果没有则插入
        insert_sql = 'INSERT OR REPLACE INTO contacts (wxid, nickname) VALUES (?, ?)'
        self.conn.execute(insert_sql, (wxid, nickname))
        self.conn.commit()

    def get_contact(self, wxid):
        # 通过微信id获取微信名称的语句（暂未使用）
        query_sql = 'SELECT nickname FROM contacts WHERE wxid = ?'
        cursor = self.conn.execute(query_sql, (wxid,))
        result = cursor.fetchone()
        return result[0] if result else None

    def close(self):
        # 关闭数据库连接
        self.conn.close()