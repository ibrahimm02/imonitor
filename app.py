from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, flash
from flask_bootstrap import Bootstrap
import boto3
from boto3 import Session
from flask_cors import CORS
from datetime import datetime, timedelta, date
from operator import itemgetter
import json
import base64
import io
from collections import defaultdict

app = Flask(__name__)
Bootstrap(app)
CORS(app)
app.secret_key = 'flash-secret'

#---- CONSTANTS ------------------------------------------------------------------------------------------------#
REGION_NAME = "us-east-1"


#---- VARIABLES ------------------------------------------------------------------------------------------------#

ec2_client = boto3.client("ec2", region_name=REGION_NAME)

ec2_resource = boto3.resource('ec2', region_name=REGION_NAME)

cw_client = boto3.client('cloudwatch')

s3_client = boto3.client('s3')

s3_resource = boto3.resource('s3')

rds_client = boto3.client("rds", region_name=REGION_NAME)

current_region = ec2_client.meta.region_name

#---- INDEX ------------------------------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('landing.html')

#----AWS OVERVIEW ------------------------------------------------------------------------------------------------#

@app.route('/aws/overview')
def aws_overview():

    ec2_states = ec2_state_stats()

    response = ec2_client.describe_instances()

    ec2_CPUUtilization = get_ec2_CPUUtilization()
    ec2_CPUCreditUsage = get_ec2_CPUCreditUsage()

    size_count = s3_objects_size()

    rds_states = rds_state_stats()
    rds, rds_totalStorage, rds_insCnt = get_rds_instance_details()
    rds_CPUUtilization = get_rds_graph(type='CPUUtilization')  
    rds_FreeableMemory = get_rds_graph(type='freeableMemory') 

    ebs_volumes, ebs_vol_count, ebs_unattached_count = aws_ebs_volumes()

    if not(response):
        return render_template("message.html",message="No Instances running. Create an instance first")

    return render_template('aws/overview.html', 
    current_region=current_region, 
    response=response,
    ec2_states=ec2_states,
    ec2_CPUUtilization=ec2_CPUUtilization,
    ec2_CPUCreditUsage=ec2_CPUCreditUsage,
    size_count=size_count,
    rds_states=rds_states,
    rds_insCnt=rds_insCnt,
    rds_totalStorage=rds_totalStorage,
    rds_CPUUtilization=rds_CPUUtilization,
    rds_FreeableMemory=rds_FreeableMemory,
    ebs_volumes=ebs_volumes,
    ebs_vol_count=ebs_vol_count,
    ebs_unattached_count=ebs_unattached_count,
    )

#----GCP OVERVIEW---------------------------------------------------------------------------------------------------#

@app.route('/gcp/overview')
def gcp_overview():

    return render_template('gcp/gcp_overview.html')

#----AZURE OVERVIEW---------------------------------------------------------------------------------------------------#

@app.route('/azure/overview')
def azure_overview():

    return render_template('azure/azure_overview.html')

#---- TEST ------------------------------------------------------------------------------------------------#

# @app.route('/members')
# def members():
#      return render_template('/index.html', message="No Instances running. Create an instance first" )
    # return {"members": ["Member1", "Member2", "Member3"]}

#---- ACCOUNT ------------------------------------------------------------------------------------------------#

@app.route('/aws/account')
def aws_account():

    account_details = boto3.client("sts").get_caller_identity()


    return render_template('account.html', account_details=account_details)

#---- AWS/EC2 ------------------------------------------------------------------------------------------------#

@app.route('/aws/ec2-instance-all')
def ec2_instances():
    response = ec2_client.describe_instances()

    if not(response):
        return render_template("message.html",message="No Instances running. Create an instance first")

    else:
        return response

