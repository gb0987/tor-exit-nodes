import aws_cdk as core
import aws_cdk.assertions as assertions

from tor_exit_nodes.tor_exit_nodes_stack import TorExitNodesStack

# example tests. To run these tests, uncomment this file along with the example
# resource in tor_exit_nodes/tor_exit_nodes_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TorExitNodesStack(app, "tor-exit-nodes")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
