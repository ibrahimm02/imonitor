
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

cw_client = session.client('cloudwatch',region_name=REGION_NAME)
rds_client = session.client("rds", region_name=REGION_NAME)


#--------------------------------------------------------------

def get_rds_graph(type):
    
    data=[]
    response_data=[]
    res = rds_client.describe_db_instances()

    for i in res['DBInstances']:   
            response_data.append({
            "DBInstanceIdentifier": i['DBInstanceIdentifier']
        })

    # print(response_data)
  
    instance_ids=[i["DBInstanceIdentifier"] for i in response_data]
    for ins in instance_ids:

        if type == 'CPUUtilization':
            data.append(["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
            print(filter_data)
        elif type == 'freeStorageSpace':
            data.append(["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'freeableMemory':
            data.append(["AWS/RDS", "FreeableMemory", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'readIOPS':
            data.append(["AWS/RDS", "ReadIOPS", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'writeIOPS':
            data.append(["AWS/RDS", "WriteIOPS", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'readThroughput':
            data.append(["AWS/RDS", "ReadThroughput", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'writeThroughput':
            data.append(["AWS/RDS", "WriteThroughput", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'readLatency':
            data.append(["AWS/RDS", "ReadLatency", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}
        elif type == 'writeLatency':
            data.append(["AWS/RDS", "WriteLatency", "DBInstanceIdentifier", str(ins)])
            filter_data={"metrics":data}


        img = cw_client.get_metric_widget_image(MetricWidget=json.dumps(filter_data))
        bytes_data=io.BytesIO(img["MetricWidgetImage"])
        fr=base64.b64encode(bytes_data.getvalue())
        
        rds_graph = fr.decode('utf-8')

    return rds_graph



