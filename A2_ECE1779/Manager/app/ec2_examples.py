from flask import render_template, redirect, url_for, request,flash
from flask_login import current_user, login_required, logout_user
from app import webapp ,db

import boto3
from app import Config
from datetime import datetime, timedelta
from operator import itemgetter
from app.forms import Max_Threshold, Min_Threshold, Add_Ratio, Red_Ratio
from app.models_man import AutoScale, User, Image



@webapp.teardown_appcontext  # inorder to close the db connection when the app context expires
def shutdown_session(exception):
    db.session.remove()



def register_inst_elb(ids):
    # funtion to register newly spun instances to ELB
    elb = boto3.client('elb')
    response = elb.register_instances_with_load_balancer(
        LoadBalancerName=webapp.config['ELB_NAME'],
        Instances=ids,)


def deregister_inst_elb(ids):
    # funtion to deregister  instances from ELB
    elb = boto3.client('elb')
    response = elb.deregister_instances_from_load_balancer(
        LoadBalancerName=webapp.config['ELB_NAME'],
        Instances=ids)

@webapp.route('/ec2_summary',methods=['GET'])
@login_required
# Display an HTML summary of all ec2 instances
def ec2_summary():
    ec2 = boto3.resource('ec2')
    client = boto3.client('cloudwatch')

    pids = AutoScale.query.filter_by(id_scaling=1).first()
    metric_name = 'CPUUtilization'

    ##    CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System


    namespace = 'AWS/EC2'
    statistic = 'Average'



    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'ImageId', 'Value': webapp.config['AMI_ID']}]
    )

    cpu_stats = []
    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))




    namespace = 'AWS/ELB'
    statistic = 'Sum'
    metric_name = 'RequestCount'



    http = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],

    )

    http_req_stats = []
    for point in http['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        http_req_stats.append([time,point['Sum']])

    http_req_stats = sorted(http_req_stats, key=itemgetter(0))


    namespace = 'AWS/ELB'
    statistic = 'Average'
    metric_name = 'HealthyHostCount'



    workers = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,
        Statistics=[statistic],
    )

    num_workers_stats = []
    for point in workers['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        num_workers_stats.append([time,point['Average']])

    num_workers_stats = sorted(num_workers_stats, key=itemgetter(0))




    ids = AutoScale.query.filter_by(id_scaling=1).first()
    auto = ids.auto_toggle


    return render_template("ec2_examples/summary.html",title="All EC2 Instances Summary",
                           cpu_stats=cpu_stats,
                           http_req_stats=http_req_stats,
                           num_workers_stats=num_workers_stats,
                           auto=auto,pids=pids)





@webapp.route('/ec2_examples',methods=['GET'])
@login_required
# Display an HTML list of all ec2 instances
def ec2_list():

    # create connection to ec2
    ec2 = boto3.resource('ec2')

    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running','pending','stopping','shutting down']},{'Name': 'image-id', 'Values': [webapp.config['AMI_ID']]}])
    ids = AutoScale.query.filter_by(id_scaling=1).first()
    auto = ids.auto_toggle
    return render_template("ec2_examples/list.html",title="EC2 Instances",instances=instances, auto=auto)


@webapp.route('/ec2_examples/<id>',methods=['GET'])
#Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    metric_name = 'CPUUtilization'


    namespace = 'AWS/EC2'
    statistic = 'Average'



    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName=metric_name,
        Namespace=namespace,  # Unit='Percent',
        Statistics=[statistic],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    cpu_stats = []


    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))



    statistic_http = 'Sum'

    http_req = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='requests',
        Namespace='ece1779/EC2',  # Unit='Percent',
        Statistics=[statistic_http],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )


    http_req_stats = []

    for point in http_req['Datapoints']:


        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        http_req_stats.append([time,point[statistic_http]])

        http_req_stats = sorted(http_req_stats, key=itemgetter(0))



    return render_template("ec2_examples/view.html",title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           http_req_stats =http_req_stats)



@webapp.route('/ec2_examples/create',methods=['POST'])
@login_required

# Creating a new EC2 instance
def ec2_create():

    ec2 = boto3.resource('ec2')

    ec2.create_instances(
        ImageId=webapp.config['AMI_ID'],
        MinCount=1,
        MaxCount=1,
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
        })
    instances = ec2.instances.filter(Filters=[{'Name': 'image-id', 'Values': [webapp.config['AMI_ID']]},
                                         {'Name': 'instance-state-name', 'Values': ['running', 'pending']}, ])
    ids = []
    for instance in instances:
        ids.append({'InstanceId': instance.id})
    register_inst_elb(ids)
    return redirect(url_for('ec2_list'))



@webapp.route('/ec2_examples/delete/<id>',methods=['POST'])
# Terminate a EC2 instance
def ec2_destroy(id):

    ec2 = boto3.resource('ec2')

    ec2.instances.filter(InstanceIds=[id]).terminate()

    ids = []
    ids.append({'InstanceId': id})

    deregister_inst_elb(ids)

    return redirect(url_for('ec2_list'))


