from urllib import response
from flask import Flask, render_template, jsonify
from flask_bootstrap import Bootstrap
import boto3

ec2_client = boto3.client("ec2", region_name="us-east-1")

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aws/ec2-instance-all')
def ec2_instances():
    response = ec2_client.describe_instances()
    return response

@app.route('/aws/s3-instance-all')
def s3_instances():
    # Retrieve the list of existing buckets
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()

    # Output the bucket names
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')
    return response

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


if __name__ == "__main__":
    app.run(debug=True)