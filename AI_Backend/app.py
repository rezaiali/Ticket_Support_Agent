from typing import TypedDict, Annotated, Sequence, Union,Any
import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
import uvicorn
import httpx
import json
import ast


app = FastAPI()
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage],add_messages]

class AskMessage(BaseModel):
    q: str = Field(min_length=1)

class AskResponse(BaseModel):
    answer: str

class Ticket(BaseModel):
    id:int
    title:str
    description:str
    status:str
    category:str
    priority:str
    assignee:str
    

class APIAskResponse(BaseModel):
    user_prompt: Any
    tool_used: Any
    tickets: list[Ticket]
    final_answer: Any

@tool
def findNoAssignee():
    """To get the no assignee tickets """

    #r= httpx.get("http://host.docker.internal:4046/api/tickets/no/assignee")
    APIserver=os.getenv("APIserver")
    APIPort=os.getenv("APIPort")
    r= httpx.get(f"http://{APIserver}:{APIPort}/api/tickets/no/assignee")
    return r.json()

@tool
def findHighPrioritytickets():
     """To get list of high priority """
     
     APIserver=os.getenv("APIserver")
     APIPort=os.getenv("APIPort")
     r= httpx.get(f"http://{APIserver}:{APIPort}/api/tickets/priority/high")
     return r.json()
@tool
def assignTicketToSteve(Tickets:list[Ticket]):
    """For assigning those unassigned ticket to Steve"""
    APIserver=os.getenv("APIserver")
    APIPort=os.getenv("APIPort")
    count=0
    res={}
    try:
        for ticket in Tickets:
             r=httpx.put(f"http://{APIserver}:{APIPort}/api/tickets/assignTicket",data={"assignee":"Steve", "ticket_id":{ticket.id}})
             count +=1
        res={"message": f"it assigned {count} tickets", "errors": "none"}
    except Exception as err:
        res={"message": f"it assigned {count} tickets", "errors":"{err}"}
    finally:
        return res



tools=[findNoAssignee,findHighPrioritytickets,assignTicketToSteve]

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    base_url=os.getenv(
        "OLLAMA_BASE_URL",
        "http://host.docker.internal:11434"
    ),
    temperature=0.7
).bind_tools(tools)


def call_model(state:AgentState) -> AgentState:
    # system_prompt=SystemMessage(content="""You are my assistant, please answer my query to the best of your ability""")
    system_prompt=SystemMessage(content="""You are an agent, 
    When user ask give me the today's update, you will do these step:
    - Use the 'findNoAssignee' tool to find all the ticket which are not assigned.
    - Use the 'assignTicketToSteve' tool to assigne all the unsignee tickets to 'Steve'
    - Tell the use how many tickets were not assigned and how many now assign to Steve  """)
    
    respose= llm.invoke([system_prompt]+ state["messages"])
    return {"messages":[respose]}


def should_continue(state:AgentState) -> AgentState:
    messages=state["messages"]
    last_message=messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

graph = StateGraph(MessagesState)

graph.add_node("call_agent", call_model)
tool_node= ToolNode(tools=tools)
graph.add_node("tools",tool_node)

graph.set_entry_point("call_agent")

graph.add_conditional_edges(
    "call_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    },
)


graph.add_edge("tools", "call_agent")

agent = graph.compile()



def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance (message, tuple):
            print(message)
        else:
            message.pretty_print()

@app.get("/")
def AIEndPointstart():
    return {"messages":"The AI Agent is started"}


@app.post("/api/AskAI", response_model=APIAskResponse)
async def ask_ai(item: AskMessage):
    try:
        
        ##### Code works for stream ##################

        # inputs: MessagesState = {"messages": [HumanMessage(content=item.q)]}
        # qAnswer = agent.stream(inputs,stream_mode="values")
        # output=""
        # for s in qAnswer:
        #     message = s["messages"][-1]
        #     #if "AIMessage" in message:
        #     output=f"{output}  {message}" 
        #########################################

        ##### Code works for ainvoke ##################
        inputs: MessagesState = {"messages": [HumanMessage(content=item.q)]} 
        qAnswer =await agent.ainvoke(inputs)
        res=qAnswer["messages"]
        user_prompt = res[0].content
        tool_call_info = res[1].tool_calls[0]       # {'name': 'findNoAssignee', 'args': {}, ...}
        tool_raw_output = json.loads(res[2].content) # Parses the {"message": "[...]"} JSON
        final_ai_answer = res[-1].content

        tickets = ast.literal_eval(tool_raw_output["message"])

        theAnswer={
                    "user_prompt": user_prompt,
                    "tool_used": tool_call_info["name"],
                    "tickets": tickets,
                    "final_answer": final_ai_answer
                   }
        return theAnswer

    except Exception as error:
        logger.exception("Agent execution failed, {error}")
        raise HTTPException(
            status_code=503,
            detail="AI agent unavailable"
        )



def start_api_service():
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "4048"))

    uvicorn.run(
        app,
        host=host,
        port=port
    )




if __name__ == "__main__":
   start_api_service()
