from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, flash
import boto3
from flask_cors import CORS
from operator import itemgetter
import json
import base64
import io
import datetime
import statistics


app = Flask(__name__)
CORS(app)
app.secret_key = 'flash-secret'

#---- CONSTANTS ------------------------------------------------------------------------------------------------#
REGION_NAME = "us-east-1"


#---- VARIABLES ------------------------------------------------------------------------------------------------#

ec2_client = boto3.client("ec2", region_name=REGION_NAME)

ec2_resource = boto3.resource('ec2', region_name=REGION_NAME)

cw_client = boto3.client('cloudwatch', region_name=REGION_NAME)

s3_client = boto3.client('s3')

s3_resource = boto3.resource('s3')

rds_client = boto3.client("rds", region_name=REGION_NAME)

cf_client = boto3.client('cloudfront')

current_region = ec2_client.meta.region_name

from iMonitor.aws.aws import aws_bp
from iMonitor.azure.azure import azure_bp
from iMonitor.gcp.gcp import gcp_bp
#---- BLUEPRINTS ------------------------------------------------------------------------------------------------#
app.register_blueprint(aws_bp, url_prefix='/aws')
app.register_blueprint(azure_bp, url_prefix='/azure')
app.register_blueprint(gcp_bp, url_prefix='/gcp')

#---- INDEX ------------------------------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('landing.html')

# #----AWS OVERVIEW ------------------------------------------------------------------------------------------------#

# @app.route('/aws/overview')
# def aws_overview():

#     ec2_states = ec2_state_stats()

#     response = ec2_client.describe_instances()

#     ec2_CPUUtilization = get_ec2_CPUUtilization()
#     ec2_CPUCreditUsage = get_ec2_CPUCreditUsage()

#     s3_size_count = s3_objects_size()
#     s3_graph_NOO = s3_graph("NumberOfObjects")

#     rds_states = rds_state_stats()
#     rds, rds_totalStorage, rds_insCnt = get_rds_instance_details()
#     rds_CPUUtilization = get_rds_graph(type='CPUUtilization')  
#     rds_FreeableMemory = get_rds_graph(type='freeableMemory') 

#     cf_4ER_graph = get_cloudfront_metrics("4xxErrorRate")
#     cf_5ER_graph = get_cloudfront_metrics("5xxErrorRate")

#     ebs_volumes, ebs_vol_count, ebs_unattached_count, ebsGraph = aws_ebs_volumes()
#     ebs_VRB_graph = get_ebs_graph("VolumeReadBytes")
#     ebs_VWB_graph = get_ebs_graph("VolumeWriteBytes")

#     if not(response):
#         return render_template("message.html",message="No Instances running. Create an instance first")

#     return render_template('aws/overview.html', 
#     current_region=current_region, 
#     response=response,
#     ec2_states=ec2_states,
#     ec2_CPUUtilization=ec2_CPUUtilization,
#     ec2_CPUCreditUsage=ec2_CPUCreditUsage,
#     s3_size_count=s3_size_count,
#     s3_graph_NOO=s3_graph_NOO,
#     rds_states=rds_states,
#     rds_insCnt=rds_insCnt,
#     rds_totalStorage=rds_totalStorage,
#     rds_CPUUtilization=rds_CPUUtilization,
#     rds_FreeableMemory=rds_FreeableMemory,
#     cf_4ER_graph=cf_4ER_graph,
#     cf_5ER_graph=cf_5ER_graph,
#     ebs_volumes=ebs_volumes,
#     ebs_vol_count=ebs_vol_count,
#     ebs_unattached_count=ebs_unattached_count,
#     ebs_VRB_graph=ebs_VRB_graph,
#     ebs_VWB_graph=ebs_VWB_graph
#     )

# #----GCP OVERVIEW---------------------------------------------------------------------------------------------------#

# @app.route('/gcp/overview')
# def gcp_overview():

#     return render_template('gcp/gcp_overview.html')

# #----AZURE OVERVIEW---------------------------------------------------------------------------------------------------#

# @app.route('/azure/overview')
# def azure_overview():

#     return render_template('azure/azure_overview.html')

# #---- TEST ------------------------------------------------------------------------------------------------#

# # @app.route('/members')
# # def members():
# #      return render_template('/index.html', message="No Instances running. Create an instance first" )
#     # return {"members": ["Member1", "Member2", "Member3"]}

# #---- ACCOUNT ------------------------------------------------------------------------------------------------#

# @app.route('/aws/account')
# def aws_account():

#     account_details = boto3.client("sts").get_caller_identity()


#     return render_template('account.html', account_details=account_details)

# #---- AWS/EC2 ------------------------------------------------------------------------------------------------#

# @app.route('/aws/ec2-instance-all')
# def ec2_instances():
#     response = ec2_client.describe_instances()

#     if not(response):
#         return render_template("message.html",message="No Instances running. Create an instance first")

#     else:
#         return response

# @app.route('/aws/ec2')
# def aws_ec2():

#     instances = ec2_resource.instances.all()
    
#     active_instances =  get_active_instance_count()

#     total_instances = len([instance for instance in instances]); 

#     ec2_CPUUtilization = get_ec2_CPUUtilization()
#     ec2_DiskReadOps = get_ec2_DiskReadOps()
#     ec2_DiskWriteOps = get_ec2_DiskWriteOps()
#     ec2_NetworkIn = get_ec2_NetworkIn()
#     ec2_NetworkOut = get_ec2_NetworkOut()
#     ec2_CPUCreditUsage = get_ec2_CPUCreditUsage()
#     ec2_CPUCreditBalance = get_ec2_CPUCreditBalance()
#     ec2_DiskReadBytes = get_ec2_DiskReadBytes()
#     ec2_DiskWriteBytes = get_ec2_DiskWriteBytes()

#     avg_util, max_util, min_util = get_ec2_metrics_amm()

#     ec2_states = ec2_state_stats()

#     if not(instances):
#         return render_template("aws/aws-ec2/ec2.html", info="No instance Data")

