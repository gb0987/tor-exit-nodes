# Local Setup

These setup instructions are written for OSX. 

## If you're starting fresh

You need an [AWS account](https://aws.amazon.com/resources/create-account/) and you need to [install the AWS CDK.](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) The CDK has [a couple prerequisites](https://docs.aws.amazon.com/cdk/v2/guide/prerequisites.html). With that done, Run ```aws configure``` and enter [your credentials](https://aws.amazon.com/blogs/security/how-to-find-update-access-keys-password-mfa-aws-management-console/).
You'll need Python, (your system Python is probably fine if you have one). 

## Normal Setup 

```bash 
# Make the venv:
python3 -m venv .venv
source .venv/bin/activate  

# Install dependencies (this project only has the default AWS CDK project dependencies):
pip install -r requirements.txt

# Run bootstrap (first time only):
cdk bootstrap

# Synth if you want to test without deploying:
cdk synth

# Deploy
cdk deploy
```
If you're on windows you'll have to make some adjustments. I recommend [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) in that case though, then you can just use this script.

You may want to install dev dependencies for local work.

```pip install -r requirements-dev.txt```

# Docs

This is a simple API for managing a list of known Tor exit nodes. The list is automatically updated daily from [CheckPoint's database]("https://secureupdates.checkpoint.com/IP-list/TOR.txt").

IPv6 addresses can be passed in any form. They will be converted to exploded/long/full form.

## Endpoints

### Health Check

Simple function to check if the server is up.

```bash
GET /health
```

Response:

```json
{
    "statusCode": 200,
    "body": "OK"
}
```

### List All Nodes

Returns all known Tor exit nodes.

```
GET /nodes
```

Response:

```json
{
    "statusCode": 200,
    "body": ["1.2.3.4", "5.6.7.8"]
}
```

### Check Node

Check if a particular address is a Tor exit node. Returns "true" or "false".

```
GET /nodes/{ip}
```

Parameters:
- `ip`: IP address to check

Response:

```json
{
    "statusCode": 200,
    "body": "true" 
}
```

### Delete Node

```
DELETE /nodes/{ip}
```

Parameters:
- `ip`: IP address to remove

Response if IP exists:

```json
{
    "statusCode": 200,
    "body": "Deleted"
}
```

Response if IP not found:

```json
{
    "statusCode": 404,
    "body": "IP not found"
}
```

# Tests
I included some very basic tests.

```python -m pytest tests/unit```


## Testing from Terminal

Use the [invoke URL](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-call-api.html).

```bash
export TEST_API_URL=https://your-actual-api-url.com
# Health check
curl $TEST_API_URL/health
# List all nodes
curl $TEST_API_URL/nodes
# Check specific IP
curl $TEST_API_URL/nodes/1.2.3.4
# Delete node
curl -X DELETE $TEST_API_URL/nodes/1.2.3.4
```

Note that passing brackets in with a IPv6 url will cause issues when using curl, you can just omit them.


# Possible Improvements

Storing pickled files in s3 and reading them with lambda is fast and extremely cheap. If we needed to go much much faster, the API could use DynamoDB instead, but that seems like overkill. 

The API Gateway has aggressive throttling so that we can't exceed free tier by much. It could have some kind of usage quota and API keys instead. Again, seemed like overkill.

Finally, deletions don't persist through the daily update of the IP list. It wouldn't be difficult to add, but it would effectively be a blacklist/exclusionlist which should then have even more functionality. At minimum, you should be able to reset the list. At that point it would make more sense to just have all the CRUD functions, a full API, just maintain a parallel Tor nodes database with some updates from CheckPoint. That was not the ask, so I kept it simple instead.