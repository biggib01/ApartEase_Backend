import json

from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import os
from library.main import db, app, az
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from library.functions import getNameFromURL

load_dotenv()

# Azure Blob Storage configuration
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')
CONTAINER_NAME = os.getenv('CONTAINER_NAME')

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400

    files = request.files.getlist('files[]')
    uploaded_file_urls = []

    for file in files:
        if file.filename == '':
            continue

        # Save file locally
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Upload to Azure Blob Storage
        blob_client = container_client.get_blob_client(file.filename)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)

        # Generate a URL with SAS token for the uploaded file
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=CONTAINER_NAME,
            blob_name=file.filename,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)  # URL will be valid for 1 hour
        )

        file_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{file.filename}"



        uploaded_file_urls.append(file_url)

    headers = {
        'Content-Type': 'application/json'
    }

    for url_img in uploaded_file_urls:
        data = {
            'url': url_img
        }
        try:
            # request for prediction
            response = requests.post('http://213.180.0.67:20010/predict', headers=headers, json=data)

            response_json = json.loads(response.json())

            # Join all classes starting from index 0 into a single number (string)
            numberOfUnits = ''.join([str(pred['class']) for pred in response_json['predictions']])

            # Get room number
            roomNumber = response_json['room_number']

            # Check if there are any warnings
            if response_json['warnings']:
                extractionStatus = "Not fully successful"
            else:
                extractionStatus = "Fully successful"

            create_unit = {
                'numberOfUnits': numberOfUnits,
                'extractionStatus': extractionStatus,
                'res_room': roomNumber,
                'imgUrl': url_img
            }

            requests.post('http://127.0.0.1:1234/unit/add', headers=headers, json=create_unit)

        except Exception as e:

            filename = getNameFromURL(url_img)

            az.delete_file(filename)

            return make_response(jsonify({'error': 'There is some problem/error with backend.'}), 500)

    return make_response(jsonify({'uploaded_file_urls': uploaded_file_urls}), 200)