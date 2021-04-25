import boto3
import time
from datetime import datetime, timedelta

old_date = '01/01/10 00:00:00'
log_start_date = datetime.strptime(old_date, '%d/%m/%y %H:%M:%S')
#log_start_date = (datetime.today() - timedelta(hours=5))
log_end_date = datetime.now()

client = boto3.client('logs', region_name='us-east-2')
paginator = client.get_paginator('filter_log_events')

response = client.describe_log_groups(
    logGroupNamePrefix='/aws/lambda/'
)

def epoch_converter(this):
    this_is=int(int(this)/1000)
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(this_is))

for lgn in response.get("logGroups",[{"logGroupName":"Not_Found"}]):
    log_group=lgn.get("logGroupName","NA")
    if log_group != "NA":

        stream_response = client.describe_log_streams(
            logGroupName=log_group,                  # Can be dynamic
            #orderBy='LastEventTime',                 # For the latest events
            #limit=1                                  # the last latest event, if you just want one
        )
        latestlogStreamName = stream_response["logStreams"]
        find_max0={}
        find_max1=[]
        for y in latestlogStreamName:
            find_max0[y["logStreamName"]]=y["creationTime"]
            find_max1.append(y["creationTime"])
        max_is=max(find_max1)
        #print(find_max0)
        #print(find_max1)
        for stream in find_max0:
            if find_max0[stream] == max_is:
                print("Selected Stream : ",stream,"\n")
                latestlogStreamName = stream
        
        #exit()
        response_iterator = paginator.paginate(
            logGroupName=log_group,
            logStreamNames=[latestlogStreamName],
        )
        find_max2=[]
        for x in response_iterator:
            for content in x.get("events"):
                find_max2.append(int(int(content.get('timestamp'))/1000))
                #print(datetime.fromtimestamp(int(content.get('timestamp'))))  
        if len(find_max2) > 0:
            this_is=max(find_max2)
            print({log_group:str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(this_is)))})