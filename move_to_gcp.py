from google.cloud import storage
from io import BytesIO
import pandas as pd
import json
import os
from main import new_folder, bucket_name

print("hello")

client = storage.Client()
# bucket_name = "us_amazon_bronze"
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)
# new_folder = "output_20201117_162936"
blobs = bucket.list_blobs(prefix=new_folder+"/")

deal_details_dfs = []
deal_status_dfs = []
for blob in blobs:
    if ".json" in str(blob.name):
        print(blob.name)
        data = json.loads(blob.download_as_string(client=None))
        deal_details_df = pd.DataFrame(data['dealDetails']).transpose().reset_index(drop=True)
        deal_details_df = deal_details_df.drop(columns=['accessBehavior','items','parentItems'])
        deal_details_df['file'] = new_folder+"/"+blob.name
        deal_details_df['scrape_folder'] = deal_details_df['file'].str.split("/", expand=True)[0]
        deal_details_df['scrape_date'] = deal_details_df['scrape_folder'].str.split("_", expand=True)[1]
        deal_details_df['scrape_time'] = deal_details_df['scrape_folder'].str.split("_", expand=True)[2]
        deal_details_dfs.append(deal_details_df)
        deal_status_df = pd.DataFrame(data['dealStatus']).transpose().reset_index().rename(columns={"index":"dealID"})
        deal_status_df = deal_status_df.drop(columns='dealItemStatus')
        deal_status_df['file'] = new_folder+"/"+blob.name
        deal_status_df['scrape_folder'] = deal_status_df['file'].str.split("/", expand=True)[0]
        deal_status_df['scrape_date'] = deal_status_df['scrape_folder'].str.split("_", expand=True)[1]
        deal_status_df['scrape_time'] = deal_status_df['scrape_folder'].str.split("_", expand=True)[2]
        deal_status_dfs.append(deal_status_df)

deal_details = pd.concat(deal_details_dfs)
deal_status = pd.concat(deal_status_dfs)

deal_details_file = str("dealDetails_" + new_folder + ".parquet")
deal_status_file = str("dealStatus_" + new_folder + ".parquet")

deal_details.to_parquet(deal_details_file)
deal_status.to_parquet(deal_status_file)

bucket_name = "us_amazon_silver"
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)

object_name_in_gcs_bucket = bucket.blob("deal_status/" + new_folder + "/" + deal_status_file)
object_name_in_gcs_bucket.upload_from_filename(deal_status_file)
object_name_in_gcs_bucket = bucket.blob("deal_details/" + new_folder + "/" + deal_details_file)
object_name_in_gcs_bucket.upload_from_filename(deal_details_file)

os.system("sudo rm "+deal_status_file)
os.system("sudo rm "+deal_details_file)
os.system("sudo rm -r "+new_folder)

shutdown_script = "gcloud compute instances stop us-amazon --zone us-central1-a"
os.system(shutdown_script)