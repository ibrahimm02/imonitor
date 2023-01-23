import os
from flask import Flask, Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash

from .utils.cloudfront.metrics import *

from .utils.ebs.graphs import *

from .utils.ec2.graphs import *
from .utils.ec2.metrics import *

from .utils.rds.graphs import *
from .utils.rds.metrics import *

from .utils.s3.graphs import *
from .utils.s3.metrics import *

#------------------------------------------------------------------

REGION_NAME = os.environ.get('REGION_NAME')

ec2_client = boto3.client("ec2", region_name=REGION_NAME)

ec2_resource = boto3.resource('ec2', region_name=REGION_NAME)

cw_client = boto3.client('cloudwatch', region_name=REGION_NAME)

current_region = ec2_client.meta.region_name

#------------------------------------------------------------------

aws_bp = Blueprint('aws_bp', __name__,
                    template_folder=os.path.join(os.getcwd(), 'iMonitor', 'aws', 'templates'),
                    static_folder='static', static_url_path='assets')

#-----------AWS OVERVIEW ------------------------------------------

@aws_bp.route('/overview')
def aws_overview():

    ec2_states = ec2_state_stats()

    response = ec2_client.describe_instances()

    ec2_CPUUtilization = get_ec2_CPUUtilization()
    ec2_CPUCreditUsage = get_ec2_CPUCreditUsage()

    s3_size_count = s3_objects_size()
    s3_graph_NOO = s3_graph("NumberOfObjects")

    rds_states = rds_state_stats()
    rds, rds_totalStorage, rds_insCnt = get_rds_instance_details()
    rds_CPUUtilization = get_rds_graph(type='CPUUtilization')  
    rds_FreeableMemory = get_rds_graph(type='freeableMemory') 

    cf_4ER_graph = get_cloudfront_metrics("4xxErrorRate")
    cf_5ER_graph = get_cloudfront_metrics("5xxErrorRate")

    ebs_volumes, ebs_vol_count, ebs_unattached_count, ebsGraph = aws_ebs_volumes()
    ebs_VRB_graph = get_ebs_graph("VolumeReadBytes")
    ebs_VWB_graph = get_ebs_graph("VolumeWriteBytes")

    if not(response):
        return render_template("message.html",message="No Instances running. Create an instance first")

    return render_template('overview.html', 
                            current_region=current_region, 
                            response=response,
                            ec2_states=ec2_states,
                            ec2_CPUUtilization=ec2_CPUUtilization,
                            ec2_CPUCreditUsage=ec2_CPUCreditUsage,
                            s3_size_count=s3_size_count,
                            s3_graph_NOO=s3_graph_NOO,
                            rds_states=rds_states,
                            rds_insCnt=rds_insCnt,
                            rds_totalStorage=rds_totalStorage,
                            rds_CPUUtilization=rds_CPUUtilization,
                            rds_FreeableMemory=rds_FreeableMemory,
                            cf_4ER_graph=cf_4ER_graph,
                            cf_5ER_graph=cf_5ER_graph,
                            ebs_volumes=ebs_volumes,
                            ebs_vol_count=ebs_vol_count,
                            ebs_unattached_count=ebs_unattached_count,
                            ebs_VRB_graph=ebs_VRB_graph,
                            ebs_VWB_graph=ebs_VWB_graph
                            )

#----------- ACCOUNT --------------------------------------------

@aws_bp.route('/account')
def aws_account():

    account_details = boto3.client("sts").get_caller_identity()
    return render_template('account.html', account_details=account_details)

#----------- AWS EC2 --------------------------------------------

@aws_bp.route('/ec2-instance-all')
def ec2_instances():
    response = ec2_client.describe_instances()

    if not(response):
        return render_template("message.html",message="No Instances running. Create an instance first")

    else:
        return response

#----------------------------------------------------------------

@aws_bp.route('/ec2')
def aws_ec2():

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

    avg_util, max_util, min_util = get_ec2_metrics_amm()

    ec2_states = ec2_state_stats()

    if not(instances):
        return render_template("aws-ec2/ec2.html", info="No instance Data")

    return render_template("aws-ec2/aws_ec2.html", 
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
        avg_util=avg_util, max_util=max_util, min_util=min_util,
        ec2_states=ec2_states,
        )

#-----------------------------------------------------------------

@aws_bp.route('/ec2-instance-start', methods=["POST"])
def ec2_instance_start():

    key = request.form['instance']
    
    try:
        instance = ec2_resource.Instance(key)
        instance.start()
        # print(f'Starting EC2 instance: {instance.id}')

        # # instance.wait_until_running()

        # print(f'EC2 instance "{instance.id}" has been started')
        flash(f'EC2 instance "{instance.id}" has been started')
    except:
        return False

    return redirect(url_for('aws_bp.aws_ec2'))

