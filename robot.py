import sqlite3
import threading
import logging
import signal
import sys
import time
from wcferry import Wcf, WxMsg
import yaml

# 初始化日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 用于存储联系人信息的数据库类
class ContactDatabase:
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

    # 其他方法的注释保持不变...


    
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

# 主机器人类，使用 Wcf 处理微信消息
class WeChatRobot:
    def __init__(self, db_path):
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        self.db = ContactDatabase(db_path)
        self.wcf = Wcf(debug=True)  # Initialize the Wcf client
        self.running = True
        self.worker_threads = []

    def onMsg(self, msg: WxMsg) -> int:
        try:
            logging.info(f"Received message: {msg}")
            threading.Thread(target=self.processMsg, args=(msg,)).start()
        except Exception as e:
            logging.error(f"Error in onMsg: {e}")
        return 0
    
    def group_message(self, msg: WxMsg):
        try:
            # 在这里添加处理群聊消息的逻辑
            logging.info(f"Processing group message: {msg}")
            # ...
        except Exception as e:
            logging.error(f"Error handling group message: {e}")

    def processMsg(self, msg: WxMsg):
        try:
            if msg.from_group():
                if msg.roomid in self.config['roomid']:
                    # 处理来自配置群聊的消息
                    self.group_message(msg)
                else:
                    # 处理来自非配置群聊的消息
                    logging.info(f"Non-configured group message: {msg}")
            else:
                # 处理私聊消息
                logging.info(f"Processing private message: {msg}")
                # 在这里添加处理私聊消息的逻辑
        except Exception as e:
            logging.error(f"Error processing message: {e}")
    
    def start(self):
        logging.info("Starting the WeChat robot...")
        # 监听退出组合键 (Ctrl+C)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # 接收数据
        self.wcf.enable_recv_msg(self.onMsg)

        # 加载数据库
        self.load_contacts()
        
        # 主线程
        try:
            logging.info("Started the WeChat robot...")
            while self.running:
                time.sleep(1)  
        except KeyboardInterrupt:
            logging.info("Interrupted by user")
        
        # 清理退出
        self.running = False
        for thread in self.worker_threads:
            thread.join()
        self.db.close()
    
    def load_contacts(self):
        # 读取个微信息，存入数据库
        contacts = self.wcf.get_contacts()
        for contact in contacts:
            self.db.insert_contact(contact['wxid'], contact['name'])

    def signal_handler(self, signal_received, frame):
       
        # 关闭数据库连接
        self.db.close()
        
        # 清理 Wcf 对象
        self.wcf.cleanup()  

        # 停止线程
        self.running = False
        for thread in self.worker_threads:
            thread.join()


# Execution Execution Execution Execution Execution Execution Execution Execution
if __name__ == "__main__":
    robot = WeChatRobot("contacts.db")
    robot.start()
