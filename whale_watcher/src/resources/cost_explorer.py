from typing import List
import boto3
from toolz.dicttoolz import get_in
from functools import partial
from dataclasses import dataclass
from langchain import PromptTemplate
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.chat_models import ChatOpenAI

chat = ChatOpenAI(temperature=0)

client = boto3.client('ce')

template =  """Context: {context}. Question: {query}"""

def response_filtering(boto3_response:dict)->str:
    start_date_key =['TimePeriod', 'Start']
    end_date_key = ['TimePeriod', 'End']
    services_key = ['Groups']
    
    dates = [{'date_period': (get_in(start_date_key, period), get_in(end_date_key, period)), 
              'services': [(x.get('Keys')[0], get_in(['Metrics', 'UnblendedCost', 'Amount'], x))
                           for x
                           in get_in(services_key, period)]}
             for period
             in boto3_response.get('ResultsByTime')]
    
    return dates

def date_to_prompt(data_str:str)->str:
    return f"From {data_str.get('date_period')[0]} to {data_str.get('date_period')[1]}"

def service_to_prompt(data_str:str)->str:
    return [f"the cost of {service[0]} was {round(float(service[1]), 2)} USD"
            for service
            in data_str.get('services')]
    
def convert_data_to_prompt(data_dict:dict)->str:
  
    prompts = ["".join([date_to_prompt(data) + " " + ",".join(service_to_prompt(data))])
     for data
     in data_dict]
    
    return prompts

def convert_response(boto3_responses: dict)->dict:
    dates = response_filtering(boto3_responses)
    
    return dates

if __name__ == "__main__":

    
    start  = "2022-04-01"
    end  = "2023-04-30"
    response = client.get_cost_and_usage(
        TimePeriod={
           'Start': start,
           'End': end,
        },
        Filter = { 
            'Not': { 
                'Dimensions': {
                    'Key': "RECORD_TYPE",
                    'Values': ["Refund", "Credit"]
                 }
             },
        },
        Granularity = 'MONTHLY',
        Metrics=[ 'UnblendedCost' ],
        GroupBy=[{"Type": "DIMENSION","Key": "SERVICE"}]
    )
    
    ce = convert_response(response)
    
    prompt = convert_data_to_prompt(ce)
    
    prompt_template = PromptTemplate(
        input_variables=["context", "query"],
        template=template
        )
    
    human_message_prompt = HumanMessagePromptTemplate.from_template(template)
    print(chat(human_message_prompt.format_messages(context = str(prompt).translate({ord(i): '' for i in "'[]"}),
                           query = "What was the most expensive AWS service?")
    ))
    
    