# lambda/handler.py
import pickle
import os
from functools import wraps
from typing import Callable
import json

import requests
import boto3

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]


def api_response(f: Callable):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return {"statusCode": 200, "body": str(result)}
        except Exception as e:
            return {"statusCode": 500, "body": str(e)}

    return wrapper


def lambda_handler(event, context):
    if event.get("detail_type") == "ScheduledUpdate":
        return update_nodes()
    try:
        match (event["resource"], event["httpMethod"]):
            case ("/health", "GET"):
                return {"statusCode": 200, "body": "OK"}
            case ("/list", "GET"):
                return list_nodes()
            case ("/check/{ip}", "GET"):
                return check(event["pathParameters"]["ip"])
            case ("/delete/{ip}", "DELETE"):
                return delete_node(event["pathParameters"]["ip"])
            case _:
                return {"statusCode": 405, "body": "Method not allowed"}
    except Exception as e:
        return {"statusCode": 400, "body": f"Bad request: {str(e)}"}


def _write_nodes(nodes: set):
    s3.put_object(Bucket=BUCKET_NAME, Key="tor_nodes.pickle", Body=pickle.dumps(nodes))


def _read_nodes() -> set:
    response = s3.get_object(Bucket=BUCKET_NAME, Key="tor_nodes.pickle")
    return pickle.loads(response["Body"].read())


# TODO: schedule this to run at regular intervals! daily, or however often the list actually gets updated!


@api_response
def update_nodes():
    response = requests.get("https://secureupdates.checkpoint.com/IP-list/TOR.txt")
    response.raise_for_status()
    # this could be .. idk redis instead of pickled. but why invoke another aws service, we just gonna keep overwriting the whole thing, we're just adding complexity and slowing down calls at that point
    # could also format the ips in some other way at this point. right now we even include the brackets!
    response = set(response.text.splitlines())
    _write_nodes(response)


@api_response
def check(ip: str) -> bool:
    nodes = _read_nodes()
    return ip in nodes


@api_response
def list_nodes():
    nodes = _read_nodes()
    return json.dumps(list(nodes))


@api_response
def delete_node(ip: str):
    nodes = _read_nodes()
    nodes.remove(ip)
    _write_nodes(nodes)
