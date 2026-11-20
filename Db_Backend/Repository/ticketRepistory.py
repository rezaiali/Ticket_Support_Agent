from sqlalchemy import text, create_engine,select, MetaData
import pandas as pd
from typing import Any, Hashable
from pydantic import BaseModel
from dotenv import load_dotenv
import os


class ticket(BaseModel):
    id:int
    title:str
    description:str
    status:str
    category:str
    priority:str
    assignee:str



class ticketRepository():
    def __init__(self) -> None:
        self.conn=None
       

    def dbconnect(self)->bool:
        try:

            load_dotenv()
            sqlStr=f"mysql://{os.getenv("DbUser")}:{os.getenv("DbPass")}@{os.getenv("DbHost")}:3306/{os.getenv("DbName")}"
            print(sqlStr)
            engine=create_engine(sqlStr)
            self.conn=engine.connect()
            if self.conn:
                print("Database is connected!")
                return True
            else: 
                return False        
        except Exception as error:
            print (f"Error - {error}" )
            return False
    def getTickets(self):
        try:
            if self.conn:
                dt=pd.read_sql_query("select * from tickets", self.conn)
                return dt.to_dict(orient='records')
        except Exception as error:
                return error
    
    def getTicketById(self, ticketId):
        try:
            if self.conn:
                dt=pd.read_sql_query(f"Select * from tickets where ticket_id={ticketId}",self.conn)
                return dt.to_dict(orient='records')
        except Exception as error:
            return [{"message":f"{error}"}]

    def insertTicket(self, title, description, status, category, priority) -> bool:
        try:
            if self.conn:
                Insertq=text(f"""Insert into tickets (title, description, status, category, priority) values 
                ('{title}','{description}','{status}','{category}','{priority}')
                """)
                self.conn.execute(Insertq)
                self.conn.commit()
                cur=self.conn.connection.cursor()
                print (cur.lastrowid)
                return True
            else:
                return False
        except Exception as error:
            print(f"There is an err: {error}")
            return False
    def updateTicket(self, ticket:ticket) -> bool:
        try:
            if self.conn:
                updateq=text(f""" Update tickets set 
                            title='{ticket.title}',description='{ticket.description}', status='{ticket.status}', category='{ticket.category}',
                             priority='{ticket.priority}', assignee='{ticket.assignee}' Where ticket_id={ticket.id}
                        """)    

                self.conn.execute(updateq)
                self.conn.commit()
                return True
            else:
                return False 
        except Exception as err:
            print(f"Error: {err}")
            return False
    def deleteTicket(self, id)-> bool:
        try:
            if self.conn:
                deleteq=text(f""" delete tickets where ticket_id={id}
                            """)
                return True
            else:
                return False
        except Exception as err:
            print (f"Error: {err}")
            return False
    def assignTicket(self,assignee,ticketId)->bool:
         try:
            if self.conn:
                updateq=text(f""" Update tickets set  assignee='{assignee}' Where ticket_id={ticketId}
                        """)
                print(updateq)
                self.conn.execute(updateq)
                self.conn.commit()
                return True
            else:
                return False 
         except Exception as err:
            print(f"Error: {err}")
            return False
    def getTicketsByPriority(self, priorityType):
         try:
            if self.conn:
                dt=pd.read_sql_query(f"Select * from tickets where priority='{priorityType}'",self.conn)
                return dt.to_dict(orient='records')
         except Exception as error:
                return [{"message":f"{error}"}]
    def getTicketByStatus(self,statusType):
         try:
            if self.conn:
                dt=pd.read_sql_query(f"Select * from tickets where status={statusType}",self.conn)
                return dt.to_dict(orient='records')
         except Exception as error:
                return [{"message":f"{error}"}]
    def getTicketNoneAssigned(self):
          try:
            if self.conn:
                dt=pd.read_sql_query(f"Select * from tickets where assignee IS Null",self.conn)
                return dt.to_dict(orient='records')
          except Exception as error:
                return [{"message":f"{error}"}]