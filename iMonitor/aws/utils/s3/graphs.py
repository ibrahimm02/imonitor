import boto3
import datetime
import base64
import io
import os
import json
from operator import itemgetter

AWS_SERVER_ACCESS_KEY = os.environ.get('AWS_SERVER_ACCESS_KEY')
AWS_SERVER_SECRET_KEY = os.environ.get('AWS_SERVER_SECRET_KEY')
REGION_NAME = os.environ.get('REGION_NAME')

session = boto3.Session(
    aws_access_key_id=AWS_SERVER_ACCESS_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
)

s3_client = session.client('s3')
cw_client = session.client('cloudwatch',region_name=REGION_NAME)

def s3_graph(type):

    start = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    end = datetime.datetime.utcnow() - datetime.timedelta(days=1)

    data=[]
    response_data=[]

    allbuckets = s3_client.list_buckets()

    for i in allbuckets['Buckets']:
        response_data.append({
            "BucketName": i['Name']
        })
    # print(f'Response Data: ', response_data)

    bucket_names=[i["BucketName"] for i in response_data]
    for bname in bucket_names:

        if type == "BucketSizeBytes":
            data.append(["AWS/S3", "BucketSizeBytes", "BucketName", str(bname), "StorageType", "StandardStorage"])
            filter_data={"metrics":data,"start": str(start), "end": str(end),"title": "Bucket Size Bytes"}
            # print(f'Filter Data: ', filter_data)
        elif type == "NumberOfObjects":
            data.append(["AWS/S3", "NumberOfObjects", "BucketName", str(bname), "StorageType", "AllStorageTypes"])
            filter_data={"metrics":data, "start": str(start), "end": str(end),"title": "Number Of Objects"}
            # print(f'Filter Data: ', filter_data)

        response = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
        
        # print(response)

        bytes_data=io.BytesIO(response["MetricWidgetImage"])
        fr=base64.b64encode(bytes_data.getvalue())

        # print(fr)
        s3graph = fr.decode('utf-8')

    return s3graph