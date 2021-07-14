"""
Flatten records from ITS Sandbox S3 bucket and publish to Socrata.

"""
from __future__ import print_function

from copy import deepcopy
from datetime import datetime, timedelta
import io
import json
import logging
import os
import traceback
from time import time

import pandas as pd
from socrata.authorization import Authorization
from socrata import Socrata, Revisions

from sandbox_exporter.flattener import load_flattener
from sandbox_exporter.s3 import S3Helper


logger = logging.getLogger()
logger.setLevel(logging.INFO)  # necessary to make sure aws is logging

s3_helper = S3Helper()


def run(event, auth):
    '''
    Sample event:
    {
        "overwrite": True,
        "num_hours_backtrack": 720,
        "s3_source_bucket": "usdot-its-cvpilot-public-data",
        "s3_source_prefix": "nycdot/EVENT",
        "socrata_dataset_id": "usnx-z3mt",
        "float_fields": [],
        "data_sample_length": "month",
        "permission": "private"
    }

    Sample auth:
    {
        "domain": "datahub.transportation.gov",
        "username": "someUsername",
        "password": "somePassword"
    }

    '''
    socrata_auth = Authorization(
        auth['domain'],
        auth['username'],
        auth['password']
    )

    formatted_source_prefix = get_formatted_source_prefix(**event)
    s3_source_kwargs = {"Bucket": event['s3_source_bucket'], "Prefix": formatted_source_prefix}
    
    revision = Revisions(event['socrata_dataset_id'], socrata_auth)
    if event['overwrite'] == True:
        replacement = revision.create_replace_revision(permission=event['permission'])
        print('Overwrite')
    else:
        replacement = revision.create_update_revision(permission=event['permission'])
    source = replacement.create_upload(f"{formatted_source_prefix.replace('/', '_')}.csv")
    result = source._chunked_bytes(bytes_generator(s3_source_kwargs), "text/csv")
    input_schema = result.get_latest_input_schema()
    output_schema = input_schema.get_latest_output_schema()
    job = replacement.apply(output_schema=output_schema)
    job = job.show()
    job.wait_for_finish(progress = lambda job: logger.info(job.attributes['status']))


def get_formatted_source_prefix(data_sample_length, s3_source_prefix, num_hours_backtrack, **kwargs):
    if data_sample_length == 'static':
        return s3_source_prefix

    source_ymdh = datetime.today() - timedelta(hours=num_hours_backtrack)
    y,m,d = source_ymdh.strftime('%Y-%m-%d').split('-')
    if data_sample_length == 'month':
        return f"{s3_source_prefix}/{y}/{m}"
    else:
        return f"{s3_source_prefix}/{y}/{m}/{d}"

def bytes_generator(s3_source_kwargs, limit=None):
    bucket_key_tuples, next_s3_source_kwargs = s3_helper.get_fp_chunks_from_prefix(s3_source_kwargs)
    if len(bucket_key_tuples) > 0:
        flattener_mod = load_flattener(bucket_key_tuples[0][1])
    flattener = flattener_mod()

    count = 0
    while bucket_key_tuples or next_s3_source_kwargs:
        for idx, bucket_key in enumerate(bucket_key_tuples):
            bucket, key = bucket_key
            if limit is not None and count >= limit:
                bucket_key_tuples, next_s3_source_kwargs = None, None
                break
            stream = s3_helper.get_data_stream(bucket, key)
            flat_recs = []
            for r in s3_helper.newline_json_rec_generator(stream):
                try:
                    flat_recs += flattener.process_and_split(r)
                except:
                    logger.error(f"Error while transforming record: {r}")
                    logger.error(traceback.format_exc())
                    raise
            df = pd.DataFrame(flat_recs)
            df = prep_df(df, flattener.col_order)
            s = io.StringIO()
            if count == 0:
                df.to_csv(s, index=False, header=True)
                for i in s.getvalue():
                    yield i.encode()
            else:
                df.to_csv(s, index=False, header=False)
                for i in s.getvalue():
                    yield i.encode()

            count += len(df)
        bucket_key_tuples = []
        if next_s3_source_kwargs:
            bucket_key_tuples, next_s3_source_kwargs = s3_helper.get_fp_chunks_from_prefix(next_s3_source_kwargs)

def prep_df(df, col_order):
    for col in col_order:
        if col not in df.columns:
            df[col] = None
    return df[col_order]


if __name__ == '__main__':
    t0 = time()
    event = json.loads(os.environ.get('EVENT'))
    auth = json.loads(os.environ.get('AUTH'))
    auth['domain'] = 'datahub.transportation.gov'
    print('Starting event:')
    print(event)
    run(event, auth)
    t1 = time()
    print(f'Run completed in {(t1-t0)/60:.02} minutes.')