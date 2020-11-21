from original_scrape import new_folder
import os

bucket_name = "us_amazon_bronze"
command_script = "gsutil mv -r "+ new_folder+" gs://"+bucket_name
os.system(command_script)


import move_to_gcp



