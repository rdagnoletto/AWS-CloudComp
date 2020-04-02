    
from flask import render_template, redirect, url_for, request, flash, send_from_directory, abort, Response
#from wand.image import Image as wandImage
from flask_login import login_required, current_user
from flask_wtf.file import FileField, FileRequired, FileAllowed
from pathvalidate import sanitize_filename
import requests
from wand.image import Image
from random import randint


#### for TA Access###
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'jpe', 'svg', 'bmp', 'JPG'])
#### for TA Access###

import os
import boto3
import ntpath
import urllib

from app import webapp, image_uploadset, db
from app.models import User #, Image
from app.forms import ImageForm, SearchForm
#import cv2
from os import urandom
#from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

s3 = boto3.client("s3",
    aws_access_key_id=webapp.config['S3_KEY'],
    aws_secret_access_key=webapp.config['S3_SECRET'] )

# @webapp.teardown_appcontext  # inorder to close the db connection when the app context expires
# def shutdown_session(exception):
#     db.session.remove()



######################################DYNAMODB INITIALIZATION ###################

def create_dynamo_Attrib():

    table = dynamodb.create_table(
        TableName = webapp.config["DDB_ATTRIB_TBL_NAME"],
        KeySchema = [
                    {   'AttributeName': 'attribute',
                        'KeyType': 'HASH'  #Partition key
                    }
                    # ,
                    # {
                    #     'AttributeName': 'attrib_counter',
                    #     'KeyType': 'RANGE'  #sort key
                    # }
                    ],

        AttributeDefinitions=[ # define columns

                    {
                        'AttributeName': 'attribute',
                        'AttributeType': 'S'

                    }
                    #,
                    # {
                    #     'AttributeName': 'attrib_counter',
                    #     'AttributeType': 'N'
                    # }

                    ],
        ProvisionedThroughput={
                        'ReadCapacityUnits': 2,
                        'WriteCapacityUnits': 2
                    }
        )


# To wait till the db is created .
    client = boto3.client("dynamodb")

    #Wait for the table to exist before exiting
    print('Waiting for User', '...')
    waiter = client.get_waiter('table_exists')
    waiter.wait(TableName=webapp.config["DDB_ATTRIB_TBL_NAME"])
    print("Table created")
    return



def putItem_Attrib(attribute,attrib_counter=None,im_path = [] ):

    # helper function to add data to table

    table = dynamodb.Table(webapp.config["DDB_ATTRIB_TBL_NAME"])
    # table_exists = False


    # if table.creation_date_time != None:

    #     #print("table exists !! ",table.creation_date_time)
    #     table_exists = True
    # else:
    #     table_exists = False
    #     #print("table do not exist")
    #     #print("table:",table)

    # if not table_exists:
    #     create_dynamo_Attrib()

    response = table.put_item(
       Item={
            'attribute': attribute,
            'attrib_counter': attrib_counter,
            'im_path' : im_path,
        }
    )

    print("Item addition succeeded")

    return



#for creating the User Dynamodb for the first time
@webapp.route('/create_attrib_db')
def create_attrib_db():

    create_dynamo_Attrib()


    return "Data added"





#########################################################################