@app.route('/aws/ec2')
def aws_ec2():
    # # ec2_client = boto3.client("ec2", region_name="us-west-2")
    # reservations = ec2_client.describe_instances(Filters=[
    #     {
    #         "Name": "instance-state-name",
    #         "Values": ["running"],
    #     }
    # ]).get("Reservations")

    # for reservation in reservations:
    #     for instance in reservation["Instances"]:
    #         instance_id = instance["InstanceId"]
    #         instance_type = instance["InstanceType"]
    #         public_ip = instance["PublicIpAddress"]
    #         private_ip = instance["PrivateIpAddress"]
    #         print(f"{instance_id}, {instance_type}, {public_ip}, {private_ip}")
        
    # return reservations

    instances = ec2_resource.instances.all()
    
    active_instances =  get_active_instance_count()

    total_instances = len([instance for instance in instances]); 

    ec2_CPUUtilization = get_ec2_CPUUtilization()
    ec2_DiskReadOps = get_ec2_DiskReadOps()
    ec2_DiskWriteOps = get_ec2_DiskWriteOps()
    ec2_NetworkIn = get_ec2_NetworkIn()
    ec2_NetworkOut = get_ec2_NetworkOut()
    ec2_CPUCreditUsage = get_ec2_CPUCreditUsage()
    ec2_CPUCreditBalance = get_ec2_CPUCreditBalance()
    ec2_DiskReadBytes = get_ec2_DiskReadBytes()
    ec2_DiskWriteBytes = get_ec2_DiskWriteBytes()


    # ec2_metrics = ec2_metrics_amm()

    ec2_states = ec2_state_stats()
    # data = {'chart_data': ec2_states}
    
    if not(instances):
        return render_template("aws/aws-ec2/ec2.html", info="No instance Data")

    return render_template("aws/aws-ec2/aws_ec2.html", 
        instances=instances, 
        active_instances=active_instances, 
        total_instances=total_instances, 
        ec2_CPUUtilization=ec2_CPUUtilization, 
        ec2_DiskReadOps=ec2_DiskReadOps,
        ec2_DiskWriteOps=ec2_DiskWriteOps,
        ec2_NetworkIn=ec2_NetworkIn,
        ec2_NetworkOut=ec2_NetworkOut,
        ec2_CPUCreditUsage=ec2_CPUCreditUsage,
        ec2_CPUCreditBalance=ec2_CPUCreditBalance,
        ec2_DiskReadBytes=ec2_DiskReadBytes,
        ec2_DiskWriteBytes=ec2_DiskWriteBytes,

        # ec2_metrics=ec2_metrics, 
        ec2_states=ec2_states)

# --------------------------------------------------------------

# get list of all running instances
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

#---------------------------------------------------------------
def test1():

    # instance = ec2_resource.instances.filter(Filters=[{
    #     'Name': 'instance-state-name',
    #     'Values': ['running']}])

    # ec2info = defaultdict()
    # for tag in instance.tags:
    #     if 'Name'in tag['Key']:
    #         print(tag['Key'])
    #         name = tag['Value']
    # # Add instance info to a dictionary    \
    # print(instance.get('Instances'))
    # ec2info[instance.id] = {
    #     'Name': name,
    #     'Instance ID': instance.id,
    #     'Type': instance.instance_type,
    #     'State': instance.state['Name'],
    #     'Private IP': instance.private_ip_address,
    #     'Public IP': instance.public_ip_address,
    #     'Launch Time': instance.launch_time
    # }
    # attributes = ['Instance ID', 'Type', 'State', 'Private IP', 'Public IP', 'Launch Time']
    # for instance_id, instance in ec2info.items():
    #     for key in attributes:
    #         print("{0}: {1}".format(key, instance[key]))
    #     print("------")

    testList = list(ec2_resource.instances.all())

    if len(testList) > 0:
        for item in testList:
            print(item.tags)

# test1()

# --------------------------------------------------------------

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

# def request_metric(client,InstanceId):

#     startTime= datetime.today() + timedelta(days=-1)
#     startTimeFormat = startTime.strftime('%Y-%m-%d') + ' 00:00:00'

