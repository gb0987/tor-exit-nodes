from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
)
from constructs import Construct


class TorExitNodesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "TorNodesBucket")

        handler = _lambda.Function(
            self,
            "TorNodesHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("lambda"),
            handler="handler.lambda_handler",
            timeout=Duration.seconds(30),
            environment={"BUCKET_NAME": bucket.bucket_name},
        )

        bucket.grant_read_write(handler)

        api = apigw.RestApi(self, "TorNodesApi")

        
        check_resource = api.root.add_resource("check")
        ip_resource = check_resource.add_resource("{ip}")
        
        
        ip_resource.add_method("GET", apigw.LambdaIntegration(handler))

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "TorExitNodesQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