@webapp.route('/uploaded_images',methods=['GET', 'POST'])
@login_required
def images_view():
    form = SearchForm()
    empty = True
    if form.validate_on_submit():
        search_term = form.search_term.data.lower()
        table = dynamodb.Table(webapp.config["DDB_USER_TBL_NAME"])
        response = table.get_item(Key = {'username' :current_user.id})

        #print("user response",response)
        images = []
        similarity_api = 'https://api.twinword.com/api/v6/text/similarity/'
        association_api = 'https://api.twinword.com/api/v4/word/associations/'
        headers = {"X-RapidAPI-Key": webapp.config['TWIN_API_KEY'],"Content-Type": "application/x-www-form-urlencoded"}

        r = requests.post(association_api, headers=headers, data={"entry":search_term}).json()

        associations_scored = r.get('associations_scored',{})
        associations_scored[search_term] = 100.0
        associations = r.get('associations_array',[])
        associations.append(search_term)

        print(associations_scored)
        if 'Item' in response:

            #print("responses in upload images",response)

            if response['Item']['images'] != []:
                empty = False
                for item in response['Item']['images']:
                    labels = item.get('labels',[])
                    label_dict = {l['Name'].lower():int(l['Confidence']) for l in labels}
                    label_list = [l['Name'].lower() for l in labels ]

                    matches = list(set(associations) & set(label_list))

                    print("label dict",label_dict)

                    score_matches = {}
                    for match in matches:
                        score_matches[match] = (float(label_dict.get(match,0)/100))*(float(associations_scored.get(match,0))/100)


                    # score_matches = {}
                    # for label in label_list:
                    #     r = requests.post(similarity_api, headers=headers, data={"text1":search_term,'text2':label}).json()
                    #     print(r['similarity'])
                    #     score_matches[label] = float(r['similarity'])*(float(label_dict.get(label,0)/100))

                    top_match = max(score_matches, key=score_matches.get, default=None)
                    top_score = score_matches.get(top_match, 0)
                    if top_score > 0.2:
                        images.append({'path':item['path'],'score_matches':score_matches,'top_score':top_score,'top_match':top_match})

                images.sort(key=lambda i: i.get('top_score',0), reverse=True)

                #print("images path",images)

        return render_template("images/thumbnail.html", title="Image Gallery", images=images,s3_loc = webapp.config["S3_LOCATION_WATER"],form=form,empty=empty)



    table = dynamodb.Table(webapp.config["DDB_USER_TBL_NAME"])
    response = table.get_item(Key = {'username' :current_user.id})

    #print("user response",response)

    images = []

    if 'Item' in response:

        #print("responses in upload images",response)

        if response['Item']['images'] != []:
            empty = False
            for item in response['Item']['images']:
                images.append({'path':item['path']})
        #images = None

    # else:
    #     images = None


    return render_template("images/thumbnail.html", title="Image Gallery", images=images,s3_loc = webapp.config["S3_LOCATION"],form=form,empty=empty) # , instance_id = r.text)

    #return render_template("images/thumbnail.html", title="Image Gallery", images=images,s3_loc = webapp.config["S3_LOCATION"]) # , instance_id = r.text)