#-----------------------------------------------------------------

@aws_bp.route('/ec2-instance-stop', methods=["POST"])
def ec2_instance_stop():
    key = request.form['instance']

    try:
        instance = ec2_resource.Instance(key)
        instance.stop()
        # print(f'Stopping EC2 instance: {instance.id}')

        # instance.wait_until_stopped()

        # print(f'EC2 instance "{instance.id}" has been stopped')

        flash(f'EC2 instance "{instance.id}" has been stopped')
    except:
        return False

    return redirect(url_for('aws_bp.aws_ec2'))

#-----------------------------------------------------------------

@aws_bp.route('/ec2-instance-data', methods=["POST"])
def ec2_instance_data():

    key = request.form['instanceId']

    dp_time_CU, dp_avg_CU = get_ec2_ins_metrics(type='CPUUtilization', ins_id=key)
    dp_time_DRO, dp_avg_DRO = get_ec2_ins_metrics(type='DiskReadOps', ins_id=key)
    dp_time_DWO, dp_avg_DWO = get_ec2_ins_metrics(type='DiskWriteOps', ins_id=key)
    dp_time_NI, dp_avg_NI = get_ec2_ins_metrics(type='NetworkIn', ins_id=key)
    dp_time_NO, dp_avg_NO = get_ec2_ins_metrics(type='NetworkOut', ins_id=key)
    dp_time_CCU, dp_avg_CCU = get_ec2_ins_metrics(type='CPUCreditUsage', ins_id=key)
    dp_time_CCB, dp_avg_CCB = get_ec2_ins_metrics(type='CPUCreditBalance', ins_id=key)
    dp_time_DRB, dp_avg_DRB = get_ec2_ins_metrics(type='DiskReadBytes', ins_id=key)
    dp_time_DWB, dp_avg_DWB = get_ec2_ins_metrics(type='DiskWriteBytes', ins_id=key)
    dp_time_SCF, dp_avg_SCF = get_ec2_ins_metrics(type='StatusCheckFailed', ins_id=key)

    response = ec2_client.describe_instances(
        InstanceIds=[
            key,
        ],
    )

    # print(f'Instance {key} attributes:')

    for reservation in response['Reservations']:
        reservation
    
    return render_template('aws-ec2/aws_ec2_instance_data.html', 
                            instance=reservation,
                            dp_time_CU=dp_time_CU, dp_avg_CU=dp_avg_CU,
                            dp_time_DRO=dp_time_DRO, dp_avg_DRO=dp_avg_DRO,
                            dp_time_DWO=dp_time_DWO, dp_avg_DWO=dp_avg_DWO,
                            dp_time_NI=dp_time_NI, dp_avg_NI=dp_avg_NI,
                            dp_time_NO=dp_time_NO, dp_avg_NO=dp_avg_NO,
                            dp_time_CCU=dp_time_CCU, dp_avg_CCU=dp_avg_CCU,
                            dp_time_CCB=dp_time_CCB, dp_avg_CCB=dp_avg_CCB,
                            dp_time_DRB=dp_time_DRB, dp_avg_DRB=dp_avg_DRB,
                            dp_time_DWB=dp_time_DWB, dp_avg_DWB=dp_avg_DWB,
                            dp_time_SCF=dp_time_SCF, dp_avg_SCF=dp_avg_SCF
                            )

#----------- AWS S3 ---------------------------------------------

@aws_bp.route('/s3')
def aws_s3():

    response = s3_client.list_buckets()

    size_count = s3_objects_size()

    # dp_time_BSB, dp_avg_BSB = aws_get_s3_bucket_metrics("BucketSizeBytes", "project-test-bucket1", "StandardStorage" )
    # dp_time_NOO, dp_avg_NOO = aws_get_s3_bucket_metrics("NumberOfObjects", "project-test-bucket1", "AllStorageTypes")

    # dp_a_NOO = json.loads(dp_avg_NOO)
    # dp_a_NOO = [round(x) for x in dp_a_NOO]
    # dp_a_BSB = json.loads(dp_avg_BSB)

    img_BSB = s3_graph("BucketSizeBytes")
    img_NOO = s3_graph("NumberOfObjects")

    if len(response['Buckets'])==0:
        return f'No Buckets!'
    # Output the bucket names
    else:
        print('Existing buckets:')
        for bucket in response['Buckets']:
            print(f'  {bucket["Name"]}')

        return render_template("aws-s3/aws_s3.html", 
                response=response, 
                size_count=size_count, 
                img_BSB=img_BSB,
                img_NOO=img_NOO,
                )

