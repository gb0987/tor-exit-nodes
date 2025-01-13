#!/usr/bin/env python3
import os

import aws_cdk as cdk

from tor_exit_nodes.tor_exit_nodes_stack import TorExitNodesStack


app = cdk.App()
TorExitNodesStack(
    app,
    "TorExitNodesStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

app.synth()
