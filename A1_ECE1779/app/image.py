
from flask import render_template,redirect,url_for,request,g,flash,send_from_directory,abort
from wand.image import Image as wandImage
from flask_login import login_required, current_user
from flask_wtf.file import FileField, FileRequired, FileAllowed
from pathvalidate import sanitize_filename

#### for TA Access###
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
#### for TA Access###

import os
import boto3
import ntpath
import urllib

from app import webapp, image_uploadset, db
from app.models import User, Image
from app.forms import ImageForm
import cv2


@webapp.teardown_appcontext  # inorder to close the db connection when the app context expires
def shutdown_session(exception):
    db.session.remove()





@webapp.route('/uploads/<folder>/<image_name>')
def download_file(folder, image_name):

    upload_dir = os.path.join(os.getcwd(), webapp.config['UPLOADED_IMAGES_DEST'],folder)
    filename = image_name
    return send_from_directory(upload_dir, filename, as_attachment=True)

@webapp.route('/uploaded_images',methods=['GET'])
@login_required
def images_view():
    images = Image.query.filter_by(user_id=current_user.id).all()
    return render_template("images/thumbnail.html", title="Image Gallery", images=images)

@webapp.route('/new_image',methods=['GET', 'POST'])
@login_required
def new_image():
    form = ImageForm()
    if form.validate_on_submit():
        # save original image
        real_name = ntpath.basename(image_uploadset.save(form.image_file.data, folder='originals', name=form.image_file.data.filename))

        original_path = './images/originals/'+real_name
        image_cv = cv2.imread(original_path)


        # Face detection
        ## need to tell the location of the classifier manually!!
        # face_cascade = cv2.CascadeClassifier('C:/Users/mihir/PycharmProjects/A1_ECE1779/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml')
        #face_cascade = cv2.CascadeClassifier('/Users/ragnoletto/Documents/School/UofT/ECE1779/assignments/A1_ECE1779/venv/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml')
        #face_cascade = cv2.CascadeClassifier('/Users/bibinsebastian/Dropbox/UofT/ECE1779/A1_ECE1779/venv/lib/python3.6/site-packages/cv2/data/haarcascade_frontalface_default.xml')
        face_cascade = cv2.CascadeClassifier('./venv/lib/python3.5/site-packages/cv2/data/haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        face_cv = image_cv.copy() #this is neeeded since it will throw error if there is no image in the picture

        for (x,y,w,h) in faces:
            face_cv = cv2.rectangle(image_cv, (x,y) , (x + w,y + h), (0,0,255),8)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = face_cv[y:y+h, x:x+w]


        picture_path = './images/faces/'+real_name
        cv2.imwrite(picture_path, face_cv)
        cv2.waitKey(0)

        try:
            image = Image(user_id=current_user.id, file_name=real_name, num_faces = len(faces))
            db.session.add(image)
            db.session.commit()
            flash('File Uploaded!')
        except Exception as error:
            db.session.rollback()
            abort(500, error)
        finally:
            db.session.close()



    return render_template("images/new.html", title="Upload an Image", form=form)



@webapp.route('/face_detection/<int:id>',methods=['GET'])
@login_required
def face_detect(id):

    # Display original and image with face detection side by side
    try:
        image = Image.query.filter_by(id=id).one()
    except MultipleResultsFound:
        # Should never be here since id is the primary key there will only be one.
        print(MultipleResultsFound)
        flash("Image %d was stored incorrectly." % id)
        return redirect(url_for('main'))
    except NoResultFound:
        # If someone trys to access an image id that doesn't exist by manually typing the url
        print(NoResultFound)
        flash("Image %d does not exist." % id)
        return redirect(url_for('main'))

    # If image exists, make sure that it belongs to the currently logged in user.
    if image.user_id != current_user.id:
        flash("You do not have access to this image.")
        return redirect(url_for('main'))

    original = url_for("download_file", folder="originals",  image_name=image.file_name)
    face_detection = url_for("download_file", folder="faces",  image_name=image.file_name)

    if image.num_faces == 0:
        flash("There were no faces detected in this image.")
    elif image.num_faces == 1:
        flash("There was 1 face detected in this image.")
    else:
        flash("There were %d faces detected in this image." % image.num_faces)


    return render_template("images/face.html",og=original, face=face_detection, title ="Face Detection" )








################### TA ACCESS ############



@webapp.route('/api/upload', methods=['POST','GET'])
def ta_upload():

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            error_msg = "Did you forget the file? "
            return render_template('users/ta_upload.html',error_msg=error_msg)


        username = request.form.get('username')
        password = request.form.get('password')
        file = request.files.get('file')

        print("username is ", username)
        print("File name",file)



        if len(username) <2  or len(username) > 30 or len(password) <2  or len(password) > 30:
            error_msg = "Username or Password do not meet the length requirements"
            return render_template('users/ta_upload.html',error_msg=error_msg)



        if username == None or password == None or file == None:
            error_msg = "Welcome - Please input credentials and file"
            return render_template('users/ta_upload.html',error_msg=error_msg)


        if username == "" or password == "":
            error_msg = "Error: All fields are required!"
            return render_template('users/ta_upload.html',error_msg=error_msg)


        user = User.query.filter_by(username=username).first()

        if user is None:

            error_msg = "User Not Registered!!"
            return render_template('users/ta_upload.html',error_msg=error_msg)

        else:
            if not user.check_password(password):
                error_msg = "Invalid username and password combination"
                return render_template('users/ta_upload.html',error_msg=error_msg)

            print("Allowed?", allowed_file(file.filename))

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print("secure file name", filename)


                clean_name = sanitize_filename(urllib.parse.unquote(filename)).replace(" ", "_")

                # save original image
                real_name = ntpath.basename(image_uploadset.save(file, folder='originals', name=clean_name))

                print("real_name:",real_name)

                original_path = './images/originals/'+real_name

                print("original_path",original_path)

                image_cv = cv2.imread(original_path)

                # Face detection
                ## need to tell the location of the classifier manually!!
                #face_cascade = cv2.CascadeClassifier('C:/Users/mihir/PycharmProjects/A1_ECE1779/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml')
                #face_cascade = cv2.CascadeClassifier('/Users/bibinsebastian/Dropbox/UofT/ECE1779/A1_ECE1779/venv/lib/python3.6/site-packages/cv2/data/haarcascade_frontalface_default.xml')
                face_cascade = cv2.CascadeClassifier('./venv/lib/python3.5/site-packages/cv2/data/haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                face_cv = image_cv.copy() #this is neeeded since it will throw error if there is no image in the picture

                for (x,y,w,h) in faces:
                    face_cv = cv2.rectangle(image_cv, (x,y) , (x + w,y + h), (0,0,255),8)
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = face_cv[y:y+h, x:x+w]


                picture_path = './images/faces/'+real_name
                cv2.imwrite(picture_path, face_cv)
                cv2.waitKey(0)

                try:
                    image = Image(user_id=user.id, file_name=real_name, num_faces = len(faces))
                    db.session.add(image)
                    db.session.commit()
                    #flash('File Uploaded!')
                    error_msg = "File Upload Success"
                    return render_template('users/ta_upload.html',error_msg=error_msg)
                except Exception as error:
                    db.session.rollback()
                    abort(500, error)
                finally:
                    db.session.close()

            else:
                error_msg = "File is not an Image"
                return render_template('users/ta_upload.html',error_msg=error_msg)

    return render_template('users/ta_upload.html')