#     endTime = datetime.today() + timedelta(days=-1)
#     endTimeFormat = endTime.strftime('%Y-%m-%d') + ' 23:59:59'

#     response = client.get_metric_statistics(
#         Namespace = 'AWS/EC2',
#         Period = 86400,
#         StartTime = startTimeFormat,
#         EndTime = endTimeFormat,
#         MetricName = 'CPUUtilization',
#         Statistics=['Maximum','Minimum','Average'],
#         Dimensions = [
#             {
#                 'Name': 'InstanceId',
#                 'Value': InstanceId
#             }   
#         ],        
#     )

#     return response["Datapoints"]  

# request_metric(ec2_resource,"i-043567371c05991f9")

# --------------------------------------------------------------

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

#-----------------------------------------------------------------------------
def instance_output_format(instance_data):
    response={
        "InstanceId":instance_data.get("InstanceId",''),
        "InstanceType":instance_data.get("InstanceType",""),
        "State":instance_data["State"]["Name"],
        "PrivateIpAddress":instance_data.get("PrivateIpAddress",""),
        "PublicIpAddress":instance_data.get("PublicIpAddress",""),
        "SecurityGroups":instance_data.get("SecurityGroups",""),
    }
    return response

#---- EC2 GRAPH-1 ------------------------------------------------------------------------------------------------#

def get_ec2_CPUUtilization():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "CPUUtilization", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-2 ------------------------------------------------------------------------------------------------#

def get_ec2_DiskReadOps():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "DiskReadOps", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-3 ------------------------------------------------------------------------------------------------#

def get_ec2_DiskWriteOps():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "DiskWriteOps", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-4 ------------------------------------------------------------------------------------------------#

def get_ec2_NetworkIn():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "NetworkIn", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-5 ------------------------------------------------------------------------------------------------#

def get_ec2_NetworkOut():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "NetworkOut", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-6 ------------------------------------------------------------------------------------------------#

def get_ec2_CPUCreditUsage():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "CPUCreditUsage", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-7 ------------------------------------------------------------------------------------------------#

def get_ec2_CPUCreditBalance():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "CPUCreditBalance", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-8 ------------------------------------------------------------------------------------------------#

def get_ec2_DiskReadBytes():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "DiskReadBytes", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-9 ------------------------------------------------------------------------------------------------#

def get_ec2_DiskWriteBytes():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "DiskWriteBytes", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-10 ------------------------------------------------------------------------------------------------#

def get_ec2_DiskWriteOps():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "DiskWriteOps", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph

#---- EC2 GRAPH-11 ------------------------------------------------------------------------------------------------#

def get_ec2_DiskWriteOps():
  
    data=[]
    response_data=[]
    for instance in ec2_client.describe_instances()["Reservations"]:
        for each_in in instance["Instances"]:
            response_data.append(instance_output_format(each_in)) 

    instance_ids=[i["InstanceId"] for i in response_data]
    for ins in instance_ids:
            data.append(["AWS/EC2", "DiskWriteOps", "InstanceId",str(ins)])
            filter_data={"metrics":data}

    # print(data)

    response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())
    
    ec2_graph = fr.decode('utf-8')

    return ec2_graph


#-----------------------------------------------------------------------------

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

#-----------------------------------------------------------------------------

now = datetime.utcnow() # Now time in UTC format 
past = now - timedelta(minutes=60) # Minus 60 minutes