#-----------------------------------------------------------------

@aws_bp.route('/s3-bucket-data', methods=["POST"])
def s3_bucket_data():

    key = request.form['bucketName']

    # objects = s3_client.list_objects_v2(Bucket='project-test-bucket1')

    # for obj in objects['Contents']:
    #     print(obj)

    dp_time_BSB, dp_avg_BSB = aws_get_s3_bucket_metrics("BucketSizeBytes", key, "StandardStorage", ['Average'])
    dp_time_NOO, dp_avg_NOO = aws_get_s3_bucket_metrics("NumberOfObjects", key, "AllStorageTypes", ['Average'])


    return render_template("aws-s3/aws_s3_bucket_data.html",
                            key=key,
                            dp_time_BSB=dp_time_BSB, dp_avg_BSB=dp_avg_BSB,
                            dp_time_NOO=dp_time_NOO, dp_avg_NOO=dp_avg_NOO)

#----------- AWS RDS ---------------------------------------------

@aws_bp.route('/rds')
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

    return render_template('aws-rds/aws_rds.html', 
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
        rds_totalStorage=rds_totalStorage,
        )

#-----------------------------------------------------------------

@aws_bp.route('rds-instance-data', methods=["POST"])
def rds_instance_data():

    key = request.form['dbInstanceId']

    db_data = get_rds_db_data(key)

    rds_t_CU, rds_a_CU = get_rds_ins_metrics("CPUUtilization", key)
    rds_t_FSS, rds_a_FSS = get_rds_ins_metrics("FreeStorageSpace", key)
    rds_t_FM, rds_a_FM = get_rds_ins_metrics("FreeableMemory", key)
    rds_t_RIOPS, rds_a_RIOPS = get_rds_ins_metrics("ReadIOPS", key)
    rds_t_WIOPS, rds_a_WIOPS = get_rds_ins_metrics("WriteIOPS", key)
    rds_t_RT, rds_a_RT = get_rds_ins_metrics("ReadThroughput", key)
    rds_t_WT, rds_a_WT = get_rds_ins_metrics("WriteThroughput", key)
    rds_t_RL, rds_a_RL = get_rds_ins_metrics("ReadLatency", key)
    rds_t_WL, rds_a_WL = get_rds_ins_metrics("WriteLatency", key)
    rds_t_DBC, rds_a_DBC = get_rds_ins_metrics("DatabaseConnections", key)

    return render_template('aws-rds/aws_rds_instance_data.html', 
                            key=key, db_data=db_data,
                            rds_t_CU=rds_t_CU, rds_a_CU=rds_a_CU,
                            rds_t_FSS=rds_t_FSS, rds_a_FSS=rds_a_FSS,
                            rds_t_FM=rds_t_FM, rds_a_FM=rds_a_FM,
                            rds_t_RIOPS=rds_t_RIOPS, rds_a_RIOPS=rds_a_RIOPS,
                            rds_t_WIOPS=rds_t_WIOPS, rds_a_WIOPS=rds_a_WIOPS,
                            rds_t_RT=rds_t_RT, rds_a_RT=rds_a_RT,
                            rds_t_WT=rds_t_WT, rds_a_WT=rds_a_WT,
                            rds_t_RL=rds_t_RL, rds_a_RL=rds_a_RL,
                            rds_t_WL=rds_t_WL, rds_a_WL=rds_a_WL,
                            rds_t_DBC=rds_t_DBC, rds_a_DBC=rds_a_DBC)

#-----------------------------------------------------------------

@aws_bp.route('rds-all-data')
def get_rds_db_data(dbId):

    response = rds_client.describe_db_instances(
        DBInstanceIdentifier=dbId,
    )

    return response

#-----------------------------------------------------------------

