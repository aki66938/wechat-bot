import logging
from wcferry import WxMsg

# 聊天处理类
class ChatHandler:
    def __init__(self, db, config):
        self.db = db
        self.config = config

    def process_group_message(self, msg: WxMsg):
        # 处理群聊消息的逻辑
        logging.info(f"Processing group message: {msg}")
        # ... 其他逻辑 ...

    def process_private_message(self, msg: WxMsg):
        # 处理私聊消息的逻辑
        logging.info(f"Processing private message: {msg}")
        # ... 其他逻辑 ...
