from robot import WeChatRobot 
from db.db import DBmanager

# Execution Execution Execution Execution Execution Execution Execution Execution
def main():
    db = DBmanager(".\db\database.db")
    robot = WeChatRobot(db) 
    robot.start() 
 
if __name__ == "__main__":
    main()