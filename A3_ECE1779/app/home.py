from flask import render_template, redirect, url_for, request, flash, Response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from boto3.dynamodb.conditions import Key, Attr
from app import webapp, db #, dynamo
from app.models import User
from app.forms import SearchForm
import requests
import boto3
from boto3.dynamodb.conditions import Key
import json

#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


@webapp.route('/',methods=['GET'])
def home():
    form = SearchForm()

    return render_template("home/landing.html", title="Welcome", form=form)


@webapp.route('/search',methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search_term = form.search_term.data
        return redirect(url_for('gallery', search_term=search_term))

    return redirect(url_for('home'))



@webapp.route('/results/<search_term>',methods=['GET'])
def gallery(search_term):
    form = SearchForm()
    form.search_term.data = search_term
    search_term = search_term.lower()
    table = dynamodb.Table(webapp.config["DDB_ATTRIB_TBL_NAME"])

    user_table = dynamodb.Table(webapp.config["DDB_USER_TBL_NAME"])

    similarity_api = 'https://api.twinword.com/api/v6/text/similarity/'
    association_api = 'https://api.twinword.com/api/v4/word/associations/'
    headers = {"X-RapidAPI-Key": webapp.config['TWIN_API_KEY'],"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(association_api, headers=headers, data={"entry":search_term}).json()

    associations_scored = r.get('associations_scored',{})
    associations_scored[search_term] = 150.0
    associations = r.get('associations_array',[])
    associations.insert(0,search_term)
    associations = [a.lower() for a in associations]

    empty = True
    images = {}
    matches = set()
    row_dict = {}
    score_threshold = 0.1

    response = table.scan()
    rows = response.get('Items', [{}])
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        rows += response.get('Items', [])

    for row in rows:
        attr = row.get('attribute', None)
        if attr is not None:
            attr_set = set(attr.split(' '))
            attr_set.add(attr)
            attr_set = {a.lower() for a in attr_set}
            matches = matches.union(attr_set)
            for a in attr_set:
                row_dict[a] = row

    matches = matches.intersection(set(associations))

    for match in matches:
        for pic in row_dict.get(match, {}).get('im_path', []):
            empty = False
            path = pic.get('path','')
            username = pic.get('username','')
            match_score = float(associations_scored.get(match.lower(),0)/100)*float(pic.get('Confidence',0)/100)
            if match_score >= score_threshold and match_score >= images.get(path,[0])[0]:
                images[path] = (match_score, username)

    sorted_images = sorted(images.items(), key=lambda im: im[1][0], reverse=True)
    return render_template("home/results.html", images=sorted_images,s3_loc = webapp.config["S3_LOCATION_WATER"],form=form)


@webapp.route('/displaywm/<im_id>', defaults={'user_id': None}, methods=['GET'])
@webapp.route('/displaywm/<user_id>/<im_id>',methods=['GET'])
def displaywm(user_id, im_id):

    image_loc = webapp.config["S3_LOCATION_WATER"] + "w_"+ im_id

    email = None
    if user_id is not None:
        table = dynamodb.Table(webapp.config["DDB_USER_TBL_NAME"])
        response = table.get_item(Key = {'username' :user_id})
        email = response.get('Item',{}).get('email', None)


    return render_template("images/display.html",og=image_loc, email=email, title ="Display")




