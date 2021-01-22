# blob-trigger-unzip

This function fires when a .zip file is uploaded to a container specified in INPUT_CONTAINER_NAME, and extracts its contents to a container 
defined in OUTPUT_CONTAINER_NAME.

The rawtestdata_STORAGE environment variable represents the Azure blob storage account connection string. This as well as INPUT_CONTAINER_NAME and 
OUTPUT_CONTAINER_NAME will need to be added as application settings in function app --> configuration.
