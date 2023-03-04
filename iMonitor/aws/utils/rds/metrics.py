import boto3
import datetime
import base64
import io
import os
import json
from operator import itemgetter

AWS_SERVER_ACCESS_KEY = os.environ.get('AWS_SERVER_ACCESS_KEY')
AWS_SERVER_SECRET_KEY = os.environ.get('AWS_SERVER_SECRET_KEY')
REGION_NAME = os.environ.get('REGION_NAME')

session = boto3.Session(
    aws_access_key_id=AWS_SERVER_ACCESS_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
)

cw_client = session.client('cloudwatch',region_name=REGION_NAME)
rds_client = session.client("rds", region_name=REGION_NAME)


#--------------------------------------------------------------

def get_rds_instance_details():

    response_data=[]
    total_storage = 0
    ins_cnt = 0

    response = rds_client.describe_db_instances()

    for i in response['DBInstances']:   
        try:
            response_data.append({
            "DBInstanceIdentifier": i['DBInstanceIdentifier'],
            "DBInstanceClass":i["DBInstanceClass"],
            "AllocatedStorage":i["AllocatedStorage"],
            "Engine":i["Engine"],
            "AvailabilityZone":i["AvailabilityZone"],
            "DBInstanceArn":i["DBInstanceArn"],
            "DBInstanceStatus":i["DBInstanceStatus"]
        })
            total_storage += (i["AllocatedStorage"])
            ins_cnt += 1

        except Exception as ex:
            continue
            pass
    
    roundSize = ("%.3f TB" % (total_storage*1.0/1024))
    # print(f'size: ', roundSize)
    # print(f'instance count: ', ins_cnt)

    # print(f'response data :',response_data)

    return response, roundSize, ins_cnt

#--------------------------------------------------------------

def get_rds_ins_metrics(type, ins_id):

    dps_avg = []
    dps_time = []

    dp = cw_client.get_metric_statistics(
        Period=300,
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        EndTime=datetime.datetime.utcnow(),
        MetricName=type,
        Namespace='AWS/RDS',
        Statistics=['Average'],
        Dimensions=[{'Name':'DBInstanceIdentifier', 'Value':ins_id}]
        )
    # print(dp)

    datapoints = dp['Datapoints']
    sorted_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))

    # print(sorted_datapoint)

    for i in range(len(sorted_datapoint)):
        sorted_datapoint[i]['sort_by'] = i

    for dp in sorted_datapoint:
        time = dp['Timestamp']
        output_date = datetime.datetime.strftime(time, "%H:%M")

        dps_avg.append(round(dp['Average'], 4))
        dps_time.append(output_date)
    
    dt = dps_time[-10:]
    da = dps_avg[-10:]
    # print(dt)
    # print(da)

    return json.dumps(dt), json.dumps(da)


#--------------------------------------------------------------

def get_rds_snapshots():
    
    response_data = []
    response = rds_client.describe_db_snapshots()
    # DBInstanceIdentifier='database-instance-01'
    # )
    # print(response)
    for i in response['DBSnapshots']:
        try:
            response_data.append({
            "DBInstanceIdentifier": i['DBInstanceIdentifier'],
        })
        except Exception as ex:
            continue
            pass
    return response


#--------------------------------------------------------------

def rds_state_stats():

    stats = {
        "available": 0,
        "starting": 0,
        "stopping": 0,
        "stopped": 0,
        "backing-up": 0,
        "creating": 0,
        "deleting": 0,
        "configuring-enhanced-monitoring": 0
        }
    
    paginator = rds_client.get_paginator('describe_db_instances')
    response_iterator = paginator.paginate()
    for ri in response_iterator:
            for ins in ri['DBInstances']:
                    
                    # print(ins)
                    # print('##############################################')
                    state = ins['DBInstanceStatus']
                    stats[state] += 1
    state_data=[]
    for i in stats.keys():
        state_data.append({"state":i,"value":int(stats[i])})

    return state_data

#--------------------------------------------------------------



#--------------------------------------------------------------



#--------------------------------------------------------------



