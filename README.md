# Local Setup

These setup instructions are written for OSX.

## If you're starting fresh

You need an [AWS account](https://aws.amazon.com/resources/create-account/) and you need to [install the AWS CDK.](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) The CDK has [a couple prerequisites](https://docs.aws.amazon.com/cdk/v2/guide/prerequisites.html). With that done, Run ```aws configure``` and enter [your credentials](https://aws.amazon.com/blogs/security/how-to-find-update-access-keys-password-mfa-aws-management-console/).
You'll need Python, (your system Python is probably fine if you have one). 

## Otherwise, 
No special setup is needed.
```
# Make the venv:
python -m venv .venv
source .venv/bin/activate  

# Install dependencies (this project only has the default AWS CDK project deps):
pip install -r requirements.txt

# Run bootstrap (first time only):
cdk bootstrap

# Synth if you want to test without deploying:
cdk synth

# Deploy
cdk deploy
```
If you're on windows you'll have to make some adjustments. I recommend WSL in that case though, then you can just use this script.




## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation