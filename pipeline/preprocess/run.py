#!/usr/bin/env python
import argparse
import logging
import os
import zipfile
import pandas as pd
import wandb


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

def main(args):

    # initiate wandb run
    run = wandb.init(job_type="process_data")

    artifact = run.use_artifact(args.input_artifact)
    artifact_path_zipped = artifact.file()


    # need to unzip the data
    # Define file paths
    output_file_name = 'raw_data.csv'

    # Unzip and read the CSV
    with zipfile.ZipFile(artifact_path_zipped, 'r') as zip_ref:
        # List all files in the zip
        file_list = zip_ref.namelist()
        print("Files inside the zip:", file_list)
    
        # Assuming the CSV is the first CSV file found
        csv_files = [f for f in file_list if f.endswith('.csv')]
    
        if not csv_files:
            print("No CSV files found in the ZIP.")
        else:
            csv_file = csv_files[0]  # Select the first CSV
            zip_ref.extract(csv_file, os.path.dirname(artifact_path_zipped))
        
            extracted_path = os.path.join(os.path.dirname(artifact_path_zipped), csv_file)
            final_path = os.path.join(os.path.dirname(artifact_path_zipped), output_file_name)
        
            # Rename if necessary
            if extracted_path != final_path:
                os.rename(extracted_path, final_path)

            # rename artifact_path
            artifact_path = final_path



    df = pd.read_csv(artifact_path)

    # Drop the duplicates
    logger.info("Dropping duplicates")
    df = df.drop_duplicates().reset_index(drop=True)

    # A minimal feature engineering step: a new feature
    # This should go in a feature store
    logger.info("Feature engineering")
    df['Subscription-Contract'] = df['Subscription Type'] + '-' + df['Contract Length']

    filename = "processed_data.csv"
    df.to_csv(filename)

    artifact = wandb.Artifact(
        name=args.artifact_name,
        type=args.artifact_type,
        description=args.artifact_description,
    )
    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    # remove the temporary files
    # the Artifact object will release on its own
    os.remove(filename)
    os.remove(artifact_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Preprocess a dataset",
        fromfile_prefix_chars="@",
    )

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Fully-qualified name for the input artifact",
        required=True,
    )

    parser.add_argument(
        "--artifact_name", type=str, help="Name for the artifact", required=True
    )

    parser.add_argument(
        "--artifact_type", type=str, help="Type for the artifact", required=True
    )

    parser.add_argument(
        "--artifact_description",
        type=str,
        help="Description for the artifact",
        required=True,
    )

    args = parser.parse_args()

    main(args)