@aws_bp.route('/rds/rds-instance-start', methods=["POST"])
def rds_instance_start():
    key = request.form['instance']

    dbinstance = rds_client.start_db_instance(DBInstanceIdentifier=key)

    print(f'Starting RDS instance: {dbinstance["DBInstance"]["DBInstanceIdentifier"]}')
    
    # # instance.wait_until_running()

    print(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been started')
    flash(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been started')
    return redirect(url_for('aws_bp.aws_rds'))

#-----------------------------------------------------------------

@aws_bp.route('/rds/rds-instance-stop', methods=["POST"])
def rds_instance_stop():
    key = request.form['instance']

    dbinstance = rds_client.stop_db_instance(DBInstanceIdentifier=key)
   
    print(f'Stopping RDS instance: {dbinstance["DBInstance"]["DBInstanceIdentifier"]}')
    
    # instance.wait_until_running()

    print(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been stopped')
    flash(f'EC2 instance "{dbinstance["DBInstance"]["DBInstanceIdentifier"]}" has been stopped')

    return redirect(url_for('aws_bp.aws_rds'))

#----------- AWS CLOUDFRONT ----------------------------------------

@aws_bp.route('/cloudfront')
def aws_cloudfront():

    cf_dist = get_cloudfront_dist()
    cf_REQ_graph = get_cloudfront_metrics("Requests")
    cf_BD_graph = get_cloudfront_metrics("BytesDownloaded")
    cf_BU_graph = get_cloudfront_metrics("BytesUploaded")
    cf_4ER_graph = get_cloudfront_metrics("4xxErrorRate")
    cf_5ER_graph = get_cloudfront_metrics("5xxErrorRate")
    cf_TER_graph = get_cloudfront_metrics("TotalErrorRate")

    return render_template('aws-cloudfront/aws-cloudfront.html', 
            cf_dist=cf_dist, 
            cf_REQ_graph=cf_REQ_graph,
            cf_BD_graph=cf_BD_graph,
            cf_BU_graph=cf_BU_graph,
            cf_4ER_graph=cf_4ER_graph,
            cf_5ER_graph=cf_5ER_graph,
            cf_TER_graph=cf_TER_graph)

#-----------------------------------------------------------------

@aws_bp.route('/cloudfront-distribution', methods=["POST"])
def get_cf_dist_data():

    key = request.form['distributionId']

    response = cf_client.get_distribution(Id=key).get("Distribution")
    
    print(f'Response: ' ,response)

    cf_REQ_graph = get_cf_dist_graph("Requests", key)
    cf_BD_graph = get_cf_dist_graph("BytesDownloaded", key)
    cf_BU_graph = get_cf_dist_graph("BytesUploaded", key)
    cf_4ER_graph = get_cf_dist_graph("4xxErrorRate", key)
    cf_5ER_graph = get_cf_dist_graph("5xxErrorRate", key)
    cf_TER_graph = get_cf_dist_graph("TotalErrorRate", key)
    cf_dist = get_cloudfront_dist()

    return render_template('aws-cloudfront/aws-cloudfront-dist-data.html', 
                key=key,
                response=response,
                cf_REQ_graph=cf_REQ_graph,
                cf_BD_graph=cf_BD_graph,
                cf_BU_graph=cf_BU_graph,
                cf_4ER_graph=cf_4ER_graph,
                cf_5ER_graph=cf_5ER_graph,
                cf_TER_graph=cf_TER_graph,
                cf_dist=cf_dist)

#----------- AWS RDS ---------------------------------------------

@aws_bp.route('/ebs-met')
def get_ebs_metrics():

    ebs_vol = ec2_client.describe_volumes()

    dp = cw_client.get_metric_statistics(Namespace='AWS/EBS',
                                    MetricName='VolumeReadBytes',
                                    Dimensions=[{'Name': 'VolumeId', 'Value': 'vol-0b5363d3f9b960df6'}],
                                    Statistics=['Average'],
                                    Period=3600,
                                    StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=7) ,
                                    EndTime=datetime.datetime.utcnow(),
                                    )

    print(dp)

    return ebs_vol

#---- AWS/LAMBDA --------------------------------------------------

@aws_bp.route('/lambda-instance-all')
def lambda_instances():
    lambda_client = boto3.client('lambda')
    response = lambda_client.list_functions()
    return response

#---- AWS/ELASTIC LOAD BALANCER -----------------------------------

@aws_bp.route('/elb-instance-all')
def elb_instances():
    elb_client = boto3.client('elb')
    response = elb_client.describe_load_balancers()
    return response

#---- AWS/ELASTIC BEAN STALK --------------------------------------

@aws_bp.route('/elasticbeanstalk-instance-all')
def elasticbeanstalk_instances():
    elasticbeanstalk_client = boto3.client('elasticbeanstalk')
    response = elasticbeanstalk_client.describe_environments()
    return response

#---- AWS/ELASTIC CONTAINER SERVICE -------------------------------

@aws_bp.route('/ecs-instance-all')
def ecs_instances():
    ecs_client = boto3.client('ecs')
    response = ecs_client.describe_clusters(
        clusters=[
            'string',
        ]
    )
    return response

#---- AWS/ELASTIC FILE SYSTEM -------------------------------------

@aws_bp.route('/efs-instance-all')
def efs_instances():
    efs_client = boto3.client('efs')
    response = efs_client.describe_file_systems(
        MaxItems=123,
        # Marker='string',
        # CreationToken='string',
        # FileSystemId='string'
    )
    return response

