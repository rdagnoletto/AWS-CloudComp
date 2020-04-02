import os

# In __init__.py these are loaded into a config dict
class Config(object):

	# Secret key should be set as an environment variable on the webserver
	# but this will fall back on a randomly generated key
	#SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(16).hex()
	SECRET_KEY = '115cdb33c7a42a4dde68e9d735c6589d'
	#SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@ece1779.cvcuzp6pmmiu.us-east-1.rds.amazonaws.com/ece1779'
	#SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@ece1779-1.cu4cz2ndgdbf.us-east-1.rds.amazonaws.com/ece1779'
	#SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@127.0.0.1/ece1779_A1'
	#SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@ece1779new.cu4cz2ndgdbf.us-east-1.rds.amazonaws.com/ece1779'
	#final_RDS
	SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@ece1779a2.cu4cz2ndgdbf.us-east-1.rds.amazonaws.com/ece1779'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	UPLOADED_IMAGES_DEST = "./images/"
	S3_BUCKET = "cloudbuster1"
	S3_KEY = "AKIAI7LCCCSTGKOMT7ZA"
	S3_SECRET = "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"
	S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)


	AMI_ID = 'ami-00345de3fb8cb8056' # new py3.7 AMI created and changed RDS to ece1779a2
	KEY_NAME = 'ece1779_A1'
	SEC_GRP  = 'launch-wizard-3'
	SEC_GRP_ID = 'sg-039330932ae5af1db'
	INST_TYPE = 't2.micro'
	ELB_NAME = 'a2'
