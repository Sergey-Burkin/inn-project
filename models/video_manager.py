#!/usr/bin/env python
#-*- coding: utf-8 -*-
import boto3
from botocore.exceptions import ClientError
import hashlib
from datetime import datetime

class VideoManager:
    def __init__(self):
        self.s3 = boto3.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net'
        )

    def upload_video(self, filepath, bucket_name='innpracbucket'):
        try:
            # Generate a unique filename based on current timestamp
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            
            # Create a hash of the file content
            with open(filepath, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            # Combine timestamp and hash to create a unique filename
            new_file_name = f"{timestamp}_{file_hash}.mp4"
            
            # Upload the video
            self.s3.upload_file(filepath, bucket_name, new_file_name)
            
            # Return the public URL of the uploaded file
            return f"https://storage.yandexcloud.net/{bucket_name}/{new_file_name}"
        except ClientError as e:
            print(f"Error uploading video: {e}")
            return None

    def get_video(self, bucket_name='innpracbucket', filename=None):
        if not filename:
            raise ValueError("Filename must be specified")
        
        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=filename)
            return response
        except ClientError as e:
            print(f"Error getting video: {e}")
            return None

    def delete_video(self, bucket_name='innpracbucket', filename=None):
        if not filename:
            return
        
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=filename)
            return True
        except ClientError as e:
            print(f"Error deleting video: {e}")
            return False
