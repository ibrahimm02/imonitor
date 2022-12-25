from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app, flash

from flask_bootstrap import Bootstrap
import boto3
from boto3 import Session
from flask_cors import CORS
from datetime import datetime, timedelta
from operator import itemgetter
import json
import base64
import io


ec2_client = boto3.client("ec2", region_name="us-east-1")

ec2_resource = boto3.resource('ec2', region_name="us-east-1")

cw_client = boto3.client('cloudwatch')

app = Flask(__name__)
Bootstrap(app)
CORS(app)
app.secret_key = 'flash-secret'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/members')
def members():
     return render_template('index.html', message="No Instances running. Create an instance first" )
    # return {"members": ["Member1", "Member2", "Member3"]}


@app.route('/aws/ec2-instance-all')
def ec2_instances():
    response = ec2_client.describe_instances()

    if not(response):
        return render_template("message.html",message="No Instances running. Create an instance first")

    else:
        return response

@app.route('/aws/ec2-instances')
def get_running_ec2_instances():
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

    active_instances =  get_active_instance_count()

    instances = ec2_resource.instances.all()

    total_instances = len([instance for instance in instances]); 

    ec2_graph = get_ec2_graph()

    ec2_metrics = ec2_metrics_amm()

    ec2_states = ec2_state_stats()
    # data = {'chart_data': ec2_states}
    

    if not(instances):
        return render_template("aws/aws/ec2.html", info="No instance Data")

    return render_template("aws/aws_ec2.html", instances=instances, active_instances=active_instances, 
            total_instances=total_instances, graphImage=ec2_graph, ec2_metrics=ec2_metrics, ec2_states=ec2_states)

@app.route('/aws/s3-instance-all')
def s3_instances():
    # Retrieve the list of existing buckets
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()

    if len(response['Buckets'])==0:
        return f'No Buckets!'
    # Output the bucket names
    else:
        print('Existing buckets:')
        for bucket in response['Buckets']:
            print(f'  {bucket["Name"]}')
        return render_template("aws/s3buckets.html", response=response)

@app.route('/aws/rds-instance-all')
def rds_instances():
    rds_client = boto3.client('rds')
    response = rds_client.describe_db_instances(
        # DBInstanceIdentifier='string',
        # Filters=[
        #     {
        #         'Name': 'string',
        #         'Values': [
        #             'string',
        #         ]
        #     },
        # ],
        # MaxRecords=123,
        # Marker='string'
    )
    return response

@app.route('/aws/lambda-instance-all')
def lambda_instances():
    lambda_client = boto3.client('lambda')
    response = lambda_client.list_functions()
    return response

@app.route('/aws/elb-instance-all')
def elb_instances():
    elb_client = boto3.client('elb')
    response = elb_client.describe_load_balancers()
    return response

@app.route('/aws/elasticbeanstalk-instance-all')
def elasticbeanstalk_instances():
    elasticbeanstalk_client = boto3.client('elasticbeanstalk')
    response = elasticbeanstalk_client.describe_environments()
    return response

@app.route('/aws/ecs-instance-all')
def ecs_instances():
    ecs_client = boto3.client('ecs')
    response = ecs_client.describe_clusters(
        clusters=[
            'string',
        ]
    )
    return response

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

# @app.route('/aws/rds-instance-all')
# def rds_instances():
#     rds_client = boto3.client('rds')
#     response = rds_client.describe_db_clusters(
#         DBClusterIdentifier='string',
#         Filters=[
#             {
#                 'Name': 'string',
#                 'Values': [
#                     'string',
#                 ]
#             },
#         ],
#         MaxRecords=123,
#         Marker='string',
#         IncludeShared=True|False
#     )
#     return response




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


def get_ec2_graph():
  
    cw_client = boto3.client('cloudwatch')

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
    
    ec2_graph1 = fr.decode('utf-8')

    return ec2_graph1

get_ec2_graph()

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
        graph_data.append({"key":i,"value":int(stats[i])})
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

            EC2CPUUtilization = cw_client.get_metric_statistics(
                Namespace = 'AWS/EC2',
                MetricName = 'CPUUtilization',
                StartTime=datetime.utcnow() - timedelta(days=2) ,
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
          #  return print(EC2CPUUtilization)
                
            datapoints = EC2CPUUtilization['Datapoints']     # CPU Utilization results                
            sorted_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))

            for i in range(len(sorted_datapoint)):
                sorted_datapoint[i]['sort_by'] = i

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
            
