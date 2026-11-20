from fastapi import APIRouter, Request
import uvicorn
from Repository.ticketRepistory import ticket, ticketRepository

ticket_router=APIRouter()
ticketRep= ticketRepository()


#getting list of tickets
@ticket_router.get("/tickets")
def getTickets():
    try:
            if ticketRep.dbconnect():
                res=ticketRep.getTickets()
                return {"message":f"{res}"}
            else:
                return {"message": "Databased connection issue"}
    except Exception as error:
                    return {"message": f"There was an issue: {error}"}    

#gettting a single ticket
@ticket_router.get("/tickets/{ticket_id}")
def getTicketById(ticket_id)-> dict:
    try:
        if ticketRep.dbconnect():
            res=ticketRep.getTicketById(ticketId=ticket_id)
            return {"message":res}
        else:
            return {"message": "Databased connection issue"}
    except Exception as error:
                return {"message": f"There was an issue: {error}"}    
#creating a new ticket
@ticket_router.post("/tickets/addticket")
def addNewTicket(newticket:ticket):
    try:
        if ticketRep.dbconnect():
            if ticketRep.insertTicket(newticket.title,newticket.description,newticket.status,newticket.category,newticket.priority):
                return {"message": "New ticket was added"}
            else:
                return {"message": "New ticket did not added!"}
        else:
            return {"message": "Databased connection issue"}
    except Exception as error:
        return {"message": f"There was an issue: {error}"}
# Assigning a ticket
@ticket_router.put("/tickets/assignTicket/")
def assignTicket(payloady:dict):
      try:
             print(f"{payloady}")
             if ticketRep.dbconnect():
                 if ticketRep.assignTicket(payloady.get("assignee"),payloady.get("ticket_id")):
                     return {"message": f"the ticket is aassigned to {payloady.get("assignee")}"}
                 else:
                     return {"message": "the ticket did not assigned!"}
             else:
                 return {"message": "Databased connection issue"}
      except Exception as error:
             print(f"{payloady}")
             return {"message": f"There was an issue: {payloady} - {error}"}
      
#updating a ticket
@ticket_router.put("/tickets/updateTicket")
def updateTicket(payloady:ticket):
    try:
        if ticketRep.dbconnect():
            if ticketRep.updateTicket(payloady):
                return {"message": f"the ticket is updated - {payloady.id}"}
            else:
                return {"message": "the ticket did not update!"}
        else:
            return {"message": "Databased connection issue"}
    except Exception as error:
            return {"message": f"There was an issue: {error}"}

#deleting a ticket
@ticket_router.delete("/tickets/{ticketId}")
def delTicket(ticketId):
    try:
        if ticketRep.dbconnect():
            if ticketRep.deleteTicket(ticketId):
                return {"message": f"the ticket is deleted to {ticketId}"}
            else:
                return {"message": "the ticket did not deleted!"}
        else:
            return {"message": "Databased connection issue"}
    except Exception as error:
                return {"message": f"There was an issue: {error}"} 

@ticket_router.get("/tickets/no/assignee")
def getNoAssigneeTicket():
    
      try:
        if ticketRep.dbconnect():
            res=ticketRep.getTicketNoneAssigned()
            return {"message":f"{res}"}
        else:
            return {"message": "Databased connection issue"}
      except Exception as error:
                return {"message": f"There was an issue: {error}"}
@ticket_router.get("/tickets/priority/{priorityType}")
def getPriorityTickets(priorityType:str):
         try:
            if ticketRep.dbconnect():
                res=ticketRep.getTicketsByPriority(priorityType)
                return {"message":f"{res}"}
            else:
                return {"message": "Databased connection issue"}
         except Exception as error:
                         return {"message": f"There was an issue: {error}"}