#     return render_template("aws/aws-ec2/aws_ec2.html", 
#         instances=instances, 
#         active_instances=active_instances, 
#         total_instances=total_instances, 
#         ec2_CPUUtilization=ec2_CPUUtilization, 
#         ec2_DiskReadOps=ec2_DiskReadOps,
#         ec2_DiskWriteOps=ec2_DiskWriteOps,
#         ec2_NetworkIn=ec2_NetworkIn,
#         ec2_NetworkOut=ec2_NetworkOut,
#         ec2_CPUCreditUsage=ec2_CPUCreditUsage,
#         ec2_CPUCreditBalance=ec2_CPUCreditBalance,
#         ec2_DiskReadBytes=ec2_DiskReadBytes,
#         ec2_DiskWriteBytes=ec2_DiskWriteBytes,
#         avg_util=avg_util, max_util=max_util, min_util=min_util,
#         ec2_states=ec2_states,
#         )

# # --------------------------------------------------------------

# # get list of all running instances
# def get_running_instances():
#     reservations = ec2_client.describe_instances(Filters=[
#         {
#             "Name": "instance-state-name",
#             "Values": ["running"],
#         }
#     ]).get("Reservations")


#     for reservation in reservations:
#         for instance in reservation["Instances"]:
#             instance_id = instance["InstanceId"]
#             instance_type = instance["InstanceType"]
#             public_ip = instance["PublicIpAddress"]
#             private_ip = instance["PrivateIpAddress"]
#             print(f"{instance_id}, {instance_type}, {public_ip}, {private_ip}")

# #---------------------------------------------------------------

# # get_running_instances()

# # @app.route('/aws-ec2-instances')
# # def aws_ec2_instances():
# #     ec2 = boto3.client('ec2')
# #     # response = ec2.describe_instances()
# #     if sys.argv[1] == 'ON':
# #         response = ec2.monitor_instances(InstanceIds=['i-0eadf739e14d3b325'])
# #     else:
# #         response = ec2.unmonitor_instances(InstanceIds=['i-0eadf739e14d3b325'])

# #     return response

# # --------------------------------------------------------------

# def get_active_instance_count():

#     INSTANCE_STATE = 'running'

#     instances = ec2_resource.instances.filter(
#         Filters=[
#             {
#                 'Name': 'instance-state-name',
#                 'Values': [
#                     INSTANCE_STATE
#                 ]
#             }
#         ]
#     )

#     # print(f'Instances in state "{INSTANCE_STATE}":')
#     count = 0
#     for instance in instances:
#         # print(f'  - Instance ID: {instance.id}')
#         count += 1
    
#     return count

# #-----------------------------------------------------------------------------
# def instance_output_format(instance_data):
#     response={
#         "InstanceId":instance_data.get("InstanceId",''),
#         "InstanceType":instance_data.get("InstanceType",""),
#         "State":instance_data["State"]["Name"],
#         "PrivateIpAddress":instance_data.get("PrivateIpAddress",""),
#         "PublicIpAddress":instance_data.get("PublicIpAddress",""),
#         "SecurityGroups":instance_data.get("SecurityGroups",""),
#     }
#     return response

# #---- EC2 GRAPH-1 ------------------------------------------------------------------------------------------------#

# def get_ec2_CPUUtilization():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "CPUUtilization", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-2 ------------------------------------------------------------------------------------------------#

# def get_ec2_DiskReadOps():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "DiskReadOps", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-3 ------------------------------------------------------------------------------------------------#

# def get_ec2_DiskWriteOps():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "DiskWriteOps", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-4 ------------------------------------------------------------------------------------------------#

# def get_ec2_NetworkIn():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "NetworkIn", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-5 ------------------------------------------------------------------------------------------------#

# def get_ec2_NetworkOut():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "NetworkOut", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-6 ------------------------------------------------------------------------------------------------#

# def get_ec2_CPUCreditUsage():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "CPUCreditUsage", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-7 ------------------------------------------------------------------------------------------------#

# def get_ec2_CPUCreditBalance():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "CPUCreditBalance", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-8 ------------------------------------------------------------------------------------------------#

# def get_ec2_DiskReadBytes():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "DiskReadBytes", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-9 ------------------------------------------------------------------------------------------------#

# def get_ec2_DiskWriteBytes():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "DiskWriteBytes", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-10 ------------------------------------------------------------------------------------------------#

# def get_ec2_DiskWriteOps():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "DiskWriteOps", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph

# #---- EC2 GRAPH-11 ------------------------------------------------------------------------------------------------#

# def get_ec2_DiskWriteOps():
  
#     data=[]
#     response_data=[]
#     for instance in ec2_client.describe_instances()["Reservations"]:
#         for each_in in instance["Instances"]:
#             response_data.append(instance_output_format(each_in)) 

#     instance_ids=[i["InstanceId"] for i in response_data]
#     for ins in instance_ids:
#             data.append(["AWS/EC2", "DiskWriteOps", "InstanceId",str(ins)])
#             filter_data={"metrics":data}

#     # print(data)

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())
    
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph


# #-----------------------------------------------------------------------------

# def ec2_state_stats():
#     stats = {
#         "pending": 0,
#         "running": 0,
#         "shutting-down": 0,
#         "terminated": 0,
#         "stopping": 0,
#         "stopped": 0
#         }
    
#     qs_ = ec2_client.get_paginator('describe_instances')
#     response_ = qs_.paginate()
#     for rs in response_:
#         for reservation in rs['Reservations']:
#             for instance in reservation['Instances']:
#                 state = instance['State']['Name']
#                 stats[state] += 1
#     graph_data=[]
#     for i in stats.keys():
#         graph_data.append({"state":i,"value":int(stats[i])})
#     return (graph_data)

# #-----------------------------------------------------------------------------
# def get_ec2_metrics_amm():

#     dp_avg = []
#     dp_max = []
#     dp_min = []

#     reservations = ec2_client.describe_instances().get("Reservations")

#     # print(reservations)

#     # if not reservations:
#     #     print("list empty")
#     #     avg_uti = dp_avg.append(0)
#     #     max_uti = dp_max.append(0)
#     #     min_uti = dp_min.append(0)

#     # else:
#     #     print("list not empty")

#     for res in reservations:
#         for instance in res["Instances"]:

#             print(instance["InstanceId"])

