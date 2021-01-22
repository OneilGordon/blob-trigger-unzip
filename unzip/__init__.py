import logging
import azure.functions as func

import os
import zipfile
import tempfile
from io import BytesIO, StringIO

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError

def main(myblob: func.InputStream, inputBlob: func.InputStream, outputBlob: func.Out[func.InputStream]) -> None:
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
                 
    #connect to storage account
    connect_str = os.environ["rawtestdata_STORAGE"]
    input_container = os.environ["INPUT_CONTAINER_NAME"]
    output_container = os.environ["OUTPUT_CONTAINER_NAME"]
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    input_container_client = blob_service_client.get_container_client(input_container)

    if input_container != output_container:
        try:
            output_container_client = blob_service_client.get_container_client(output_container)
            output_container_client.create_container()
        except ResourceExistsError:
            output_container_client = blob_service_client.get_container_client(output_container)
    else:
        output_container_client = input_container_client 

    #extract filename from myblob path
    file_path = str(myblob.name)
    blob_name = file_path[file_path.rindex('/')+ 1:]
    blob_client_input = input_container_client.get_blob_client(blob_name)

    #download blob stream data
    download_stream = blob_client_input.download_blob()
    converted_data = BytesIO(download_stream.readall())
    
    #create zipfile object and upload extractred files
    zip_object = zipfile.ZipFile(converted_data, "a")
    with tempfile.TemporaryDirectory() as dir_name:
        for filename in zip_object.namelist():
            directory = os.path.basename(filename)
            #skip directories
            if not directory:
                continue
            
            zip_object.extract(filename, path=dir_name)
            file_location = os.path.join(dir_name, filename)
            with open(file_location, "rb") as f:
                blob_client_output = output_container_client.get_blob_client(filename)
                blob_client_output.upload_blob(f, overwrite=True)


    