def ec2_metrics_amm():

    cw_client = boto3.client('cloudwatch')
    
    metrics = {}
    metrics_holder = []

    response = ec2_client.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            #print(instance["InstanceId"])
            try:
                EC2CPUUtilization = cw_client.get_metric_statistics(
                    Namespace = 'AWS/EC2',
                    MetricName = 'CPUUtilization',
                    StartTime=datetime.utcnow() - timedelta(days=7) ,
                    EndTime=datetime.utcnow(),
                    Period = 86400,
                    Statistics=['Maximum','Minimum','Average'],
                    Dimensions = [
                        {
                            'Name': 'InstanceId',
                            'Value': instance['InstanceId']
                        }   
                    ]        
                ) 
            except Exception():
                print(Exception)
            #  return print(EC2CPUUtilization)
                    
            datapoints = EC2CPUUtilization['Datapoints']     # CPU Utilization results                
            sorted_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))

                # print(sorted_datapoint)

            for i in range(len(sorted_datapoint)):
                sorted_datapoint[i]['sort_by'] = i

                print(sorted_datapoint)

            last_datapoint = sorted_datapoint[-1]  # Last result
            last_max_utilization = last_datapoint['Maximum'] # Last utilization
            last_min_utilization = last_datapoint['Minimum'] # Last utilization
            last_avg_utilization = last_datapoint['Average'] # Last utilization
                                            
                                            
            # avg_load = round((last_avg_utilization / 100.0) 3)  # Last utilization in %
            # timestamp = str(last_datapoint['Timestamp'])         # Last utilization timestamp

            # max_load = round((last_max_utilization / 100.0), 3)
            # min_load = round((last_min_utilization / 100.0), 3)

            avg_load = round((last_avg_utilization), 3)  # Last utilization in %
            timestamp = str(last_datapoint['Timestamp'])         # Last utilization timestamp

            max_load = round((last_max_utilization), 3)
            min_load = round((last_min_utilization), 3)
            #print("{0} load at {1}".format(load, timestamp))

            # result['selected_datapoints'] = datapoints
            # result['last_avg'] = last_avg_utilization
            # result['last_min'] = last_min_utilization
            # result['last_max'] = last_max_utilization
            # result['avg_load'] = avg_load
            # result['last_time'] = timestamp                
            # instance['mainState'] = result
            # instance_holder.append(instance)
            metrics['last_avg'] = avg_load
            metrics['last_max'] = max_load
            metrics['last_min'] = min_load
            
            metrics_holder.append(metrics)
            # response["header"][""]
    return metrics_holder
# ec2_metrics_amm()

#-----------------------------------------------------------------------------

@app.route('/ec2-instance-start', methods=["POST"])
def ec2_instance_start():
    key = request.form['instance']

    instance = ec2_resource.Instance(key)
    instance.start()

    print(f'Starting EC2 instance: {instance.id}')
    
    # instance.wait_until_running()

    print(f'EC2 instance "{instance.id}" has been started')
    flash(f'EC2 instance "{instance.id}" has been started')
    return redirect(url_for('aws_ec2'))
#-------------------------------------------------------------------

@app.route('/ec2-instance-stop', methods=["POST"])
def ec2_instance_stop():
    key = request.form['instance']

    instance = ec2_resource.Instance(key)
    instance.stop()

    print(f'Stopping EC2 instance: {instance.id}')
    
    # instance.wait_until_running()

    print(f'EC2 instance "{instance.id}" has been stopped')

    flash(f'EC2 instance "{instance.id}" has been stopped')
    return redirect(url_for('aws_ec2'))

