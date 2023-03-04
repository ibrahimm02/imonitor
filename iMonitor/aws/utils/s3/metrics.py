import boto3, datetime, os, json
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
s3_resource = session.resource('s3')


#--------------------------------------------------------------
def aws_get_s3_bucket_size():

    cw = boto3.client('cloudwatch')
    s3client = boto3.client('s3')

    allbuckets = s3client.list_buckets()

    print('Bucket'.ljust(45) + 'Size in Bytes'.rjust(25))

    # res = s3_client.put_bucket_metrics_configuration(
    #     Bucket='project-test-bucket1',
    #     Id='metrics-config-id',
    #     MetricsConfiguration={
    #         'Id': 'metrics-config-id',
    #         'Filter': {
    #             'Prefix': 'my-prefix',
    #         }
    #     }
    # )

    # print(f'PutMetrics: ',res)

    for bucket in allbuckets['Buckets']:
    
        response = cw.get_metric_statistics(Namespace='AWS/S3',
                                            MetricName='BytesUploaded',
                                            Dimensions=[{'Name': 'BucketName', 'Value': bucket['Name']}],
                                            Statistics=['Average'],
                                            Period=3600,
                                            StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=7) ,
                                            EndTime=datetime.datetime.utcnow(),
                                            )

        print(response)
        for item in response["Datapoints"]:
            print(bucket["Name"].ljust(45) + str("{:,}".format(int(item["Average"]))).rjust(25))

# aws_get_s3_bucket_size()

#--------------------------------------------------------------
def s3_objects_size():

    data = []
    size = 0
    totalObject = 0

    allbuckets = s3_client.list_buckets()

    totalBucket = len(allbuckets['Buckets'])

    for bucket in allbuckets['Buckets']:
        bucket = s3_resource.Bucket(bucket["Name"])
        for obj in bucket.objects.all():
            totalObject += 1
            size += obj.size

    # print('total size:')
    roundSize = ("%.3f GB" % (size*1.0/1024/1024/1024))
    # print("%.3f GB" % (size*1.0/1024/1024/1024))
    # print('total count:')
    # print(totalCount)
    print(f'Total Objects: ', totalObject)
    data.append({'total_size': roundSize, 'total_bucket': totalBucket, 'total_object': totalObject })
    return data

#--------------------------------------------------------------
def aws_get_s3_bucket_metrics(type, bname, sttype, stat):

    dps_avg = []
    dps_time = []
    
    dp = cw_client.get_metric_statistics(
            MetricName=type,
            Namespace='AWS/S3',
            Dimensions=[
                {
                    'Name': 'BucketName',
                    'Value': bname
                },
                {
                    'Name': 'StorageType',
                    'Value': sttype
                }
            ],
            Statistics=stat,
            Period=86400,
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=7) ,
            EndTime=datetime.datetime.utcnow(),
        
    )

    datapoints = dp['Datapoints']                
    sorted_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))

    # print(sorted_datapoint)

    for i in range(len(sorted_datapoint)):
        sorted_datapoint[i]['sort_by'] = i

    for dp in sorted_datapoint:
        time = dp['Timestamp']
        output_date = datetime.datetime.strftime(time, "%d/%m/%Y")

        dps_avg.append(round(dp['Average'], 4))
        dps_time.append(output_date)

    dt = dps_time[-10:]
    da = dps_avg[-10:]
    # print(dt)
    # print(da)

    return json.dumps(dt), json.dumps(da)



#--------------------------------------------------------------



#--------------------------------------------------------------



#--------------------------------------------------------------