#             response = cw_client.get_metric_statistics(
#                 MetricName = 'CPUUtilization',
#                 Namespace = 'AWS/EC2',
#                 Period = 86400,
#                 StartTime=datetime.datetime.utcnow() - datetime.timedelta(hours=3),
#                 EndTime=datetime.datetime.utcnow(),
#                 Statistics=['Maximum','Minimum','Average'],
#                 Dimensions = [
#                     {
#                         'Name': 'InstanceId',
#                         'Value': instance["InstanceId"]
#                     }   
#                 ],        
#             )

#             datapoints = response['Datapoints']

#             print(f'dp: ', datapoints)

#             for dp in datapoints:
            
#                 dp_avg.append(dp['Average'])
#                 dp_max.append(dp['Maximum'])
#                 dp_min.append(dp['Minimum'])

#     # avg_uti = round(sum(dp_avg)/len(dp_avg),3)
#     # max_uti = round(sum(dp_max)/len(dp_max),3)
#     # min_uti = round(sum(dp_min)/len(dp_min),3)
#     if dp_avg != [] or dp_max != [] or dp_min != []:

#         avg_uti = round(statistics.mean(dp_avg),3)
#         max_uti = round(statistics.mean(dp_max),3)
#         min_uti = round(statistics.mean(dp_min),3)

#     else:
#         avg_uti = (0)
#         max_uti = (0)
#         min_uti = (0)
    
#     return avg_uti, max_uti, min_uti


# # get_ec2_metrics_amm()

# #-----------------------------------------------------------------------------

# @app.route('/ec2-instance-start', methods=["POST"])
# def ec2_instance_start():

#     key = request.form['instance']
    
#     try:
#         instance = ec2_resource.Instance(key)
#         instance.start()
#         # print(f'Starting EC2 instance: {instance.id}')

#         # # instance.wait_until_running()

#         # print(f'EC2 instance "{instance.id}" has been started')
#         flash(f'EC2 instance "{instance.id}" has been started')
#     except:
#         return False

#     return redirect(url_for('aws_ec2'))

# #-------------------------------------------------------------------

# @app.route('/ec2-instance-stop', methods=["POST"])
# def ec2_instance_stop():
#     key = request.form['instance']

#     try:
#         instance = ec2_resource.Instance(key)
#         instance.stop()
#         # print(f'Stopping EC2 instance: {instance.id}')

#         # instance.wait_until_stopped()

#         # print(f'EC2 instance "{instance.id}" has been stopped')

#         flash(f'EC2 instance "{instance.id}" has been stopped')
#     except:
#         return False

#     return redirect(url_for('aws_ec2'))

# #---------------------------------------------------------------------
# @app.route('/ec2-instance-data', methods=["POST"])
# def ec2_instance_data():

#     key = request.form['instanceId']

#     dp_time_CU, dp_avg_CU = get_ec2_ins_metrics(type='CPUUtilization', ins_id=key)
#     dp_time_DRO, dp_avg_DRO = get_ec2_ins_metrics(type='DiskReadOps', ins_id=key)
#     dp_time_DWO, dp_avg_DWO = get_ec2_ins_metrics(type='DiskWriteOps', ins_id=key)
#     dp_time_NI, dp_avg_NI = get_ec2_ins_metrics(type='NetworkIn', ins_id=key)
#     dp_time_NO, dp_avg_NO = get_ec2_ins_metrics(type='NetworkOut', ins_id=key)
#     dp_time_CCU, dp_avg_CCU = get_ec2_ins_metrics(type='CPUCreditUsage', ins_id=key)
#     dp_time_CCB, dp_avg_CCB = get_ec2_ins_metrics(type='CPUCreditBalance', ins_id=key)
#     dp_time_DRB, dp_avg_DRB = get_ec2_ins_metrics(type='DiskReadBytes', ins_id=key)
#     dp_time_DWB, dp_avg_DWB = get_ec2_ins_metrics(type='DiskWriteBytes', ins_id=key)
#     dp_time_SCF, dp_avg_SCF = get_ec2_ins_metrics(type='StatusCheckFailed', ins_id=key)

#     response = ec2_client.describe_instances(
#         InstanceIds=[
#             key,
#         ],
#     )

#     # print(f'Instance {key} attributes:')

#     for reservation in response['Reservations']:
#         reservation
    
#     return render_template('aws/aws-ec2/aws_ec2_instance_data.html', 
#                             instance=reservation,
#                             dp_time_CU=dp_time_CU, dp_avg_CU=dp_avg_CU,
#                             dp_time_DRO=dp_time_DRO, dp_avg_DRO=dp_avg_DRO,
#                             dp_time_DWO=dp_time_DWO, dp_avg_DWO=dp_avg_DWO,
#                             dp_time_NI=dp_time_NI, dp_avg_NI=dp_avg_NI,
#                             dp_time_NO=dp_time_NO, dp_avg_NO=dp_avg_NO,
#                             dp_time_CCU=dp_time_CCU, dp_avg_CCU=dp_avg_CCU,
#                             dp_time_CCB=dp_time_CCB, dp_avg_CCB=dp_avg_CCB,
#                             dp_time_DRB=dp_time_DRB, dp_avg_DRB=dp_avg_DRB,
#                             dp_time_DWB=dp_time_DWB, dp_avg_DWB=dp_avg_DWB,
#                             dp_time_SCF=dp_time_SCF, dp_avg_SCF=dp_avg_SCF
#                             )
# #----------------------------------------------------------------------------------
# def get_ec2_ins_metrics(type, ins_id):

#     dps_avg = []
#     dps_time = []

#     dp = cw_client.get_metric_statistics(
#         Period=300,
#         StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
#         EndTime=datetime.datetime.utcnow(),
#         MetricName=type,
#         Namespace='AWS/EC2',
#         Statistics=['Average'],
#         Dimensions=[{'Name':'InstanceId', 'Value':ins_id}]
#         )
#     # print(dp)

#     datapoints = dp['Datapoints']     # CPU Utilization results                
#     sorted_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))

#     # print(sorted_datapoint)

#     for i in range(len(sorted_datapoint)):
#         sorted_datapoint[i]['sort_by'] = i