#------------------------------------------------------------------------------
# [{'AmiLaunchIndex': 0, 'ImageId': 'ami-064d05b4fe8515623', 'InstanceId': 'i-043567371c05991f9', 'InstanceType': 't1.micro', 'KeyName': 'ec2-key-pair', 'LaunchTime': datetime.datetime(2022, 12, 22, 16, 25, 14, tzinfo=tzutc()), 'Monitoring': {'State': 'disabled'}, 'Placement': {'AvailabilityZone': 'us-east-1b', 'GroupName': '', 'Tenancy': 'default'}, 'Platform': 'windows', 'PrivateDnsName': 'ip-172-31-21-12.ec2.internal', 'PrivateIpAddress': '172.31.21.12', 'ProductCodes': [], 'PublicDnsName': '', 'State': {'Code': 80, 'Name': 'stopped'}, 'StateTransitionReason': 'User initiated (2022-12-22 23:22:21 GMT)', 'SubnetId': 'subnet-0496468f4b393d676', 'VpcId': 'vpc-0e8dc4407141eb883', 'Architecture': 'x86_64', 'BlockDeviceMappings': [{'DeviceName': '/dev/sda1', 'Ebs': {'AttachTime': datetime.datetime(2022, 12, 4, 17, 49, 27, tzinfo=tzutc()), 'DeleteOnTermination': True, 'Status': 'attached', 'VolumeId': 'vol-0102a32c11923a8c1'}}], 'ClientToken': '6d251cb0-46ab-4e32-8b29-fa85f584488f', 'EbsOptimized': False, 'EnaSupport': True, 'Hypervisor': 'xen', 'NetworkInterfaces': [{'Attachment': {'AttachTime': datetime.datetime(2022, 12, 4, 17, 49, 26, tzinfo=tzutc()), 'AttachmentId': 'eni-attach-0b973f025345198c9', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached', 'NetworkCardIndex': 0}, 'Description': '', 'Groups': [{'GroupName': 'launch-wizard-2', 'GroupId': 'sg-08d4f8ebbd3bf8b10'}], 'Ipv6Addresses': [], 'MacAddress': '0a:fd:f4:be:f4:21', 'NetworkInterfaceId': 'eni-05fd1aeb96fc3be7e', 'OwnerId': '653628891621', 'PrivateDnsName': 'ip-172-31-21-12.ec2.internal', 'PrivateIpAddress': '172.31.21.12', 'PrivateIpAddresses': [{'Primary': True, 'PrivateDnsName': 'ip-172-31-21-12.ec2.internal', 'PrivateIpAddress': '172.31.21.12'}], 'SourceDestCheck': True, 'Status': 'in-use', 'SubnetId': 'subnet-0496468f4b393d676', 'VpcId': 'vpc-0e8dc4407141eb883', 'InterfaceType': 'interface'}], 'RootDeviceName': '/dev/sda1', 'RootDeviceType': 'ebs', 'SecurityGroups': [{'GroupName': 'launch-wizard-2', 'GroupId': 'sg-08d4f8ebbd3bf8b10'}], 'SourceDestCheck': True, 'StateReason': {'Code': 'Client.UserInitiatedShutdown', 'Message': 'Client.UserInitiatedShutdown: User initiated shutdown'}, 'Tags': [{'Key': 'Name', 'Value': 'test-instance2'}], 'VirtualizationType': 'hvm', 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 1}, 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'}, 'HibernationOptions': {'Configured': False}, 'MetadataOptions': {'State': 'applied', 'HttpTokens': 'optional', 'HttpPutResponseHopLimit': 1, 'HttpEndpoint': 'enabled', 'HttpProtocolIpv6': 'disabled', 'InstanceMetadataTags': 'disabled'}, 'EnclaveOptions': {'Enabled': False}, 'PlatformDetails': 'Windows', 'UsageOperation': 'RunInstances:0002', 'UsageOperationUpdateTime': datetime.datetime(2022, 12, 4, 17, 49, 26, tzinfo=tzutc()), 'PrivateDnsNameOptions': {'HostnameType': 'ip-name', 'EnableResourceNameDnsARecord': True, 'EnableResourceNameDnsAAAARecord': False}, 'MaintenanceOptions': {'AutoRecovery': 'default'}, 'mainState': {'selected_datapoints': [{'Timestamp': datetime.datetime(2022, 12, 22, 18, 22, tzinfo=tzutc()), 'Average': 0.7333448677986331, 'Minimum': 0.645161290322544, 'Maximum': 1.03448275862073, 'Unit': 'Percent', 'sort_by': 1}, {'Timestamp': datetime.datetime(2022, 12, 21, 18, 22, tzinfo=tzutc()), 'Average': 3.5355675644290567, 'Minimum': 0.645161290322544, 'Maximum': 51.8032786885246, 'Unit': 'Percent', 'sort_by': 0}], 'last_avg': 0.7333448677986331, 'last_min': 0.645161290322544, 'last_max': 1.03448275862073, 'avg_load': 0.007, 'last_time': '2022-12-22 18:22:00+00:00'}}]


#-----------------------------------------------------------------------------

#-------------------------------------------------------------------

@app.route('/start', methods=["POST"])
def start_instance():
    key = request.form['instance']

    instance = ec2_resource.Instance(key)
    instance.start()

    print(f'Starting EC2 instance: {instance.id}')
    
    # instance.wait_until_running()

    print(f'EC2 instance "{instance.id}" has been started')
    flash(f'EC2 instance "{instance.id}" has been started')
    return redirect(url_for('get_running_ec2_instances'))
#-------------------------------------------------------------------

@app.route('/stop', methods=["POST"])
def stop_instance():
    key = request.form['instance']

    instance = ec2_resource.Instance(key)
    instance.stop()

    print(f'Stopping EC2 instance: {instance.id}')
    
    # instance.wait_until_running()

    print(f'EC2 instance "{instance.id}" has been stopped')

    flash(f'EC2 instance "{instance.id}" has been stopped')
    return redirect(url_for('get_running_ec2_instances'))
#-------------------------------------------------------------------


@app.route('/aws/account')
def aws_account():
    return render_template('account.html')

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