#---------------------------------------------------------------------
@app.route('/ec2-instance-data', methods=["POST"])
def ec2_instance_data():

    key = request.form['instance']

   
    ec2_CPUUtilization = ec2_instance_metrics(type='CPUUtilization', ins_id=key)
    ec2_DiskReadOps = ec2_instance_metrics(type='DiskReadOps', ins_id=key)
    ec2_DiskWriteOps = ec2_instance_metrics(type='DiskWriteOps', ins_id=key)
    ec2_NetworkIn = ec2_instance_metrics(type='NetworkIn', ins_id=key)
    ec2_NetworkOut = ec2_instance_metrics(type='NetworkOut', ins_id=key)
    ec2_CPUCreditUsage = ec2_instance_metrics(type='CPUCreditUsage', ins_id=key)
    ec2_CPUCreditBalance = ec2_instance_metrics(type='CPUCreditBalance', ins_id=key)
    ec2_DiskReadBytes = ec2_instance_metrics(type='DiskReadBytes', ins_id=key)
    ec2_DiskWriteBytes = ec2_instance_metrics(type='DiskWriteBytes', ins_id=key)


    # Helper method to serialize datetime fields
    def json_datetime_serializer(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))

    response = ec2_client.describe_instances(
        InstanceIds=[
            key,
        ],
    )

    # print(f'Instance {key} attributes:')

    for reservation in response['Reservations']:
        json.dumps(
                reservation,
                indent=4,
                default=json_datetime_serializer
            )
    
    return render_template('aws/aws-ec2/aws_ec2_instance_data.html', 
                            instance=reservation,
                            ec2_CPUUtilization=ec2_CPUUtilization,
                            ec2_DiskReadOps=ec2_DiskReadOps,
                            ec2_DiskWriteOps=ec2_DiskWriteOps,
                            ec2_NetworkIn= ec2_NetworkIn,
                            ec2_NetworkOut= ec2_NetworkOut,
                            ec2_CPUCreditUsage= ec2_CPUCreditUsage,
                            ec2_CPUCreditBalance=ec2_CPUCreditBalance,           
                            ec2_DiskReadBytes=ec2_DiskReadBytes,             
                            ec2_DiskWriteBytes= ec2_DiskWriteBytes
                            )


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
    rds_graph = fr.decode('utf-8')

    return rds_graph
    
#---- AWS/EBS -----------------------------------------------------------------------------------------------#
def aws_ebs_volumes():

    ebs_vol = ec2_resource.volumes.all()

    vol_count = 0

    # for volume in ebs_vol:
    #     print('Evaluating volume {0}'.format(volume.id))
    #     print('The number of attachments for this volume is {0}'.format(len(volume.attachments)))

    ebs_status = ec2_client.describe_volumes(
    Filters=[
        {
            'Name': 'status',
            'Values': [
                'available',
            ]
        },
    ],
    
    )
    unattached_count = (len(ebs_status))

    # print(ebs_status)

    for volume in ebs_vol:
        print(volume)
        vol_count += 1
    # print(f'Count:',  vol_count)

    return volume, vol_count, unattached_count


#---- AWS/S3 ------------------------------------------------------------------------------------------------#

@app.route('/aws/s3')
def aws_s3():
    # Retrieve the list of existing buckets
    
    response = s3_client.list_buckets()

    size_count = s3_objects_size()

    s3_graph = aws_get_s3_metrics()

    if len(response['Buckets'])==0:
        return f'No Buckets!'
    # Output the bucket names
    else:
        print('Existing buckets:')
        for bucket in response['Buckets']:
            print(f'  {bucket["Name"]}')
        return render_template("aws/aws_s3.html", response=response, size_count=size_count, s3_graph=s3_graph)

#-------------------------------------------------------

def aws_get_s3_bucket_size():

    cw = boto3.client('cloudwatch')
    s3client = boto3.client('s3')

    # Get a list of all buckets
    allbuckets = s3client.list_buckets()

    # Header Line for the output going to standard out
    print('Bucket'.ljust(45) + 'Size in Bytes'.rjust(25))

    # Iterate through each bucket
    for bucket in allbuckets['Buckets']:
        # For each bucket item, look up the cooresponding metrics from CloudWatch
        response = cw.get_metric_statistics(Namespace='AWS/S3',
                                            MetricName='BucketSizeBytes',
                                            Dimensions=[
                                                {'Name': 'BucketName', 'Value': bucket['Name']},
                                                {'Name': 'StorageType', 'Value': 'StandardStorage'}
                                            ],
                                            Statistics=['Average'],
                                            Period=3600,
                                            StartTime=datetime.utcnow() - timedelta(days=7) ,
                                            EndTime=datetime.utcnow(),
                                            )
        # The cloudwatch metrics will have the single datapoint, so we just report on it. 

        print(response)
        for item in response["Datapoints"]:
            print(bucket["Name"].ljust(45) + str("{:,}".format(int(item["Average"]))).rjust(25))
            # Note the use of "{:,}".format.   
            # This is a new shorthand method to format output.
            # I just discovered it recently.