@webapp.route('/new_image',methods=['GET', 'POST'])
@login_required
def new_image():
    form = ImageForm()
    if form.validate_on_submit():
        # save original images

        rand_name = urandom(4).hex() +  form.image_file.data.filename
        real_name = ntpath.basename(image_uploadset.save(form.image_file.data,name=rand_name))
        original_path = '/tmp/'+real_name
        watermark_name = '/tmp/'+'w_'+real_name


        #Adding watermark . need to store the watermark image in s3 and read from there.
        with Image(filename=original_path) as background:
              with Image(filename='cpics.png') as watermark:
                background.watermark(image=watermark, transparency=0.50, left = randint(1,100), top = randint(1,100))
              background.save(filename=watermark_name)


        try:

            s3.upload_file(original_path,webapp.config["S3_BUCKET"],real_name)
            s3.upload_file(watermark_name,webapp.config["S3_BUCKET_WATER"],'w_'+real_name)

            os.remove(original_path)
            os.remove(watermark_name)

            table_user = dynamodb.Table(webapp.config["DDB_USER_TBL_NAME"])
            table_attrib = dynamodb.Table(webapp.config["DDB_ATTRIB_TBL_NAME"])
            # rekognition on images
            rekognition = boto3.client('rekognition')

            response_label = rekognition.detect_labels(Image={"S3Object": {"Bucket": webapp.config["S3_BUCKET"], "Name": real_name}}, MaxLabels=10,
                                                 MinConfidence=70)

            response_faces = rekognition.recognize_celebrities(Image={"S3Object": {"Bucket": webapp.config["S3_BUCKET"], "Name": real_name}})

            #print("rekognition response", response)

            # labels = [{'Confidence': Decimal(str(round(label_prediction['Confidence'], 1))),
            #            'Name': label_prediction['Name']} for label_prediction in response['Labels']]




            labels = [{'Confidence': int(label_prediction['Confidence']),'Name': label_prediction['Name'].lower()} for label_prediction in response_label['Labels'] ]

            if response_faces['CelebrityFaces'] != []:

                labels.extend( [{'Confidence': int(face_prediction['MatchConfidence']),'Name': face_prediction['Name'].lower()} for face_prediction in response_faces['CelebrityFaces'] ] )

            #print("labels:::::", labels)


            # update table
            response_user = table_user.get_item(
                        Key={
                            'username': current_user.id,
                        }
                    )
            #print("response 1  ",response1)


            response_attrib = table_attrib.scan()

            records = []

            for i in response_attrib['Items']:
                records.append(i)

            while 'LastEvaluatedKey' in response_attrib:
                response_attrib = table.scan(
                    IndexName=indexName,
                    ExclusiveStartKey=response['LastEvaluatedKey']
                    )

                for i in response_attrib['Items']:
                    records.append(i)




            #print("response_attrib",response_attrib)




            attrib_list = {}
            for item in records:

                attrib_list[(item['attribute'])] = int(item['attrib_counter'])



            for label in labels:

                if label['Name'] in attrib_list.keys():
                    attrib_list[label['Name']] += int(1)


                    table_attrib.update_item(
                        Key={
                            'attribute': label['Name']
                            #,
                            # 'attrib_counter': attrib_list[label['Name']]

                        },
                        UpdateExpression="SET attrib_counter = :val, im_path = list_append(im_path, :val2)",

                        ExpressionAttributeValues={
                            ':val': attrib_list[label['Name']],
                            # ':val2': [real_name] },
                            ':val2': [{
                                'username':current_user.id,
                                'email':response_user['Item']['email'],
                                'path': real_name,
                                'Confidence': label['Confidence'],
                                        }]
                                },

                        ReturnValues="UPDATED_NEW"
                        )

                else:
                    putItem_Attrib(label['Name'],int(1),[{
                                'username':current_user.id,
                                'email':response_user['Item']['email'],
                                'path': real_name,
                                'Confidence': label['Confidence']}])



            # for label in labels:
            #     if label['Name'] in attrib_list:
            #         attrib_list[label['Name']] += int(1)
            #     else:
            #         attrib_list[label['Name']] = int(1)

            # print("attrib list",attrib_list)


            table_user.update_item(
                Key={
                    'username': current_user.id,
                },
                UpdateExpression="SET images = list_append(images, :val)",
                ExpressionAttributeValues={
                    ':val': [{
                        'path': real_name,
                        'labels': labels,
                    }],
                },
                ReturnValues="UPDATED_NEW"
            )




            # table.update_item(
            #     Key={
            #         'username': current_user.id,
            #     },
            #     UpdateExpression="SET images = list_append(images, :val), attrib = :val2",
            #     ExpressionAttributeValues={
            #         ':val': [{
            #             'path': real_name,
            #             'labels': labels,
            #         }],
            #         ':val2': attrib_list,
            #     },
            #     ReturnValues="UPDATED_NEW"
            # )




            #print("labels",labels)



            flash('File Uploaded!')



        except Exception as error:
#            db.session.rollback()
            abort(500, error)


    return render_template("images/new.html", title="Upload an Image", form=form)

#<int:id>

@webapp.route('/display/<path:id>',methods=['GET'])
@login_required
def display(id):
    #print("id is", id)

    # Display original and image with face detection side by side

    image_loc = webapp.config["S3_LOCATION"]+id


    table = dynamodb.Table(webapp.config["DDB_USER_TBL_NAME"])
    response = table.get_item(Key = {'username' :current_user.id})


    # attributes dont show up on page because text is white, fix this
    attributes = []

    belongs = False
    if 'Item' in response:
        if response['Item']['images'] != []:
            for item in response['Item']['images']:
                if item.get('path') == id:
                    print("ID found ")
                    belongs = True
                    for attr in item.get('labels',[]):
                        attributes.append(attr['Name'])

    if belongs:
        return render_template("images/display.html",og=image_loc, title ="Display" , attributes = attributes, id=id )
    else:
        return redirect(url_for('displaywm', id=id))




