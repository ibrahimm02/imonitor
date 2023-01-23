import boto3, os, base64, io, json

REGION_NAME = os.environ.get('REGION_NAME')
print(REGION_NAME)
REGION_NAME = 'us-east-1'
ec2_client = boto3.client("ec2", region_name=REGION_NAME)
ec2_resource = boto3.resource('ec2', region_name=REGION_NAME)

cw_client = boto3.client('cloudwatch', region_name=REGION_NAME)

def aws_ebs_volumes():

    ebs_vol = ec2_resource.volumes.all()

    data = []
    filter_data = []
    vol_count = 0

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
        print(volume.id)
        vol_count += 1
    # print(f'Count:',  vol_count)

        data.append(["AWS/EBS", "VolumeReadBytes", "VolumeId", str(volume.id)])
        filter_data={"metrics":data}

        response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))

        bytes_data=io.BytesIO(response["MetricWidgetImage"])
        fr=base64.b64encode(bytes_data.getvalue())

        # print(fr)
        ebsGraph = fr.decode('utf-8')

    return volume, vol_count, unattached_count, ebsGraph

#---------------------------------------------------------------------

def get_ebs_graph(type):

    data = []
    filter_data = []

    ebs_vol = ec2_resource.volumes.all()

    for volume in ebs_vol:
        # print(volume.id)

        data.append(["AWS/EBS", str(type), "VolumeId", str(volume.id)])
        filter_data={"metrics":data}

        response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))

        bytes_data=io.BytesIO(response["MetricWidgetImage"])
        fr=base64.b64encode(bytes_data.getvalue())

        ebsGraph = fr.decode('utf-8')
    
    return ebsGraph
