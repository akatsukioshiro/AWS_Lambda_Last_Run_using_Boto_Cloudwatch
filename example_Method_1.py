import boto3
import uuid
import time
from datetime import datetime

'''
NOTE (Issues Noted)
1. There is noticeable delay between Log Creation and Boto3 aquiring it. (maybe delay for API to update info)
2. Sometimes functions with Logs still throw error, error resolved post you manually monitor Logs in Lambda Function once(maybe helps AWS load data, no idea)
'''

old_date = '01/01/01 00:00:00'
log_start_date = datetime.strptime(old_date, '%d/%m/%y %H:%M:%S')
log_end_date = datetime.now()

client = boto3.client('logs', region_name='us-east-2')

response = client.describe_log_groups(
    logGroupNamePrefix='/aws/lambda/'
)

query = "fields @timestamp, @message"

for lgn in response.get("logGroups",[{"logGroupName":"Not_Found"}]):
    log_group=lgn.get("logGroupName","NA")
    if log_group != "NA":
        #print(log_group)
        run_query_response = client.start_query(
            logGroupName=log_group,
            startTime=int((log_start_date).timestamp()),
            endTime=int(log_end_date.timestamp()),
            queryString=query,
        )
        #print(run_query_response)
        
        query_id = run_query_response['queryId']
        responseX = None
        types_=["Running","Scheduled"]
        while responseX == None or responseX['status'] in types_:
            if responseX == None:
                print("Not Yet")
            else:
                print(responseX["status"])
            time.sleep(1)
            responseX = client.get_query_results(
                queryId=query_id
            )
        print(responseX["status"])
        #print(responseX)
        #print([x.get("value") for x in responseX["results"][0] if x.get("field")=="@timestamp"][0])
        last_run=[x.get("value") for x in responseX["results"][0] if x.get("field")=="@timestamp"][0]
        out={log_group:last_run}
        print(out)
