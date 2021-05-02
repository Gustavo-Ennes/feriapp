from google.cloud import storage
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def download_from_cloud():
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket("feriapp")

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob('pdf.pdf')
    blob.download_to_filename(os.path.join(PROJECT_ROOT, 'temp', 'pdf.pdf'))

    print("Pdf downloaded to %s" % (os.path.join(PROJECT_ROOT, 'temp', 'pdf.pdf')))

def upload_to_cloud():
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket('feriapp')
    blob = bucket.blob('pdf.pdf')

    blob.upload_from_filename(os.path.join(PROJECT_ROOT, 'temp', 'pdf.pdf'))

    print('Pdf uploaded to cloud')
