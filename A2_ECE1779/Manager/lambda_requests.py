import json,boto3,datetime

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')

def lambda_handler(event, context):
    # Lambda function to publish custom HTTP request metric

    # Create a dictionary with ip addresses of instances as the key
    # and the value being that instances id
    instance_ip_id = {}
    for i in ec2.instances.all():
        instance_ip_id[i.private_ip_address] = i.id

    # Easy testing to manually input a log
    if event.get('test', False):
    	logContent = event['log']
    # Grab the location of the logfile that triggered the lambda function
    # Get the log file and read it
    else:
	    bucket = event['Records'][0]['s3']['bucket']['name']
	    key = event['Records'][0]['s3']['object']['key']
	    response = s3.get_object(Bucket=bucket, Key=key)
	    logContent = response['Body'].read().decode('utf-8')


    # Loop through logfile and create a dictionary that will store all the
    # instances as keys, and then each intance has keys for every minute and
    # the value is the number of requests that instance got in that minute
    requests = {}
    for line in logContent.splitlines():
        line_contents = line.split(' ')

        dt = datetime.datetime.strptime(line_contents[0], '%Y-%m-%dT%H:%M:%S.%fZ')
        ip = line_contents[3].split(':')[0]
        i_id = instance_ip_id.get(line_contents[3].split(':')[0], None)

        dt = dt.replace(second=0,microsecond=0)

        if i_id:
            if i_id not in requests:
                requests[i_id] = {}
            if dt in requests[i_id]:
                requests[i_id][dt] += 1
            else:
                requests[i_id][dt] = 1

    # Use dictionary we just made to publish custom cloudwatch metric
    # group data points together to a limit of 20
    metric_data = []
    data_points = 0
    put_calls = 0
    for i_id in requests:
        for dt in requests[i_id]:
            data_points += 1
            metric_data.append(
                {
                    'MetricName': 'requests',
                    'Dimensions': [
                        {
                            'Name': 'InstanceId',
                            'Value': i_id
                        },
                    ],
                    'Timestamp': dt,
                    'Value': requests[i_id][dt],
                    'Unit': 'None'
                }
            )

            if len(metric_data) == 20:
                put_calls += 1
                response = cloudwatch.put_metric_data(
                    Namespace='ece1779/EC2',
                    MetricData=metric_data
                )
                metric_data[:] = []


    if len(metric_data) > 0:
        put_calls += 1
        response = cloudwatch.put_metric_data(
            Namespace='ece1779/EC2',
            MetricData=metric_data
        )

    return {
        'statusCode': 200,
        'body': json.dumps({'data_points':data_points,'put_metric_data_calls':put_calls})
    }
