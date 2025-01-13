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

        api = apigw.RestApi(
            self,
            "TorNodesApi",
            deploy_options=apigw.StageOptions(
                throttling_rate_limit=1, throttling_burst_limit=5
            ),
        )
        api.root.add_resource("health").add_method(
            "GET", apigw.LambdaIntegration(handler)
        )
        nodes = api.root.add_resource("nodes")
        nodes.add_method("GET", apigw.LambdaIntegration(handler))  # list
        node = nodes.add_resource("{ip}")
        node.add_method("GET", apigw.LambdaIntegration(handler))  # check
        node.add_method("DELETE", apigw.LambdaIntegration(handler))  # delete

        rule = events.Rule(
            self,
            "ScheduledUpdateRule",
            schedule=events.Schedule.rate(Duration.days(1)),
            targets=[
                targets.LambdaFunction(
                    handler,
                    event=events.RuleTargetInput.from_object(
                        {"detail_type": "ScheduledUpdateRule"}
                    ),
                )
            ],
        )
        rule.add_target(targets.LambdaFunction(handler))
