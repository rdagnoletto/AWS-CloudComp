import os

# In __init__.py these are loaded into a config dict
class Config(object):

	# Secret key should be set as an environment variable on the webserver
	# but this will fall back on a randomly generated key
	SECRET_KEY = 'b83d2ea251fe701a376fb991854894bf'
	#SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@ece1779.cvcuzp6pmmiu.us-east-1.rds.amazonaws.com/ece1779'
	#SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@ece1779-1.cu4cz2ndgdbf.us-east-1.rds.amazonaws.com/ece1779'
	#SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@ece1779new.cu4cz2ndgdbf.us-east-1.rds.amazonaws.com/ece1779'
	#SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@127.0.0.1/ece1779_A1'
	#final_RDS
	SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@a3.cu4cz2ndgdbf.us-east-1.rds.amazonaws.com/root'
	###########
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	UPLOADED_IMAGES_DEST = "/tmp/"
	S3_BUCKET = "cloudbustera3"
	S3_BUCKET_WATER = "cloudbustera3"
	S3_KEY = "AKIAI7LCCCSTGKOMT7ZA"
	S3_SECRET = "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"
	S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
	S3_LOCATION_WATER = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET_WATER)
	DDB_USER_TBL_NAME ='User_1'
	DDB_ATTRIB_TBL_NAME ='Attrib_1'

	TWIN_API_KEY = 'YA3FEliVOh+JmhhuHYyS7PBs6KujyQithRBFWrB4s9aYEWDzzeJB1tY7C76qhelhhniiy0xwOSb7oZcIruxJyQ=='

	DEEPAI_API_KEY = 'dcc9e673-d571-439b-a1f1-156b5e71677b'
	# AWS_ACCESS_KEY_ID = "AKIAJCPFXVIUU4LRWX2A"
	# AWS_SECRET_ACCESS_KEY = "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"