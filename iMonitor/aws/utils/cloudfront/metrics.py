import boto3
import json
import base64
import io, os

AWS_SERVER_ACCESS_KEY = os.environ.get('AWS_SERVER_ACCESS_KEY')
AWS_SERVER_SECRET_KEY = os.environ.get('AWS_SERVER_SECRET_KEY')
REGION_NAME = os.environ.get('REGION_NAME')

session = boto3.Session(
    aws_access_key_id=AWS_SERVER_ACCESS_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
)

cw_client = session.client('cloudwatch', region_name=REGION_NAME)
cf_client = session.client('cloudfront')


def get_cloudfront_dist():

    response = cf_client.list_distributions().get("DistributionList")

    return response

#----------------------------------------------------------------

def get_cloudfront_metrics(type):

    data = []
    filter_data = []
    response_data = []
    response = cf_client.list_distributions().get("DistributionList")

    for i in response['Items']:   
        response_data.append({
        "DistIdentifier": i['Id']
    })
  
    instance_ids=[i["DistIdentifier"] for i in response_data]
    for ins in instance_ids:

        # print(f'Ids: ', ins)

        data.append(["AWS/CloudFront", str(type), "DistributionId", str(ins), "Region", "Global"])
        filter_data = {"metrics":data}

        img = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))

        bytes_data=io.BytesIO(img["MetricWidgetImage"])
        fr=base64.b64encode(bytes_data.getvalue())

        cf_graph = fr.decode('utf-8')

    # dp = cw_client.get_metric_statistics(
    #                             Namespace='AWS/CloudFront',
    #                             MetricName='4xxErrorRate',
    #                             Dimensions=[{'Name': 'DistributionId', 'Value': 'E2QSD328Y0MR1L', 'Name': 'Region', 'Value': 'Global'}],
    #                             Statistics=['Average'],
    #                             Unit='Percent',
    #                             Period=86400,
    #                             StartTime=datetime.datetime.utcnow() - datetime.timedelta(hours=12),
    #                             EndTime=datetime.datetime.utcnow(),
    #                             )

    # print(f'cloudfront dp: ', dp)


    return cf_graph

#----------------------------------------------------------------

def get_cf_dist_graph(type, distId):

    data = []
    filter_data = []

    data.append(["AWS/CloudFront", str(type), "DistributionId", str(distId), "Region", "Global"])
    filter_data = {"metrics":data}

    img = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))

    bytes_data=io.BytesIO(img["MetricWidgetImage"])
    fr=base64.b64encode(bytes_data.getvalue())

    cf_graph = fr.decode('utf-8')

    return cf_graph