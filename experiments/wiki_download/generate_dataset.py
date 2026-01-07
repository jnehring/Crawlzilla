# parse the output of the crawler / parser and write final data files
# also compute statistics 

import os
import gzip
import json
import pandas as pd
import nltk
import re
from tqdm import tqdm
import argparse
import pyarrow as pa
import pyarrow.parquet as pq
from typing import List
import shutil
import pyarrow.dataset as ds
import sys
import glob

# parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
                        prog='Crawlzilla Dataset Generator',
                        description='Generate a Parquet dataset from all crawls.')
    
    parser.add_argument('--input_folder', default="extractor_output", type=str, help="folder in which the input data is stored. by default, this is ../outputs")
    parser.add_argument('--output_folder', default="final_dataset", type=str, help="Folder in which the output data is stored. by default, this is ../outputs/final_dataset")
    parser.add_argument('--batch_size', default=500000, type=int, help="Number of samples in each batch. Default is 500.000 which writes batches of about 40MB to disk.")

    return parser.parse_args()

# iterate over all data files and yield batches
def iterate_over_files(args):
    batch = []
    for iso2_lang in os.listdir(args.input_folder):
        dedub = []

        infiles = glob.glob(os.path.join(args.input_folder, iso2_lang, '*/*'))

        language_mapping = {'af': 'afr',
            'am': 'amh',
            'ha': 'hau',
            'rw': 'kin',
            'so': 'som',
            'sw': 'swa',
            'xh': 'xho',
            'yo': 'yor'}

        assert iso2_lang in language_mapping.keys()
        iso3_lang = language_mapping[iso2_lang]

        pbar = tqdm(total=len(infiles))
        
        dedups = set()

        print(f"reading {len(infiles)} files from folder {os.path.join(args.input_folder, iso2_lang)}")

        for file in infiles:
            with open(file) as f:
                for line in f:
                    h = hash(line)
                    if h in dedups:
                        continue

                    dedups.add(h)

                    batch.append({
                        "text": line[0:-1],
                        "language": iso3_lang,
                    })


                    if len(batch) >= args.batch_size:
                        yield batch
                        batch = []

            pbar.update(1)

    if len(batch) > 0:
        yield batch

# initialize the parquet dataset
def create_parquet_schema(folder):

    if not os.path.exists(folder):
        os.makedirs(folder)

    schema = pa.schema([
        ("text", pa.large_string()),
        ("language", pa.dictionary(pa.int8(), pa.string())),  # efficient tiny codes
    ])
    common_meta_path = os.path.join(folder, "_common_metadata")
    meta_path = os.path.join(folder, "_metadata")

    # Write dataset-level metadata that carries the schema
    pq.write_metadata(schema, common_meta_path)
    pq.write_metadata(schema, meta_path)

    return schema

# write one batch to parquet
def write_batch(folder : str, batch : List, batch_number : int):
    table = pa.table({
        "text": pa.array([row['text'] for row in batch], type=pa.large_string()),
        "language": pa.array([row['language'] for row in batch], type=pa.dictionary(pa.int8(), pa.string())),
    })

    writer = pq.ParquetWriter(
        os.path.join(folder, f"part-{batch_number:05d}.parquet"),
        schema=table.schema,
        compression="zstd",
        use_dictionary=["language"],
        write_statistics=True,
    )
    writer.write_table(table)

# read the dataset and compute statistics
def create_stats(args, dataset_folder):

    print('compute statistics')
    dataset = ds.dataset(dataset_folder, format="parquet")

    total_rows = sum(fragment.metadata.num_rows for fragment in dataset.get_fragments())
    stats = {}
    pbar = tqdm(total=total_rows)
    for batch in dataset.to_batches():
        for row in batch.to_pylist():

            key = row['language']
            if key not in stats:
                stats[key] = {
                    "language": row['language'],
                    "characters": 0,
                    "sentences": 0,
                    "words": 0,
                }
            for l in row['text'].split("\n"):
                sent_text = nltk.sent_tokenize(l) # this gives us a list of sentences
                stats[key]["sentences"] += len(sent_text)

                for sent in sent_text:
                    stats[key]["words"] += len(sent.split(" "))
                    stats[key]["characters"] += len(sent)
            
            pbar.update(1)

    # output stats
    report = []
    for s in stats.values():
        language_stats = {
            "language": s['language'],
            "words": s['words'],
            "characters": s['characters'],
            "sentences": s['sentences']
        }
        report.append(language_stats)

    report_str = []
    for r in report:
        language_stats = []
        for key, value in r.items():
            language_stats.append(f"{key}: {value}")
        report_str.append("\n".join(language_stats))
    report_str = "\n-----\n".join(report_str)
    print("Statistics")
    print(report_str)
    print()

    outfile = os.path.join(args.output_folder, "stats.csv")
    pd.DataFrame(report).to_csv(outfile)
    print("wrote statistics to " + outfile)

def setup_nltk():
    try:
        nltk.data.find('tokenizers/punkt/PY3_tab')
    except Exception as e:
        print("Downloading 'punkt_tab' NLTK data...")
        nltk.download('punkt_tab')

def main():

    args = parse_args()
    setup_nltk()
    if os.path.exists(args.output_folder):
        shutil.rmtree(args.output_folder)
    os.makedirs(args.output_folder)

    dataset_folder = os.path.join(args.output_folder)
    schema = create_parquet_schema(dataset_folder)
    i = 0
    all_stats = {}
    for batch in iterate_over_files(args):
        write_batch(dataset_folder, batch, i)
        i += 1

    create_stats(args, dataset_folder)

if __name__ == "__main__":
    main()
