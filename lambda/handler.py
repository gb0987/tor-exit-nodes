import pickle
import os
from functools import wraps
from typing import Callable
import json
import urllib.request
import ipaddress

import boto3

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]

# More specific typing feels like overkill in this case.


def api_response(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if isinstance(result, dict) and "statusCode" in result:
                return result
            return {"statusCode": 200, "body": str(result)}
        except Exception as e:
            return {"statusCode": 500, "body": str(e)}

    return wrapper


def lambda_handler(event: dict, context):
    if event.get("detail_type") == "ScheduledUpdateRule":
        return update_nodes()
    try:
        print(f"Event: {event}")  # Very basic logging. Could be expanded.
        match (event["resource"], event["httpMethod"]):
            case ("/health", "GET"):
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
    # I considered using something flashier, but that wouldn't make sense. It doesn't need to be encrypted at rest and it doesn't need to scale. It's a small list of publically available IPs, the fastest and cheapest solution is just to pickle.
    s3.put_object(Bucket=BUCKET_NAME, Key="tor_nodes.pickle", Body=pickle.dumps(nodes))


def _read_nodes() -> set:
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key="tor_nodes.pickle")
        return pickle.loads(response["Body"].read())
    except (s3.exceptions.NoSuchKey, s3.exceptions.NoSuchBucket):
        update_nodes()
        response = s3.get_object(Bucket=BUCKET_NAME, Key="tor_nodes.pickle")
        return pickle.loads(response["Body"].read())


def _clean_ip(ip: str) -> str:
    ip = urllib.parse.unquote(ip)
    ip = ip.strip("[]")
    try:
        ip = ipaddress.ip_address(ip)
        if isinstance(ip, ipaddress.IPv6Address):
            return f"[{ip.exploded}]"
        else:
            return str(ip)
    except ValueError:
        raise ValueError(f"Invalid IP address: {ip}")


@api_response
def update_nodes() -> None:
    url = "https://secureupdates.checkpoint.com/IP-list/TOR.txt"
    with urllib.request.urlopen(url) as response:
        _write_nodes(set(response.read().decode().splitlines()))


@api_response
def check(ip: str) -> bool:
    nodes = _read_nodes()
    return _clean_ip(ip) in nodes


@api_response
def list_nodes() -> str:
    nodes = _read_nodes()
    return json.dumps(list(nodes))


@api_response
def delete_node(ip: str) -> None:
    nodes = _read_nodes()
    ip = _clean_ip(ip)
    if ip not in nodes:
        return {"statusCode": 404, "body": "IP not found"}
    nodes.remove(ip)
    _write_nodes(nodes)
    return {"statusCode": 200, "body": "Deleted"}
