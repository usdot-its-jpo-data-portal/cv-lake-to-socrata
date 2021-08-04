import json
import os
from unittest import TestCase, mock


TEST_ENV_VAR = {
    "AUTH": '{"domain": "datahub.transportation.gov", "username": "someUsername", "password": "somePassword"}',
    "EVENT": '{"overwrite": true, "num_hours_backtrack": 720, "s3_source_bucket": "usdot-its-cvpilot-public-data", "s3_source_prefix": "nycdot/EVENT", "socrata_dataset_id": "xxxx-xxxx", "float_fields": [], "data_sample_length": "month", "permission": "private"}',
}

class TestImports(TestCase):
    @mock.patch.dict(os.environ, TEST_ENV_VAR)
    def test_import(self):
        import src.run