#     for dp in sorted_datapoint:
#         time = dp['Timestamp']
#         output_date = datetime.datetime.strftime(time, "%H:%M")

#         dps_avg.append(round(dp['Average'], 4))
#         dps_time.append(output_date)
    
#     dt = dps_time[-10:]
#     da = dps_avg[-10:]
#     # print(dt)
#     # print(da)

#     return json.dumps(dt), json.dumps(da)
# #-----------------------------------------------------------------------------------------
# def ec2_instance_metrics(type, ins_id):

#     if type == "CPUUtilization":
#         ins_met = {"metrics":[["AWS/EC2", "CPUUtilization", "InstanceId", str(ins_id)]]}  
#     if type == "DiskReadOps":
#         ins_met = {"metrics": [["AWS/EC2", "DiskReadOps", "InstanceId", str(ins_id)]]}
#     if type == "DiskWriteOps":
#         ins_met = {"metrics": [["AWS/EC2", "DiskWriteOps", "InstanceId", str(ins_id)]]}
#     if type == "NetworkIn":
#         ins_met = {"metrics": [["AWS/EC2", "NetworkIn", "InstanceId", str(ins_id)]]}
#     if type == "NetworkOut":
#         ins_met = {"metrics": [["AWS/EC2", "NetworkOut", "InstanceId", str(ins_id)]]}
#     if type == "CPUCreditUsage":
#         ins_met = {"metrics": [["AWS/EC2", "CPUCreditUsage", "InstanceId", str(ins_id)]]}
#     if type == "CPUCreditBalance":
#         ins_met = {"metrics": [["AWS/EC2", "CPUCreditBalance", "InstanceId", str(ins_id)]]}
#     if type == "DiskReadBytes":
#         ins_met = {"metrics": [["AWS/EC2", "DiskReadBytes", "InstanceId", str(ins_id)]]}
#     if type == "DiskWriteBytes":
#         ins_met = {"metrics": [["AWS/EC2", "DiskWriteBytes", "InstanceId", str(ins_id)]]}

#     response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(ins_met))
    
#     # print(response)

#     bytes_data=io.BytesIO(response["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())

#     # print(fr)
#     ec2_graph = fr.decode('utf-8')

#     return ec2_graph
    
# #---- AWS/EBS -----------------------------------------------------------------------------------------------#
# def aws_ebs_volumes():

#     ebs_vol = ec2_resource.volumes.all()

#     data = []
#     filter_data = []
#     vol_count = 0

#     ebs_status = ec2_client.describe_volumes(
#     Filters=[
#         {
#             'Name': 'status',
#             'Values': [
#                 'available',
#             ]
#         },
#     ],
    
#     )
#     unattached_count = (len(ebs_status))

#     # print(ebs_status)

#     for volume in ebs_vol:
#         print(volume.id)
#         vol_count += 1
#     # print(f'Count:',  vol_count)

#         data.append(["AWS/EBS", "VolumeReadBytes", "VolumeId", str(volume.id)])
#         filter_data={"metrics":data}

#         response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))

#         bytes_data=io.BytesIO(response["MetricWidgetImage"])
#         fr=base64.b64encode(bytes_data.getvalue())

#         # print(fr)
#         ebsGraph = fr.decode('utf-8')

#     return volume, vol_count, unattached_count, ebsGraph

# def get_ebs_graph(type):

#     data = []
#     filter_data = []

#     ebs_vol = ec2_resource.volumes.all()

#     for volume in ebs_vol:
#         # print(volume.id)

#         data.append(["AWS/EBS", str(type), "VolumeId", str(volume.id)])
#         filter_data={"metrics":data}

#         response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))

#         bytes_data=io.BytesIO(response["MetricWidgetImage"])
#         fr=base64.b64encode(bytes_data.getvalue())

#         ebsGraph = fr.decode('utf-8')
    
#     return ebsGraph


# #---- AWS/S3 ------------------------------------------------------------------------------------------------#

# @app.route('/aws/s3')
# def aws_s3():

#     response = s3_client.list_buckets()

#     size_count = s3_objects_size()

#     # dp_time_BSB, dp_avg_BSB = aws_get_s3_bucket_metrics("BucketSizeBytes", "project-test-bucket1", "StandardStorage" )
#     # dp_time_NOO, dp_avg_NOO = aws_get_s3_bucket_metrics("NumberOfObjects", "project-test-bucket1", "AllStorageTypes")

#     # dp_a_NOO = json.loads(dp_avg_NOO)
#     # dp_a_NOO = [round(x) for x in dp_a_NOO]
#     # dp_a_BSB = json.loads(dp_avg_BSB)

#     img_BSB = s3_graph("BucketSizeBytes")
#     img_NOO = s3_graph("NumberOfObjects")

#     if len(response['Buckets'])==0:
#         return f'No Buckets!'
#     # Output the bucket names
#     else:
#         print('Existing buckets:')
#         for bucket in response['Buckets']:
#             print(f'  {bucket["Name"]}')

#         return render_template("aws/aws-s3/aws_s3.html", 
#                 response=response, 
#                 size_count=size_count, 
#                 img_BSB=img_BSB,
#                 img_NOO=img_NOO,
#                 )

# #-------------------------------------------------------

# def aws_get_s3_bucket_size():

#     cw = boto3.client('cloudwatch')
#     s3client = boto3.client('s3')

#     allbuckets = s3client.list_buckets()

#     print('Bucket'.ljust(45) + 'Size in Bytes'.rjust(25))

#     # res = s3_client.put_bucket_metrics_configuration(
#     #     Bucket='project-test-bucket1',
#     #     Id='metrics-config-id',
#     #     MetricsConfiguration={
#     #         'Id': 'metrics-config-id',
#     #         'Filter': {
#     #             'Prefix': 'my-prefix',
#     #         }
#     #     }
#     # )

#     # print(f'PutMetrics: ',res)

#     for bucket in allbuckets['Buckets']:
    
#         response = cw.get_metric_statistics(Namespace='AWS/S3',
#                                             MetricName='BytesUploaded',
#                                             Dimensions=[{'Name': 'BucketName', 'Value': bucket['Name']}],
#                                             Statistics=['Average'],
#                                             Period=3600,
#                                             StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=7) ,
#                                             EndTime=datetime.datetime.utcnow(),
#                                             )

#         print(response)
#         for item in response["Datapoints"]:
#             print(bucket["Name"].ljust(45) + str("{:,}".format(int(item["Average"]))).rjust(25))

# # aws_get_s3_bucket_size()

# #-------------------------------------------------------
# def s3_objects_size():

#     data = []
#     size = 0
#     totalObject = 0

#     allbuckets = s3_client.list_buckets()

#     totalBucket = len(allbuckets['Buckets'])

#     for bucket in allbuckets['Buckets']:
#         bucket = s3_resource.Bucket(bucket["Name"])
#         for obj in bucket.objects.all():
#             totalObject += 1
#             size += obj.size

#     # print('total size:')
#     roundSize = ("%.3f GB" % (size*1.0/1024/1024/1024))
#     # print("%.3f GB" % (size*1.0/1024/1024/1024))
#     # print('total count:')
#     # print(totalCount)
#     print(f'Total Objects: ', totalObject)
#     data.append({'total_size': roundSize, 'total_bucket': totalBucket, 'total_object': totalObject })
#     return data

# #------------------------------------------------------
# def s3_graph(type):

#     start = datetime.datetime.utcnow() - datetime.timedelta(days=7)
#     end = datetime.datetime.utcnow() - datetime.timedelta(days=1)

#     data=[]
#     response_data=[]

#     allbuckets = s3_client.list_buckets()

#     for i in allbuckets['Buckets']:
#         response_data.append({
#             "BucketName": i['Name']
#         })
#     # print(f'Response Data: ', response_data)

#     bucket_names=[i["BucketName"] for i in response_data]
#     for bname in bucket_names:

#         if type == "BucketSizeBytes":
#             data.append(["AWS/S3", "BucketSizeBytes", "BucketName", str(bname), "StorageType", "StandardStorage"])
#             filter_data={"metrics":data,"start": str(start), "end": str(end),"title": "Bucket Size Bytes"}
#             # print(f'Filter Data: ', filter_data)
#         elif type == "NumberOfObjects":
#             data.append(["AWS/S3", "NumberOfObjects", "BucketName", str(bname), "StorageType", "AllStorageTypes"])
#             filter_data={"metrics":data, "start": str(start), "end": str(end),"title": "Number Of Objects"}
#             # print(f'Filter Data: ', filter_data)

#         response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
        
#         # print(response)

#         bytes_data=io.BytesIO(response["MetricWidgetImage"])
#         fr=base64.b64encode(bytes_data.getvalue())

#         # print(fr)
#         s3graph = fr.decode('utf-8')

#     return s3graph

# #-------------------------------------------------------
# @app.route('/s3-bucket-data', methods=["POST"])
# def s3_bucket_data():

#     key = request.form['bucketName']

#     # objects = s3_client.list_objects_v2(Bucket='project-test-bucket1')

#     # for obj in objects['Contents']:
#     #     print(obj)

#     dp_time_BSB, dp_avg_BSB = aws_get_s3_bucket_metrics("BucketSizeBytes", key, "StandardStorage", ['Average'])
#     dp_time_NOO, dp_avg_NOO = aws_get_s3_bucket_metrics("NumberOfObjects", key, "AllStorageTypes", ['Average'])


#     return render_template("aws/aws-s3/aws_s3_bucket_data.html",
#                             key=key,
#                             dp_time_BSB=dp_time_BSB, dp_avg_BSB=dp_avg_BSB,
#                             dp_time_NOO=dp_time_NOO, dp_avg_NOO=dp_avg_NOO)

# #-------------------------------------------------------
# def aws_get_s3_bucket_metrics(type, bname, sttype, stat):

#     dps_avg = []
#     dps_time = []
    
#     dp = cw_client.get_metric_statistics(
#             MetricName=type,
#             Namespace='AWS/S3',
#             Dimensions=[
#                 {
#                     'Name': 'BucketName',
#                     'Value': bname
#                 },
#                 {
#                     'Name': 'StorageType',
#                     'Value': sttype
#                 }
#             ],
#             Statistics=stat,
#             Period=86400,
#             StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=7) ,
#             EndTime=datetime.datetime.utcnow(),
        
#     )

#     datapoints = dp['Datapoints']                
#     sorted_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))

#     # print(sorted_datapoint)

#     for i in range(len(sorted_datapoint)):
#         sorted_datapoint[i]['sort_by'] = i

#     for dp in sorted_datapoint:
#         time = dp['Timestamp']
#         output_date = datetime.datetime.strftime(time, "%d/%m/%Y")

#         dps_avg.append(round(dp['Average'], 4))
#         dps_time.append(output_date)

#     dt = dps_time[-10:]
#     da = dps_avg[-10:]
#     # print(dt)
#     # print(da)

#     return json.dumps(dt), json.dumps(da)

# #---- AWS/RDS ------------------------------------------------------------------------------------------------#

# @app.route('/aws/rds')
# def aws_rds():

#     rds_CPUUtilization = get_rds_graph(type='CPUUtilization')
#     # rds_DatabaseConnections = get_rds_instancelevel_metrics(type='databaseConnections')    
#     rds_FreeStorageSpace = get_rds_graph(type='freeStorageSpace')    
#     rds_FreeableMemory = get_rds_graph(type='freeableMemory')    
#     rds_ReadIOPS = get_rds_graph(type='readIOPS')
#     rds_WriteIOPS = get_rds_graph(type='writeIOPS')    
#     rds_ReadThroughput = get_rds_graph(type='readThroughput')    
#     rds_WriteThroughput = get_rds_graph(type='writeThroughput')    
#     rds_ReadLatency = get_rds_graph(type='readLatency')     
#     rds_WriteLatency = get_rds_graph(type='writeLatency')    

#     rds_states = rds_state_stats()

#     response, rds_totalStorage, rds_insCnt = get_rds_instance_details()