@webapp.route('/max_threshold',methods=['POST', 'GET'])
@login_required
#Change maximum threshold in auto scaling policy
def max_threshold():


    form = Max_Threshold()
    form2 = Min_Threshold()
    form3 = Add_Ratio()
    form4 = Red_Ratio()
    pids = AutoScale.query.filter_by(id_scaling=1).first()


    if form.validate_on_submit():

        ids = AutoScale.query.filter_by(id_scaling=1).first()

        if form.max_thresh.data < ids.min_threshold:
            form.max_thresh.errors.append("Max Threshold Cannot be lower than Min Threshold ({})".format(ids.min_threshold))
            return render_template("ec2_examples/autosc.html",form=form, form2=form2, form3=form3, form4=form4,pids=pids)


        ids.max_threshold = form.max_thresh.data
        db.session.commit()
        flash('Max Threshold Updated')

    toggle = AutoScale.query.filter_by(id_scaling=1).first()
    auto = toggle.auto_toggle

    return render_template("ec2_examples/autosc.html",form=form, form2=form2, form3=form3, form4=form4,auto=auto, pids=pids)



@webapp.route('/min_threshold',methods=['POST', 'GET'])
@login_required
#Change minimum threshold in auto scaling policy
def min_threshold():

    form = Max_Threshold()
    form2 = Min_Threshold()
    form3 = Add_Ratio()
    form4 = Red_Ratio()
    pids = AutoScale.query.filter_by(id_scaling=1).first()

    if form2.validate_on_submit():
        ids = AutoScale.query.filter_by(id_scaling=1).first()

        if form2.min_thresh.data > ids.max_threshold:
            form2.min_thresh.errors.append("Min Threshold Cannot be greater than Max Threshold ({})".format(ids.max_threshold))
            return render_template("ec2_examples/autosc.html",form=form, form2=form2, form3=form3, form4=form4,pids=pids)

        ids.min_threshold = form2.min_thresh.data
        db.session.commit()
        flash('Min Threshold Updated')

    toggle = AutoScale.query.filter_by(id_scaling=1).first()
    auto = toggle.auto_toggle


    return render_template("ec2_examples/autosc.html",form=form, form2=form2, form3=form3, form4=form4,auto=auto, pids=pids)



@webapp.route('/add_ratio',methods=['POST', 'GET'])
@login_required
#Change addition ratio in auto scaling policy
def add_ratio():

    form = Max_Threshold()
    form2 = Min_Threshold()
    form3 = Add_Ratio()
    form4 = Red_Ratio()
    pids = AutoScale.query.filter_by(id_scaling=1).first()

    if form3.validate_on_submit():
        ids = AutoScale.query.filter_by(id_scaling=1).first()
        ids.add_ratio = form3.add_r.data
        db.session.commit()
        flash('Increase Ratio Updated')
        #return "Working"

    toggle = AutoScale.query.filter_by(id_scaling=1).first()
    auto = toggle.auto_toggle



    return render_template("ec2_examples/autosc.html",form=form, form2=form2, form3=form3, form4=form4,auto =auto, pids=pids)



@webapp.route('/red_ratio',methods=['POST', 'GET'])
@login_required
#Change reduction ratio in auto scaling policy
def red_ratio():

    form = Max_Threshold()
    form2 = Min_Threshold()
    form3 = Add_Ratio()
    form4 = Red_Ratio()
    pids = AutoScale.query.filter_by(id_scaling=1).first()
    if form4.validate_on_submit():


        ids = AutoScale.query.filter_by(id_scaling=1).first()
        ids.red_ratio = form4.red_r.data
        db.session.commit()
        flash('Decrease Ratio Updated')
    toggle = AutoScale.query.filter_by(id_scaling=1).first()
    auto = toggle.auto_toggle

    return render_template("ec2_examples/autosc.html",form=form, form2=form2, form3=form3, form4=form4,auto= auto, pids=pids)



@webapp.route('/auto_toggle',methods=['POST', 'GET'])
@login_required
# Switch between manual and auto scaling mode
def auto_toggle():
    ids = AutoScale.query.filter_by(id_scaling=1).first()

    print("current state ",ids.auto_toggle)

    if ids.auto_toggle == True:
        ids.auto_toggle = False
    else:
        ids.auto_toggle = True

    print("after change", ids.auto_toggle)

    db.session.commit()

    if ids.auto_toggle:

        flash('Auto Scaling Enabled')
    else:
        flash('Auto Scaling Disabled')

    ec2 = boto3.resource('ec2')
    #instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running','pending','stopping','shutting down']}])

    #return render_template("ec2_examples/list.html",title="EC2 Instances",instances=instances, auto=ids.auto_toggle)

    return redirect(url_for('ec2_list'))



@webapp.route('/endoftheworld',methods=['POST', 'GET'])
@login_required
def endoftheworld():

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(webapp.config['S3_BUCKET'])
    bucket.objects.all().delete()

    Image.query.delete()
    db.session.commit()


    User.query.filter(User.username != "admin").delete()
    db.session.commit()


    flash("All S3 Data and RDS data (except that of admin) deleted. Let's start over")


    return redirect(url_for('user_login'))


@webapp.route('/display',methods=['POST', 'GET'])
#Display the current auto scaling configuration policy
def disp():
    form = Max_Threshold()
    form2 = Min_Threshold()
    form3 = Add_Ratio()
    form4 = Red_Ratio()
    pids = AutoScale.query.filter_by(id_scaling=1).first()

    return render_template("ec2_examples/autosc.html",form=form, form2=form2, form3=form3, form4=form4, pids=pids)

