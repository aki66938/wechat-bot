
import threading
import logging
import signal
import time
from wcferry import Wcf, WxMsg
import yaml

from db.db import DBmanager
from chat_handler import ChatHandler

# 初始化日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 用于存储联系人信息的数据库类


# 主机器人类，使用 Wcf 处理微信消息
class WeChatRobot:
    def __init__(self, db:DBmanager):
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        self.db = db
        self.chat_handler = ChatHandler(db, self.config)
        self.wcf = Wcf(debug=True)  # Initialize the Wcf client
        self.running = True
        self.worker_threads = []

    def process_messages_from_queue(self):
        while self.running:
            if not self.wcf.msgQ.empty():
                msg = self.wcf.msgQ.get()
                self.processMsg(msg)
            time.sleep(1) 
    
    def processMsg(self, msg: WxMsg):
        try:
            if msg.from_group():
                if msg.roomid in self.config['roomid']:
                    self.chat_handler.process_group_message(msg)
                else:
                    logging.info(f"发生了什么？什么都没有-> {msg}")
            else:
                self.chat_handler.process_private_message(msg)
        except Exception as e:
            logging.error(f"消息处理失败: {e}")
    
    def start(self):
        '''
        原，呸！
        机器人，启动！
        '''
        logging.info("初始化机器人...")
        # 监听退出组合键 (Ctrl+C)
        signal.signal(signal.SIGINT, self.cleanup)
        
        # 接收数据
        self.wcf.enable_receiving_msg()
        threading.Thread(target=self.process_messages_from_queue).start()
        
        # 加载数据库
        self.load_contacts()
        
        # 主线程保持活跃
        try:
            logging.info("正在启动机器人...")
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

    def cleanup(self):
        # 清理资源
        self.running = False
        for thread in self.worker_threads:
            thread.join()
        self.db.close()
        # 清理 wcf 资源
        self.wcf.cleanup()