#     return render_template('aws/aws-rds/aws_rds.html', 
#         response=response,
#         rds_CPUUtilization=rds_CPUUtilization,
#         # rds_DatabaseConnections=rds_DatabaseConnections,
#         rds_FreeStorageSpace=rds_FreeStorageSpace,
#         rds_FreeableMemory=rds_FreeableMemory,
#         rds_ReadIOPS=rds_ReadIOPS,
#         rds_WriteIOPS=rds_WriteIOPS,
#         rds_WriteThroughput=rds_WriteThroughput,
#         rds_ReadThroughput=rds_ReadThroughput,
#         rds_WriteLatency=rds_WriteLatency,
#         rds_ReadLatency=rds_ReadLatency,
#         rds_states=rds_states,
#         rds_insCnt=rds_insCnt,
#         rds_totalStorage=rds_totalStorage,
#         )
# #-------------------------------------------------------

# def get_rds_graph(type):
    
#     data=[]
#     response_data=[]
#     res = rds_client.describe_db_instances()

#     for i in res['DBInstances']:   
#             response_data.append({
#             "DBInstanceIdentifier": i['DBInstanceIdentifier']
#         })

#     # print(response_data)
  
#     instance_ids=[i["DBInstanceIdentifier"] for i in response_data]
#     for ins in instance_ids:

#         if type == 'CPUUtilization':
#             data.append(["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", str(ins)])
#             filter_data={"metrics":data}
#             print(filter_data)
#         elif type == 'freeStorageSpace':
#             data.append(["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", str(ins)])
#             filter_data={"metrics":data}
#         elif type == 'freeableMemory':
#             data.append(["AWS/RDS", "FreeableMemory", "DBInstanceIdentifier", str(ins)])
#             filter_data={"metrics":data}
#         elif type == 'readIOPS':
#             data.append(["AWS/RDS", "ReadIOPS", "DBInstanceIdentifier", str(ins)])
#             filter_data={"metrics":data}
#         elif type == 'writeIOPS':
#             data.append(["AWS/RDS", "WriteIOPS", "DBInstanceIdentifier", str(ins)])
#             filter_data={"metrics":data}
#         elif type == 'readThroughput':
#             data.append(["AWS/RDS", "ReadThroughput", "DBInstanceIdentifier", str(ins)])
#             filter_data={"metrics":data}
#         elif type == 'writeThroughput':
#             data.append(["AWS/RDS", "WriteThroughput", "DBInstanceIdentifier", str(ins)])
#             filter_data={"metrics":data}
#         elif type == 'readLatency':
#             data.append(["AWS/RDS", "ReadLatency", "DBInstanceIdentifier", str(ins)])
#             filter_data={"metrics":data}
#         elif type == 'writeLatency':
#             data.append(["AWS/RDS", "WriteLatency", "DBInstanceIdentifier", str(ins)])
#             filter_data={"metrics":data}


#         img = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
#         bytes_data=io.BytesIO(img["MetricWidgetImage"])
#         fr=base64.b64encode(bytes_data.getvalue())
        
#         rds_graph = fr.decode('utf-8')

#     return rds_graph

# #-------------------------------------------------------
# def get_rds_instance_details():

#     response_data=[]
#     total_storage = 0
#     ins_cnt = 0

#     response = rds_client.describe_db_instances()

#     for i in response['DBInstances']:   
#         try:
#             response_data.append({
#             "DBInstanceIdentifier": i['DBInstanceIdentifier'],
#             "DBInstanceClass":i["DBInstanceClass"],
#             "AllocatedStorage":i["AllocatedStorage"],
#             "Engine":i["Engine"],
#             "AvailabilityZone":i["AvailabilityZone"],
#             "DBInstanceArn":i["DBInstanceArn"],
#             "DBInstanceStatus":i["DBInstanceStatus"]
#         })
#             total_storage += (i["AllocatedStorage"])
#             ins_cnt += 1

#         except Exception as ex:
#             continue
#             pass
    
#     roundSize = ("%.3f TB" % (total_storage*1.0/1024))
#     # print(f'size: ', roundSize)
#     # print(f'instance count: ', ins_cnt)

#     # print(f'response data :',response_data)

#     return response, roundSize, ins_cnt
# #-------------------------------------------------------
# @app.route('/aws/rds-instance-data', methods=["POST"])
# def rds_instance_data():

#     key = request.form['dbInstanceId']

#     db_data = get_rds_db_data(key)

#     rds_t_CU, rds_a_CU = get_rds_ins_metrics("CPUUtilization", key)
#     rds_t_FSS, rds_a_FSS = get_rds_ins_metrics("FreeStorageSpace", key)
#     rds_t_FM, rds_a_FM = get_rds_ins_metrics("FreeableMemory", key)
#     rds_t_RIOPS, rds_a_RIOPS = get_rds_ins_metrics("ReadIOPS", key)
#     rds_t_WIOPS, rds_a_WIOPS = get_rds_ins_metrics("WriteIOPS", key)
#     rds_t_RT, rds_a_RT = get_rds_ins_metrics("ReadThroughput", key)
#     rds_t_WT, rds_a_WT = get_rds_ins_metrics("WriteThroughput", key)
#     rds_t_RL, rds_a_RL = get_rds_ins_metrics("ReadLatency", key)
#     rds_t_WL, rds_a_WL = get_rds_ins_metrics("WriteLatency", key)
#     rds_t_DBC, rds_a_DBC = get_rds_ins_metrics("DatabaseConnections", key)

#     return render_template('aws/aws-rds/aws_rds_instance_data.html', 
#                             key=key, db_data=db_data,
#                             rds_t_CU=rds_t_CU, rds_a_CU=rds_a_CU,
#                             rds_t_FSS=rds_t_FSS, rds_a_FSS=rds_a_FSS,
#                             rds_t_FM=rds_t_FM, rds_a_FM=rds_a_FM,
#                             rds_t_RIOPS=rds_t_RIOPS, rds_a_RIOPS=rds_a_RIOPS,
#                             rds_t_WIOPS=rds_t_WIOPS, rds_a_WIOPS=rds_a_WIOPS,
#                             rds_t_RT=rds_t_RT, rds_a_RT=rds_a_RT,
#                             rds_t_WT=rds_t_WT, rds_a_WT=rds_a_WT,
#                             rds_t_RL=rds_t_RL, rds_a_RL=rds_a_RL,
#                             rds_t_WL=rds_t_WL, rds_a_WL=rds_a_WL,
#                             rds_t_DBC=rds_t_DBC, rds_a_DBC=rds_a_DBC)

