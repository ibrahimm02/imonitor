import boto3, os
from operator import itemgetter
import json
import base64
import io
import datetime
import statistics

AWS_SERVER_ACCESS_KEY = os.environ.get('AWS_SERVER_ACCESS_KEY')
AWS_SERVER_SECRET_KEY = os.environ.get('AWS_SERVER_SECRET_KEY')
REGION_NAME = os.environ.get('REGION_NAME')

session = boto3.Session(
    aws_access_key_id=AWS_SERVER_ACCESS_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
)

ec2_client = session.client("ec2", region_name=REGION_NAME)
ec2_resource = session.resource('ec2', region_name=REGION_NAME)
cw_client = session.client('cloudwatch',region_name=REGION_NAME)

#--------------------------------------------------------------

def get_running_instances():
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running"],
        }
    ]).get("Reservations")


    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            public_ip = instance["PublicIpAddress"]
            private_ip = instance["PrivateIpAddress"]
            print(f"{instance_id}, {instance_type}, {public_ip}, {private_ip}")

#--------------------------------------------------------------

# get_running_instances()

# @app.route('/aws-ec2-instances')
# def aws_ec2_instances():
#     ec2 = boto3.client('ec2')
#     # response = ec2.describe_instances()
#     if sys.argv[1] == 'ON':
#         response = ec2.monitor_instances(InstanceIds=['i-0eadf739e14d3b325'])
#     else:
#         response = ec2.unmonitor_instances(InstanceIds=['i-0eadf739e14d3b325'])

#     return response


#--------------------------------------------------------------

def get_active_instance_count():

    INSTANCE_STATE = 'running'

    instances = ec2_resource.instances.filter(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    INSTANCE_STATE
                ]
            }
        ]
    )

    # print(f'Instances in state "{INSTANCE_STATE}":')
    count = 0
    for instance in instances:
        # print(f'  - Instance ID: {instance.id}')
        count += 1
    
    return count

#--------------------------------------------------------------

def ec2_state_stats():
    stats = {
        "pending": 0,
        "running": 0,
        "shutting-down": 0,
        "terminated": 0,
        "stopping": 0,
        "stopped": 0
        }
    
    qs_ = ec2_client.get_paginator('describe_instances')
    response_ = qs_.paginate()
    for rs in response_:
        for reservation in rs['Reservations']:
            for instance in reservation['Instances']:
                state = instance['State']['Name']
                stats[state] += 1
    graph_data=[]
    for i in stats.keys():
        graph_data.append({"state":i,"value":int(stats[i])})
    return (graph_data)


#--------------------------------------------------------------

def get_ec2_metrics_amm():

    dp_avg = []
    dp_max = []
    dp_min = []

    reservations = ec2_client.describe_instances().get("Reservations")

    # print(reservations)

    # if not reservations:
    #     print("list empty")
    #     avg_uti = dp_avg.append(0)
    #     max_uti = dp_max.append(0)
    #     min_uti = dp_min.append(0)

    # else:
    #     print("list not empty")

    for res in reservations:
        for instance in res["Instances"]:

            print(instance["InstanceId"])

            response = cw_client.get_metric_statistics(
                MetricName = 'CPUUtilization',
                Namespace = 'AWS/EC2',
                Period = 86400,
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(hours=3),
                EndTime=datetime.datetime.utcnow(),
                Statistics=['Maximum','Minimum','Average'],
                Dimensions = [
                    {
                        'Name': 'InstanceId',
                        'Value': instance["InstanceId"]
                    }   
                ],        
            )

            datapoints = response['Datapoints']

            print(f'dp: ', datapoints)

            for dp in datapoints:
            
                dp_avg.append(dp['Average'])
                dp_max.append(dp['Maximum'])
                dp_min.append(dp['Minimum'])

    # avg_uti = round(sum(dp_avg)/len(dp_avg),3)
    # max_uti = round(sum(dp_max)/len(dp_max),3)
    # min_uti = round(sum(dp_min)/len(dp_min),3)
    if dp_avg != [] or dp_max != [] or dp_min != []:

        avg_uti = round(statistics.mean(dp_avg),3)
        max_uti = round(statistics.mean(dp_max),3)
        min_uti = round(statistics.mean(dp_min),3)

    else:
        avg_uti = (0)
        max_uti = (0)
        min_uti = (0)
    
    return avg_uti, max_uti, min_uti


# get_ec2_metrics_amm()

#--------------------------------------------------------------

def get_ec2_ins_metrics(type, ins_id):

    dps_avg = []
    dps_time = []

    dp = cw_client.get_metric_statistics(
        Period=300,
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        EndTime=datetime.datetime.utcnow(),
        MetricName=type,
        Namespace='AWS/EC2',
        Statistics=['Average'],
        Dimensions=[{'Name':'InstanceId', 'Value':ins_id}]
        )
    # print(dp)

    datapoints = dp['Datapoints']     # CPU Utilization results                
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

def ec2_instance_metrics(type, ins_id):

    if type == "CPUUtilization":
        ins_met = {"metrics":[["AWS/EC2", "CPUUtilization", "InstanceId", str(ins_id)]]}  
    if type == "DiskReadOps":
        ins_met = {"metrics": [["AWS/EC2", "DiskReadOps", "InstanceId", str(ins_id)]]}
    if type == "DiskWriteOps":
        ins_met = {"metrics": [["AWS/EC2", "DiskWriteOps", "InstanceId", str(ins_id)]]}
    if type == "NetworkIn":
        ins_met = {"metrics": [["AWS/EC2", "NetworkIn", "InstanceId", str(ins_id)]]}
    if type == "NetworkOut":
        ins_met = {"metrics": [["AWS/EC2", "NetworkOut", "InstanceId", str(ins_id)]]}
    if type == "CPUCreditUsage":
        ins_met = {"metrics": [["AWS/EC2", "CPUCreditUsage", "InstanceId", str(ins_id)]]}
    if type == "CPUCreditBalance":
        ins_met = {"metrics": [["AWS/EC2", "CPUCreditBalance", "InstanceId", str(ins_id)]]}
    if type == "DiskReadBytes":
        ins_met = {"metrics": [["AWS/EC2", "DiskReadBytes", "InstanceId", str(ins_id)]]}
    if type == "DiskWriteBytes":
        ins_met = {"metrics": [["AWS/EC2", "DiskWriteBytes", "InstanceId", str(ins_id)]]}

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(ins_met))
    
    # print(response)

    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())

    # print(fr)
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#--------------------------------------------------------------

def get_ec2_datapoints():

    dps_avg = []
    dps_time = []

    dp = cw_client.get_metric_statistics(
        Period=300,
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        EndTime=datetime.datetime.utcnow(),
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistics=['Average'],
        Dimensions=[{'Name':'InstanceId', 'Value':'i-0e81bafe1ec8a68f8'}]
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
    # print(sorted_datapoint)
    dt = dps_time[-10:]
    da = dps_avg[-10:]
    print(da)

    return json.dumps(dt), json.dumps(da)