@webapp.route('/superres/<path:id>',methods=['GET'])
@login_required
def superres(id):

    # Send the image to Super Resolution API and get the result

    image_loc = webapp.config["S3_LOCATION"]+id


    headers={'api-key': webapp.config['DEEPAI_API_KEY']}

    r = requests.post(
        "https://api.deepai.org/api/waifu2x",
        data={
            'image': image_loc,
        },
        headers=headers
    )

    output = r.json().get('output_url',None)



    # if belongs:
    return render_template("images/displayedited.html",edited=output, title ="Display", og=image_loc,id=id )


    # else:
    #     return redirect(url_for('displaywm', id=id))







@webapp.route('/replace/<path:id>/<path:edited>',methods=['GET'])
@login_required
def replace(id,edited):
    s3_r = boto3.resource('s3')

    edited_im =requests.get(edited, stream = True)
    file_object_from_req = edited_im.raw
    req_data = file_object_from_req.read()

    bucket = s3_r.Bucket(webapp.config['S3_BUCKET'])

    bucket.delete_objects(Delete={
                                    'Objects': [
                                        {
                                            'Key': id,
                                        },
                                    ],
                                    'Quiet': True
                                },)

    bucket.put_object(Key= id , Body = req_data)


    
    return redirect(url_for('display',id=id))
    #return render_template("images/display.html",og=edited, title ="Display" )








@webapp.route('/delete/<path:id>',methods=['GET'])
@login_required
def delete(id):
    s3_r = boto3.resource('s3')

    bucket = s3_r.Bucket(webapp.config['S3_BUCKET'])
    
    bucket.delete_objects(Delete={
                                    'Objects': [
                                        {
                                            'Key': id,
                                        },
                                    ],
                                    'Quiet': True
                                },)

    bucket.delete_objects(Delete={
                                'Objects': [
                                    {
                                        'Key': 'w_'+id,
                                    },
                                ],
                                'Quiet': True
                            },)


    table_user = dynamodb.Table(webapp.config["DDB_USER_TBL_NAME"])
    table_attrib = dynamodb.Table(webapp.config["DDB_ATTRIB_TBL_NAME"])

    
    response = table_user.get_item(Key = {'username' :current_user.id})
    image_list = response.get('Item').get('images')

    print("old len", len(image_list))

    for ind , im in enumerate(image_list):
        print(im.get('path'))
        if im.get('path') ==id:
            lab = im.get('labels')
            del(image_list[ind])


    print("new im list",image_list)

    table_user.update_item(
                    Key={
                        'username': current_user.id,
                    },
                    UpdateExpression="SET images = :val",
                    ExpressionAttributeValues={
                        ':val': image_list
                    },
                    ReturnValues="UPDATED_NEW"
                )

    response_attrib = table_attrib.scan()


    attrib_list = {}
    for item in response_attrib['Items']:

        attrib_list[(item['attribute'])] = int(item['attrib_counter'])


    for label in lab:
        print(label.get("Name"))
        if label.get("Name") in attrib_list.keys():
            
            res = table_attrib.get_item(Key = {'attribute' :label['Name']})
            print(res.get('Item').get('im_path'))

            #print(res.get('Item').get('attrib_counter'))
            if res.get('Item').get('attrib_counter') == 1 :
                table_attrib.delete_item(Key={
                 'attribute' :label['Name']},)
                print("deleted")
            else:
                print(res.get('Item'))
                attrib_list[label['Name']] -= int(1)
                path_list = res.get('Item').get('im_path')

                for ind, impath in enumerate(path_list):
                    if impath.get('path') == id:
                        del(path_list[ind])


                table_attrib.update_item(
                Key={
                    'attribute': label['Name']
                    #,
                    # 'attrib_counter': attrib_list[label['Name']]

                },
                UpdateExpression="SET attrib_counter = :val, im_path = :val2",

                ExpressionAttributeValues={
                    ':val': attrib_list[label['Name']],
                    ':val2': path_list
                        },

                ReturnValues="UPDATED_NEW"
                )

    return redirect(url_for('images_view'))






# for Zappa
if __name__ == '__main__':
    webapp.run()