# #-------------------------------------------------------
# def get_rds_ins_metrics(type, ins_id):

#     dps_avg = []
#     dps_time = []

#     dp = cw_client.get_metric_statistics(
#         Period=300,
#         StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
#         EndTime=datetime.datetime.utcnow(),
#         MetricName=type,
#         Namespace='AWS/RDS',
#         Statistics=['Average'],
#         Dimensions=[{'Name':'DBInstanceIdentifier', 'Value':ins_id}]
#         )
#     # print(dp)

#     datapoints = dp['Datapoints']
#     sorted_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))

#     # print(sorted_datapoint)

#     for i in range(len(sorted_datapoint)):
#         sorted_datapoint[i]['sort_by'] = i

#     for dp in sorted_datapoint:
#         time = dp['Timestamp']
#         output_date = datetime.datetime.strftime(time, "%H:%M")

#         dps_avg.append(round(dp['Average'], 4))
#         dps_time.append(output_date)
    
#     dt = dps_time[-10:]
#     da = dps_avg[-10:]
#     # print(dt)
#     # print(da)

#     return json.dumps(dt), json.dumps(da)

# #------------------------------------------------------------------
# @app.route('/aws/rds-all-data')
# def get_rds_db_data(dbId):

#     response = rds_client.describe_db_instances(
#         DBInstanceIdentifier=dbId,
#     )

#     return response

# #------------------------------------------------------------------
# def get_rds_snapshots():
    
#     response_data = []
#     response = rds_client.describe_db_snapshots()
#     # DBInstanceIdentifier='database-instance-01'
#     # )
#     # print(response)
#     for i in response['DBSnapshots']:
#         try:
#             response_data.append({
#             "DBInstanceIdentifier": i['DBInstanceIdentifier'],
#         })
#         except Exception as ex:
#             continue
#             pass
#     return response

# #------------------------------------------------

# @app.route('/aws/rds/rds-instance-start', methods=["POST"])
# def rds_instance_start():
#     key = request.form['instance']

#     dbinstance = rds_client.start_db_instance(DBInstanceIdentifier=key)

#     print(f'Starting RDS instance: {dbinstance["DBInstance"]["DBInstanceIdentifier"]}')
    
#     # # instance.wait_until_running()

#     print(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been started')
#     flash(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been started')
#     return redirect(url_for('aws_rds'))

# #------------------------------------------------

# @app.route('/aws/rds/rds-instance-stop', methods=["POST"])
# def rds_instance_stop():
#     key = request.form['instance']

#     dbinstance = rds_client.stop_db_instance(DBInstanceIdentifier=key)
   
#     print(f'Stopping RDS instance: {dbinstance["DBInstance"]["DBInstanceIdentifier"]}')
    
#     # instance.wait_until_running()

#     print(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been stopped')
#     flash(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been stopped')

#     return redirect(url_for('aws_rds'))

# #---------------------------------------------------------------
# def rds_state_stats():

#     stats = {
#         "available": 0,
#         "starting": 0,
#         "stopping": 0,
#         "stopped": 0,
#         "backing-up": 0,
#         "creating": 0,
#         "deleting": 0,
#         "configuring-enhanced-monitoring": 0
#         }
    
#     paginator = rds_client.get_paginator('describe_db_instances')
#     response_iterator = paginator.paginate()
#     for ri in response_iterator:
#             for ins in ri['DBInstances']:
                    
#                     # print(ins)
#                     # print('##############################################')
#                     state = ins['DBInstanceStatus']
#                     stats[state] += 1
#     state_data=[]
#     for i in stats.keys():
#         state_data.append({"state":i,"value":int(stats[i])})

#     return state_data

# #-------AWS/CLOUDFRONT-------------------------------------------
# @app.route('/aws/cloudfront')
# def aws_cloudfront():

#     cf_dist = get_cloudfront_dist()
#     cf_REQ_graph = get_cloudfront_metrics("Requests")
#     cf_BD_graph = get_cloudfront_metrics("BytesDownloaded")
#     cf_BU_graph = get_cloudfront_metrics("BytesUploaded")
#     cf_4ER_graph = get_cloudfront_metrics("4xxErrorRate")
#     cf_5ER_graph = get_cloudfront_metrics("5xxErrorRate")
#     cf_TER_graph = get_cloudfront_metrics("TotalErrorRate")

#     return render_template('aws/aws-cloudfront/aws-cloudfront.html', 
#             cf_dist=cf_dist, 
#             cf_REQ_graph=cf_REQ_graph,
#             cf_BD_graph=cf_BD_graph,
#             cf_BU_graph=cf_BU_graph,
#             cf_4ER_graph=cf_4ER_graph,
#             cf_5ER_graph=cf_5ER_graph,
#             cf_TER_graph=cf_TER_graph)

# #----------------------------------------------------------------
# def get_cloudfront_dist():

#     response = cf_client.list_distributions().get("DistributionList")

#     return response

# #----------------------------------------------------------------
# def get_cloudfront_metrics(type):

#     data = []
#     filter_data = []
#     response_data = []
#     response = cf_client.list_distributions().get("DistributionList")

#     for i in response['Items']:   
#         response_data.append({
#         "DistIdentifier": i['Id']
#     })
  
#     instance_ids=[i["DistIdentifier"] for i in response_data]
#     for ins in instance_ids:

#         # print(f'Ids: ', ins)

#         data.append(["AWS/CloudFront", str(type), "DistributionId", str(ins), "Region", "Global"])
#         filter_data = {"metrics":data}

#         img = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))

#         bytes_data=io.BytesIO(img["MetricWidgetImage"])
#         fr=base64.b64encode(bytes_data.getvalue())

#         cf_graph = fr.decode('utf-8')

