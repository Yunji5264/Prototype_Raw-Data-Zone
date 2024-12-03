from google.cloud import storage

def upload_file_to_gcs(bucket_name, metadata_path):
    """上传文件到 Google Cloud Storage 的根目录。

    参数:
    bucket_name (str): GCS 存储桶名称。
    metadata_path (str): 要上传的文件的本地路径。
    """
    # 创建一个 GCS 客户端实例
    storage_client = storage.Client()

    # 获取 GCS 存储桶
    bucket = storage_client.bucket(bucket_name)

    # 直接使用文件名作为 blob 名称
    destination_blob_name = metadata_path.split('/')[-1]  # 使用 os.path.basename(metadata_path) 更加通用

    # 创建 blob 对象
    blob = bucket.blob(destination_blob_name)

    # 上传文件
    blob.upload_from_filename(metadata_path)
    print(f"File {metadata_path} uploaded to {destination_blob_name} in bucket {bucket_name}.")
