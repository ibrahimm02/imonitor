import boto3, os
import json
import base64
import io

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