# aws_get_s3_bucket_size()

#-------------------------------------------------------
def s3_objects_size():

    data = []
    size = 0
    totalObject = 0

    allbuckets = s3_client.list_buckets()

    totalBucket = len(allbuckets['Buckets'])

    for bucket in allbuckets['Buckets']:
        bucket = s3_resource.Bucket(bucket["Name"])
        for obj in bucket.objects.all():
            totalObject 
            size += obj.size

    # print('total size:')
    roundSize = ("%.3f GB" % (size*1.0/1024/1024/1024))
    # print("%.3f GB" % (size*1.0/1024/1024/1024))
    # print('total count:')
    # print(totalCount)
    data.append({'total_size': roundSize, 'total_bucket': totalBucket, 'total_object': totalObject })
    return data


#-------------------------------------------------------

def aws_get_s3_metrics():
    # List metrics through the pagination interface
    response = cw_client.get_metric_statistics(
            MetricName='BucketSizeBytes',
            Namespace='AWS/S3',
            Dimensions=[
                {
                    'Name': 'BucketName',
                    'Value': 'project-test-bucket1'
                },
                {
                    'Name': 'StorageType',
                    'Value': 'StandardStorage'
                }
            ],
            Statistics=['Average'],
            Period=86400,
            StartTime=datetime.utcnow() - timedelta(days=14) ,
            EndTime=datetime.utcnow(),
        
    )
        
    print(response)

    ins_met = '{"metrics": [["AWS/S3", "BucketSizeBytes", "BucketName", "project-test-bucket1", "StorageType", "StandardStorage", "Statistics", "Average"]]}'

    response2 = cw_client.get_metric_widget_image(MetricWidget=ins_met)
    
    # print(response)

    bytes_data=io.BytesIO(response2["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())

    # print(fr)
    s3_graph = fr.decode('utf-8')

    return s3_graph


#---- AWS/RDS ------------------------------------------------------------------------------------------------#

@app.route('/aws/rds')
def aws_rds():

    rds_CPUUtilization = get_rds_graph(type='CPUUtilization')
    # rds_DatabaseConnections = get_rds_instancelevel_metrics(type='databaseConnections')    
    rds_FreeStorageSpace = get_rds_graph(type='freeStorageSpace')    
    rds_FreeableMemory = get_rds_graph(type='freeableMemory')    
    rds_ReadIOPS = get_rds_graph(type='readIOPS')
    rds_WriteIOPS = get_rds_graph(type='writeIOPS')    
    rds_ReadThroughput = get_rds_graph(type='readThroughput')    
    rds_WriteThroughput = get_rds_graph(type='writeThroughput')    
    rds_ReadLatency = get_rds_graph(type='readLatency')     
    rds_WriteLatency = get_rds_graph(type='writeLatency')    

    rds_states = rds_state_stats()

    response, rds_totalStorage, rds_insCnt = get_rds_instance_details()

    return render_template('aws/aws_rds.html', 
        response=response,
        rds_CPUUtilization=rds_CPUUtilization,
        # rds_DatabaseConnections=rds_DatabaseConnections,
        rds_FreeStorageSpace=rds_FreeStorageSpace,
        rds_FreeableMemory=rds_FreeableMemory,
        rds_ReadIOPS=rds_ReadIOPS,
        rds_WriteIOPS=rds_WriteIOPS,
        rds_WriteThroughput=rds_WriteThroughput,
        rds_ReadThroughput=rds_ReadThroughput,
        rds_WriteLatency=rds_WriteLatency,
        rds_ReadLatency=rds_ReadLatency,
        rds_states=rds_states,
        rds_insCnt=rds_insCnt,
        rds_totalStorage=rds_totalStorage
        )
#-------------------------------------------------------

def get_rds_graph(type):
    
    data=[]
    response_data=[]
    res = rds_client.describe_db_instances()

    for i in res['DBInstances']:   
            response_data.append({
            "DBInstanceIdentifier": i['DBInstanceIdentifier']
        })

    # print(response_data)
  
    instance_ids=[i["DBInstanceIdentifier"] for i in response_data]
    for ins in instance_ids:

        if type == 'CPUUtilization':
            data.append(["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
            print(filter_data)
        elif type == 'freeStorageSpace':
            data.append(["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'freeableMemory':
            data.append(["AWS/RDS", "FreeableMemory", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'readIOPS':
            data.append(["AWS/RDS", "ReadIOPS", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'writeIOPS':
            data.append(["AWS/RDS", "WriteIOPS", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'readThroughput':
            data.append(["AWS/RDS", "ReadThroughput", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'writeThroughput':
            data.append(["AWS/RDS", "WriteThroughput", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'readLatency':
            data.append(["AWS/RDS", "ReadLatency", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'writeLatency':
            data.append(["AWS/RDS", "WriteLatency", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}


        img = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
        bytes_data=io.BytesIO(img["MetricWidgetImage"])
        fr=base64.b64encode(bytes_data.getvalue())
        
        rds_graph = fr.decode('utf-8')

        return rds_graph

#-------------------------------------------------------
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
    print(roundSize)
    print(f'instance count: ', ins_cnt)


    return response, roundSize, ins_cnt
#-------------------------------------------------------
def get_rds_instancelevel_metrics(type):
    
    if type == 'CPUUtilization':
        rds = '{"metrics": [["AWS/RDS", "CPUUtilization"]]}'
    elif type == 'databaseConnections':
        rds = '{"metrics": [["AWS/RDS", "DatabaseConnections"]]}'
    elif type == 'freeStorageSpace':
        rds = '{"metrics": [["AWS/RDS", "FreeStorageSpace"]]}'
    elif type == 'freeableMemory':
        rds = '{"metrics": [["AWS/RDS", "FreeableMemory"]]}'
    elif type == 'readIOPS':
        rds = '{"metrics": [["AWS/RDS", "ReadIOPS"]]}'
    elif type == 'writeIOPS':
        rds = '{"metrics": [["AWS/RDS", "WriteIOPS"]]}'
    elif type == 'readThroughput':
        rds = '{"metrics": [["AWS/RDS", "ReadThroughput"]]}'    
    elif type == 'writeThroughput':
        rds = '{"metrics": [["AWS/RDS", "WriteThroughput"]]}'
    elif type == 'readLatency':
        rds = '{"metrics": [["AWS/RDS", "ReadLatency"]]}'
    elif type == 'writeLatency':
        rds = '{"metrics": [["AWS/RDS", "WriteLatency"]]}'
    
    
    response = cw_client.get_metric_widget_image(MetricWidget=rds)
    
    # print(response)

    bytes_data=io.BytesIO(response["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())

    # print(fr)
    rds_graph = fr.decode('utf-8')

    return rds_graph
#------------------------------------------------------------------


#------------------------------------------------------------------
def get_rds_metrics():
    
    now = datetime.utcnow() # Now time in UTC format 
    past = now - timedelta(minutes=60) # Minus 60 minutes
 
    response = cw_client.get_metric_statistics(
        Period=86400,
        StartTime=datetime.utcnow() - timedelta(days=7) ,
        EndTime=datetime.utcnow(),
        MetricName='CPUUtilization',
        Namespace='AWS/RDS',
        Statistics=['Maximum'],
        Dimensions=[{'Name':'DBInstanceIdentifier', 'Value':'database-1'}]
        )
    return print(response)


# get_rds_metrics()

#------------------------------------------------------------------
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

#------------------------------------------------

@app.route('/aws/rds/rds-instance-start', methods=["POST"])
def rds_instance_start():
    key = request.form['instance']

    dbinstance = rds_client.start_db_instance(DBInstanceIdentifier=key)

    print(f'Starting RDS instance: {dbinstance["DBInstance"]["DBInstanceIdentifier"]}')
    
    # # instance.wait_until_running()

    print(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been started')
    flash(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been started')
    return redirect(url_for('aws_rds'))

#------------------------------------------------

@app.route('/aws/rds/rds-instance-stop', methods=["POST"])
def rds_instance_stop():
    key = request.form['instance']

    dbinstance = rds_client.stop_db_instance(DBInstanceIdentifier=key)
   
    print(f'Stopping RDS instance: {dbinstance["DBInstance"]["DBInstanceIdentifier"]}')
    
    # instance.wait_until_running()

    print(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been stopped')
    flash(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been stopped')

    return redirect(url_for('aws_rds'))

#---------------------------------------------------------------

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

#---------------------------------------------------------------
@app.route('/aws/rds-all')
def rds_all():

    data = []
    size = 0
    totalObject = 0

    response = rds_client.describe_db_instances()

    for i in response['DBInstances']:   
        try:
            # print(i["AllocatedStorage"])
            size += (i["AllocatedStorage"])
        except Exception as ex:
            continue
            pass
        
        print(size)
        
        # bucket = s3_resource.Bucket(bucket["Name"])
        # for obj in bucket.objects.all():
        #     totalObject 
        #     size += obj.size

    # print('total size:')

    # roundSize = ("%.3f GB" % (size*1.0/1024/1024/1024))
    
#----------------------------------------------------------------




#---- AWS/LAMBDA ------------------------------------------------------------------------------------------------#

@app.route('/aws/lambda-instance-all')
def lambda_instances():
    lambda_client = boto3.client('lambda')
    response = lambda_client.list_functions()
    return response

#---- AWS/ELASTIC LOAD BALANCER ------------------------------------------------------------------------------------------------#

@app.route('/aws/elb-instance-all')
def elb_instances():
    elb_client = boto3.client('elb')
    response = elb_client.describe_load_balancers()
    return response

#---- AWS/ELASTIC BEAN STALK ------------------------------------------------------------------------------------------------#

@app.route('/aws/elasticbeanstalk-instance-all')
def elasticbeanstalk_instances():
    elasticbeanstalk_client = boto3.client('elasticbeanstalk')
    response = elasticbeanstalk_client.describe_environments()
    return response

#---- AWS/ELASTIC CONTAINER SERVICE ------------------------------------------------------------------------------------------------#

@app.route('/aws/ecs-instance-all')
def ecs_instances():
    ecs_client = boto3.client('ecs')
    response = ecs_client.describe_clusters(
        clusters=[
            'string',
        ]
    )
    return response

#---- AWS/ELASTIC FILE SYSTEM ------------------------------------------------------------------------------------------------#

@app.route('/aws/efs-instance-all')
def efs_instances():
    efs_client = boto3.client('efs')
    response = efs_client.describe_file_systems(
        MaxItems=123,
        # Marker='string',
        # CreationToken='string',
        # FileSystemId='string'
    )
    return response

#-----COSTS --------#
def get_costs():
    client = boto3.client('ce')

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': '2023-01-08',
            'End': '2023-01-09'
        },
        Metrics=['AmortizedCost'],
        Granularity='DAILY',
  
    )
    from pprint import pprint
    pprint(response)

# get_costs()
#-------------------------------------------------------------#


#---- ERROR HANDLERS ------------------------------------------------------------------------------------------------#

# Page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500









if __name__ == "__main__":
    app.run(debug=True)