import aws_cdk as cdk
import aws_cdk.assertions as assertions

from tor_exit_nodes.tor_exit_nodes_stack import TorExitNodesStack


def test_tor_exit_nodes_stack():
    app = cdk.App()
    stack = TorExitNodesStack(app, "test-stack")
    template = assertions.Template.from_stack(stack)
    template.has_resource("AWS::S3::Bucket", {})
    template.has_resource(
        "AWS::Lambda::Function",
        {
            "Properties": {
                "Runtime": "python3.12",
                "Handler": "handler.lambda_handler",
                "Timeout": 30,
            }
        },
    )
    template.has_resource("AWS::ApiGateway::RestApi", {})
    template.has_resource(
        "AWS::Events::Rule", {"Properties": {"ScheduleExpression": "rate(1 day)"}}
    )