#     # dp = cw_client.get_metric_statistics(
#     #                             Namespace='AWS/CloudFront',
#     #                             MetricName='4xxErrorRate',
#     #                             Dimensions=[{'Name': 'DistributionId', 'Value': 'E2QSD328Y0MR1L', 'Name': 'Region', 'Value': 'Global'}],
#     #                             Statistics=['Average'],
#     #                             Unit='Percent',
#     #                             Period=86400,
#     #                             StartTime=datetime.datetime.utcnow() - datetime.timedelta(hours=12),
#     #                             EndTime=datetime.datetime.utcnow(),
#     #                             )

#     # print(f'cloudfront dp: ', dp)


#     return cf_graph

# @app.route('/aws/cloudfront-distribution', methods=["POST"])
# def get_cf_dist_data():

#     key = request.form['distributionId']

#     response = cf_client.get_distribution(Id=key).get("Distribution")
    
#     print(f'Response: ' ,response)

#     cf_REQ_graph = get_cf_dist_graph("Requests", key)
#     cf_BD_graph = get_cf_dist_graph("BytesDownloaded", key)
#     cf_BU_graph = get_cf_dist_graph("BytesUploaded", key)
#     cf_4ER_graph = get_cf_dist_graph("4xxErrorRate", key)
#     cf_5ER_graph = get_cf_dist_graph("5xxErrorRate", key)
#     cf_TER_graph = get_cf_dist_graph("TotalErrorRate", key)
#     cf_dist = get_cloudfront_dist()

#     return render_template('aws/aws-cloudfront/aws-cloudfront-dist-data.html', 
#                 key=key,
#                 response=response,
#                 cf_REQ_graph=cf_REQ_graph,
#                 cf_BD_graph=cf_BD_graph,
#                 cf_BU_graph=cf_BU_graph,
#                 cf_4ER_graph=cf_4ER_graph,
#                 cf_5ER_graph=cf_5ER_graph,
#                 cf_TER_graph=cf_TER_graph,
#                 cf_dist=cf_dist)

# def get_cf_dist_graph(type, distId):

#     data = []
#     filter_data = []

#     data.append(["AWS/CloudFront", str(type), "DistributionId", str(distId), "Region", "Global"])
#     filter_data = {"metrics":data}

#     img = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))

#     bytes_data=io.BytesIO(img["MetricWidgetImage"])
#     fr=base64.b64encode(bytes_data.getvalue())

#     cf_graph = fr.decode('utf-8')

#     return cf_graph

# #----------------------------------------------------------------
# @app.route('/aws/ebs-met')
# def get_ebs_metrics():

#     ebs_vol = ec2_client.describe_volumes()

#     dp = cw_client.get_metric_statistics(Namespace='AWS/EBS',
#                                     MetricName='VolumeReadBytes',
#                                     Dimensions=[{'Name': 'VolumeId', 'Value': 'vol-0b5363d3f9b960df6'}],
#                                     Statistics=['Average'],
#                                     Period=3600,
#                                     StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=7) ,
#                                     EndTime=datetime.datetime.utcnow(),
#                                     )

#     print(dp)

#     return ebs_vol

# #---- AWS/LAMBDA ------------------------------------------------------------------------------------------------#

# @app.route('/aws/lambda-instance-all')
# def lambda_instances():
#     lambda_client = boto3.client('lambda')
#     response = lambda_client.list_functions()
#     return response

# #---- AWS/ELASTIC LOAD BALANCER ------------------------------------------------------------------------------------------------#

# @app.route('/aws/elb-instance-all')
# def elb_instances():
#     elb_client = boto3.client('elb')
#     response = elb_client.describe_load_balancers()
#     return response

# #---- AWS/ELASTIC BEAN STALK ------------------------------------------------------------------------------------------------#

# @app.route('/aws/elasticbeanstalk-instance-all')
# def elasticbeanstalk_instances():
#     elasticbeanstalk_client = boto3.client('elasticbeanstalk')
#     response = elasticbeanstalk_client.describe_environments()
#     return response

# #---- AWS/ELASTIC CONTAINER SERVICE ------------------------------------------------------------------------------------------------#

# @app.route('/aws/ecs-instance-all')
# def ecs_instances():
#     ecs_client = boto3.client('ecs')
#     response = ecs_client.describe_clusters(
#         clusters=[
#             'string',
#         ]
#     )
#     return response

# #---- AWS/ELASTIC FILE SYSTEM ------------------------------------------------------------------------------------------------#

# @app.route('/aws/efs-instance-all')
# def efs_instances():
#     efs_client = boto3.client('efs')
#     response = efs_client.describe_file_systems(
#         MaxItems=123,
#         # Marker='string',
#         # CreationToken='string',
#         # FileSystemId='string'
#     )
#     return response

# #-----COSTS --------#
# def get_costs():
#     client = boto3.client('ce')

#     response = client.get_cost_and_usage(
#         TimePeriod={
#             'Start': '2023-01-08',
#             'End': '2023-01-09'
#         },
#         Metrics=['AmortizedCost'],
#         Granularity='DAILY',
  
#     )
#     from pprint import pprint
#     pprint(response)

# # get_costs()
# #-------------------------------------------------------------#
# def get_ec2_datapoints():

#     dps_avg = []
#     dps_time = []

#     dp = cw_client.get_metric_statistics(
#         Period=300,
#         StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
#         EndTime=datetime.datetime.utcnow(),
#         MetricName='CPUUtilization',
#         Namespace='AWS/EC2',
#         Statistics=['Average'],
#         Dimensions=[{'Name':'InstanceId', 'Value':'i-0e81bafe1ec8a68f8'}]
#         )
#     # print(dp)

#     datapoints = dp['Datapoints']               
#     sorted_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))

#     # print(sorted_datapoint)

#     for i in range(len(sorted_datapoint)):
#         sorted_datapoint[i]['sort_by'] = i

#     for dp in sorted_datapoint:
#         time = dp['Timestamp']
#         output_date = datetime.datetime.strftime(time, "%H:%M")

#         dps_avg.append(round(dp['Average'], 4))
#         dps_time.append(output_date)
#     # print(sorted_datapoint)
#     dt = dps_time[-10:]
#     da = dps_avg[-10:]
#     print(da)

#     return json.dumps(dt), json.dumps(da)
# #---------------------------------------------------------------------


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