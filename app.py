from urllib import response
from flask import Flask, render_template, jsonify
from flask_bootstrap import Bootstrap
import boto3
from flask_cors import CORS
from datetime import datetime, timedelta

ec2_client = boto3.client("ec2", region_name="us-east-1")

ec2_resource = boto3.resource('ec2', region_name="us-east-1")

app = Flask(__name__)
Bootstrap(app)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


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

    if not(instances):
        return render_template("aws/aws/ec2.html", message="No instance Data")

    return render_template("aws/aws_ec2.html", instances=instances, active_instances=active_instances, total_instances=total_instances)

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
        print(f'  - Instance ID: {instance.id}')
        count += 1
    
    return count


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