import pickle
import os
from functools import wraps
from typing import Callable
import json
import urllib.request

import boto3

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]

# More specific typing feels like overkill in this case.


def api_response(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return {"statusCode": 200, "body": str(result)}
        except Exception as e:
            return {"statusCode": 500, "body": str(e)}

    return wrapper


def lambda_handler(event: dict, context):
    if event.get("detail_type") == "ScheduledUpdateRule":
        return update_nodes()
    try:
        match (event["resource"], event["httpMethod"]):
            case ("/health", "GET"):
                print(f"Health check event: {json.dumps(event)}")
                return {"statusCode": 200, "body": "OK"}
            case ("/nodes", "GET"):
                return list_nodes()
            case ("/nodes/{ip}", "GET"):
                return check(event["pathParameters"]["ip"])
            case ("/nodes/{ip}", "DELETE"):
                return delete_node(event["pathParameters"]["ip"])
            case _:
                return {"statusCode": 405, "body": "Method not allowed"}
    except Exception as e:
        return {"statusCode": 400, "body": f"Bad request: {str(e)}"}


def _write_nodes(nodes: set) -> None:
    s3.put_object(Bucket=BUCKET_NAME, Key="tor_nodes.pickle", Body=pickle.dumps(nodes))


def _read_nodes() -> set:
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key="tor_nodes.pickle")
        return pickle.loads(response["Body"].read())
    # catch case where we have no nodes yet
    except (s3.exceptions.NoSuchKey, s3.exceptions.NoSuchBucket):
        update_nodes()
        response = s3.get_object(Bucket=BUCKET_NAME, Key="tor_nodes.pickle")
        return pickle.loads(response["Body"].read())


@api_response
def update_nodes() -> None:
    url = "https://secureupdates.checkpoint.com/IP-list/TOR.txt"
    with urllib.request.urlopen(url) as response:
        _write_nodes(set(response.read().decode().splitlines()))


@api_response
def check(ip: str) -> bool:
    nodes = _read_nodes()
    return ip in nodes


@api_response
def list_nodes() -> str:
    nodes = _read_nodes()
    return json.dumps(list(nodes))


@api_response
def delete_node(ip: str) -> None:
    nodes = _read_nodes()
    nodes.discard(ip)
    _write_nodes(nodes)
