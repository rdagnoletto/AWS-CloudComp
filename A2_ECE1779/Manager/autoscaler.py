import datetime
import time
import boto3

from app import webapp,db


from datetime import datetime, timedelta

from app.models_man import AutoScale



def register_inst_elb(ids):
    elb = boto3.client('elb')
    response = elb.register_instances_with_load_balancer(
        LoadBalancerName=webapp.config['ELB_NAME'],
        Instances=ids,)

    waiter = elb.get_waiter('instance_in_service')
    waiter.wait(LoadBalancerName=webapp.config['ELB_NAME'],Instances=ids)
    print(response)


def deregister_inst_elb(ids):
    elb = boto3.client('elb')
    response = elb.deregister_instances_from_load_balancer(
        LoadBalancerName=webapp.config['ELB_NAME'],
        Instances=ids)
    waiter = elb.get_waiter('instance_deregistered')
    waiter.wait(LoadBalancerName=webapp.config['ELB_NAME'],Instances=ids)
    print(response)

def spinup_instance(num_worker) :
    #  create the in
    ec2 = boto3.resource('ec2')
    ec2.create_instances(

        ImageId=webapp.config['AMI_ID'],
        MinCount=1,
        MaxCount=num_worker,
        KeyName=webapp.config['KEY_NAME'],
        SecurityGroups=[
            webapp.config['SEC_GRP'],
        ],
        SecurityGroupIds=[
            webapp.config['SEC_GRP_ID'],
        ],
        InstanceType=webapp.config['INST_TYPE'],
        Monitoring={
            'Enabled': True
        }
    )

    ids = []
    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [webapp.config['AMI_ID']]},
                                              {'Name': 'instance-state-name', 'Values': ['running', 'pending']} ])


    
    for instance in instances:
        print(instance.id)
        ids.append({'InstanceId': instance.id})

    register_inst_elb(ids)
    print("Instance addition success")




def spindown_instance(num_worker):

    ids = []
    ids2 = []

    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [webapp.config['AMI_ID']]},
                                              {'Name': 'instance-state-name', 'Values': ['running']}])

    print("shutdown instances :",instances)
    for idx,instance in enumerate(instances,1):
        ids.append(instance.id)
        ids2.append({'InstanceId': instance.id})
        if idx == num_worker:
            break

    ec2.instances.filter(InstanceIds=ids).terminate()

    deregister_inst_elb(ids2)

    print("Instance removal success")





while True:

    thresh = AutoScale.query.filter_by(id_scaling=1).first()
    if thresh == None:
        initial = AutoScale(id_scaling=1, max_threshold=80, min_threshold = 20,add_ratio=2,red_ratio=2 , auto_toggle=0)
        db.session.add(initial)
        db.session.commit()
        thresh = AutoScale.query.filter_by(id_scaling=1).first()


    print("maxthresh:",thresh.max_threshold)
    print("minthresh:",thresh.min_threshold)
    print("add_ratio:",thresh.add_ratio)
    print("red_ratio:",thresh.red_ratio)
    print("auto_toggle:",thresh.auto_toggle)

    max_threshold = thresh.max_threshold
    min_threshold = thresh.min_threshold

    increase_rate = thresh.add_ratio
    decrease_rate = thresh.red_ratio
    auto_toggle = thresh.auto_toggle


    if auto_toggle:
        # create connection to ec2
        print("Automatic scaling enabled ")
        ec2 = boto3.resource('ec2')

        instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running','pending']}
            ,{'Name': 'image-id', 'Values': [webapp.config['AMI_ID']]}])


        cpu_stats_1 = []
        ids = []

        for instance in instances:

            ids.append(instance.id)
            
            client = boto3.client('cloudwatch')

            # get cpu statistics in 1 minute(60s)

            cpu_1 = client.get_metric_statistics(
                Period=60,
                StartTime=datetime.utcnow() - timedelta(seconds=2 * 60),
                EndTime=datetime.utcnow() - timedelta(seconds=1 * 60),
                MetricName='CPUUtilization',
                Namespace='AWS/EC2',  # Unit='Percent',
                Statistics=['Average'],
                Dimensions=[{'Name': 'InstanceId',
                             'Value': instance.id}]
            )

            
            for point in cpu_1['Datapoints']:

                
                load = round(point['Average'], 2)
                cpu_stats_1.append(load)
               
        print("length of ids:::", len(ids))
        num_workers = len(cpu_stats_1)
        print("length of cpu_stats_1:::", num_workers)
        add_instance_num = 0 
        red_instance_num = 0 

        if num_workers != 0 :
            average_load = sum(cpu_stats_1)/num_workers
        else:
            average_load = 0 # need to check this out 

        print(cpu_stats_1)
        print("final avg load",average_load)
        print("num_workers" ,num_workers)

    ######################## Adding instances logic ######################

        if average_load > max_threshold: 
            add_instance_num = int(num_workers * increase_rate - num_workers)

            print("instances to be added",add_instance_num)

        if (add_instance_num + num_workers) > 10 or (len(ids) + add_instance_num) >10 :
            print("Too many to add:- I am not Google or Amazon")
            add_instance_num = min(max(0,(10 - num_workers)),(10-len(ids)))

        if add_instance_num >0:
            spinup_instance(add_instance_num)
            print("Adding {} Instances".format(add_instance_num))


    ######################## Removing  instances logic ######################    
        if average_load <= min_threshold:
            red_instance_num = int(num_workers - num_workers / decrease_rate )
            print("instance to be reduced", red_instance_num)
            if (num_workers-red_instance_num) <1:
                red_instance_num = num_workers - 1 

        if red_instance_num >0:
            spindown_instance(red_instance_num)
            print("after sanity check number to be reduced", red_instance_num)
    

    else:
        print("Manual mode")

    time.sleep(30)
    db.session.commit() ## to terminate session so that during next iteration we can get updated results


