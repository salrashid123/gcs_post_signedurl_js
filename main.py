import logging
import json
import uuid

from flask import Flask, render_template, request, Response,  send_from_directory, abort, redirect, jsonify, session
import os
import pprint
import sys

from base64 import b64encode
import string
import datetime

import requests
import http.client as http_client

from google.cloud import storage

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'
import google.auth
from google.oauth2 import service_account 
credentials = service_account.Credentials.from_service_account_file('svc_account.json')

bucketName = 'uploader-334920-urlsigner'
client = storage.Client(credentials=credentials)
bucket = client.get_bucket(bucketName)

app = Flask(__name__, static_url_path='')

@app.route('/public/<path:path>')
def send_file(path):
    return send_from_directory('public', path)

@app.route('/getSignedURL')
def getSignedURL():
  filename = request.args.get('filename')
  action = request.args.get('action')
  blob = bucket.blob(filename)
  url = blob.generate_signed_url(
        expiration=datetime.timedelta(minutes=10),
        method=action, version="v4")
  return url


@app.route('/getSignedPolicyDocument')
def getSignedPolicyDocument():
  filename = request.args.get('filename')
  conditions = [["starts-with", "$key", "myfolder/"], {"acl": "bucket-owner-read"}, ["eq", "$Content-Type", "text/plain" ]]
  expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
  policy = bucket.generate_upload_policy(conditions, expiration=expiration)
  return jsonify(policy)


@app.route('/policydocument')
def policydoucment():
  return render_template('policydocument.html')

@app.route('/signedurl')
def signedurl():
  return render_template('signedurl.html')

@app.route('/dropzone')
def home():
  return render_template('dropzone.html')

@app.route('/')
def index():
  return send_from_directory('public', 'index.html')

if __name__ == '__main__':

    context = ('server.crt','server.key')
    app.run(host='0.0.0.0', port=8081,  threaded=True, ssl_context=context)


