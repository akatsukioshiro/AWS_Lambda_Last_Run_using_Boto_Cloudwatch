#LIBRARIES
import boto3
import time
from datetime import datetime, timedelta
import dateutil.relativedelta

#DATE SSETTINGS
old_date = '01/01/10 00:00:00'
log_start_date = datetime.strptime(old_date, '%d/%m/%y %H:%M:%S')
log_end_date = datetime.now()

#VARIABLES
all_func=[]
func_info=[]
all_logs=[]
func_dict_temp={}
out = []
no_stream=[]

#CLIENTS and PAGINATORS
# For Lambda Funtions
client0 = boto3.client('lambda',region_name='us-east-2')
response0 = client0.get_paginator('list_functions').paginate()
# For Log Groups
client1 = boto3.client('logs', region_name='us-east-2')
response1 = client1.get_paginator("describe_log_groups").paginate(logGroupNamePrefix='/aws/lambda/')
# For Streams
response2 = client1.get_paginator("describe_log_streams")
# For events in chosen Stream
response3 = client1.get_paginator('filter_log_events')

#EPOCH CONVERTER
def epoch_converter(this):
    this_is=int(int(this)/1000)
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(this_is))

#ITERATING THROUGH LAMBDA LISTING PAGINATOR
for lmd1 in response0:
    for lmd in lmd1["Functions"]:
        all_func.append(lmd["FunctionName"])
        asv=client0.list_tags(Resource=lmd["FunctionArn"])['Tags'].get("ASV","no ASV found")
        oc=client0.list_tags(Resource=lmd["FunctionArn"])['Tags'].get("OwnerContact","no OwnerContact found")
        func_dict_temp.update({"/".join(["","aws","lambda",lmd["FunctionName"]]):{"asv":asv,"oc":oc}})
        func_info.append(",".join([lmd["FunctionName"],lmd["LastModified"],asv,oc]))

#ITERATING THROUGH LOGGROUP LISTING PAGINATOR
for lgn1 in response1:
    for lgn in lgn1.get("logGroups",[{"logGroupName":"Not_Found"}]):
        log_group=lgn.get("logGroupName","NA")
        if log_group != "NA":
            print(log_group)
            all_logs.append(log_group.split("/aws/lambda/")[1])
            stream_response_pgn = response2.paginate(
                logGroupName=log_group,
            )
            for stream_response in stream_response_pgn:
                latestlogStreamName = stream_response["logStreams"]
                find_max0={}
                find_max1=[]
                if len(latestlogStreamName)==0:
                    print(log_group,"No Streams")
                    no_stream.append(log_group)
                else:
                    for y in latestlogStreamName:
                        find_max0[y["logStreamName"]]=y["creationTime"]
                        find_max1.append(y["creationTime"])
                    max_is=max(find_max1)
                    for stream in find_max0:
                        if find_max0[stream] == max_is:
                            latestlogStreamName = stream
        
                    response4 = response3.paginate(
                        logGroupName=log_group,
                        logStreamNames=[latestlogStreamName],
                    )
                    find_max2=[]
                    for x in response4:
                        for content in x.get("events"):
                            find_max2.append(int(int(content.get('timestamp'))/1000))
                    if len(find_max2) > 0:
                        this_is=max(find_max2)
                        dt1 = datetime.fromtimestamp(this_is)
                        dt2 = datetime.fromtimestamp(int(log_end_date.timestamp()))
                        rd = dateutil.relativedelta.relativedelta (dt2, dt1)
                        rd=vars(rd)
                        now_is=int(log_end_date.timestamp())
                        dayz = int((int(log_end_date.timestamp())-this_is)/86400)
                        cond = False
                        if dayz>=30:
                            cond = True
                        else:
                            cond = False
                        new_asv=func_dict_temp.get(log_group,"No Function Found")
                        new_oc=func_dict_temp.get(log_group,"No Function Found")
                        if new_asv != "No Function Found":
                            new_asv=new_asv["asv"]
                        if new_oc != "No Function Found":
                            new_oc=new_oc["oc"]
                
                        temp = ",".join([log_group,new_asv,new_oc,str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(this_is))),str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now_is))),"{Y}Y-{m}m-{d}d".format(Y=rd.get("years",0), m=rd.get("months",0) ,d=rd.get("days",0)),str(dayz),str(cond)])
                        out.append(temp)
                        print(temp)

#CREATION OF CSV
path = "lambda_details.csv"           
with open(path,"w+") as f:
    f.write("Lambda Function Log,Lambda Function TAG-ASV,Lambda Function  TAG-OwnerContact,Lambda Function Last Log DateTime,Current DateTime,Lambda Last Used in Years-Months-Days,Lambda Last Used in Total Days,30days Threshold Crossed\n")
    f.write("\n".join(out))

path = "lambda_empty_log_group.csv"           
with open(path,"w+") as f:
    f.write("Lambda Function Log\n")
    f.write("\n".join(no_stream))

path = "lambda_functions.csv"           
with open(path,"w+") as f:
    f.write("Lambda Function Name,Function Last Modified,TAG-ASV,TAG-OwnerContact\n")
    f.write("\n".join(func_info))
    
#print(all_func)
#print(all_logs)
##print(func_dict_temp)
##print("Total Functions Found:",len(func_info))
##print("Total Logs Found:",len(all_logs))

path = "lambda_and_Log_consolidated.txt"           
with open(path,"w+") as f:
    f.write("Lambda Functions present but Logs missing :\n"+",".join(list(set(all_func).difference(set(all_logs)))))
    f.write("\nLambda Functions missing but Logs present :\n"+",".join(list(set(all_logs).difference(set(all_func)))))