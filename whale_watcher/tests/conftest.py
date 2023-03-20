# PyTest fixtures
from pathlib import Path
import pytest
import boto3
import os
from moto import mock_ecr, mock_s3, mock_sts

@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ['AWS_PROFILE'] = 'foo'
    moto_mock_cred_fp = Path(__file__).parent.absolute() / 'mock_aws_credentials'
    print(moto_mock_cred_fp)

    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = str(moto_mock_cred_fp)

@mock_sts
def test_check_aws_profile(aws_credentials):
    session = boto3.Session(profile_name='foo')
    client = session.client('sts')
    client.get_caller_identity().get('Account')

@pytest.fixture
def ecr_client(aws_credentials):
    # mock ecr client
    with mock_ecr():
        session = boto3.Session(profile_name='foo')
        conn = session.client('ecr', region_name='us-east-1')
        yield conn

@pytest.fixture
def s3_client(aws_credentials):
    # mock s3 client
    with mock_s3():
        session = boto3.Session(profile_name='foo')
        yield boto3.client("s3", region_name='us-east-1')