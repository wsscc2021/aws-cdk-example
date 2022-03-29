from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    aws_iam,
    aws_lambda,
)

class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # IAM Role
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/CfnRole.html
        iam_roles = dict()
        iam_roles["python-helloworld"] = aws_iam.CfnRole(self, "role-python-helloworld",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "lambda.amazonaws.com"
                            ]
                        },
                        "Action": [
                            "sts:AssumeRole"
                        ]
                    }
                ]
            },
            description="description",
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            ],
            max_session_duration=3600,
            path="/",
            permissions_boundary=None,
            policies=None,
            role_name="role-lambda-python-helloworld",)

        # AWS Lambda Function
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/CfnFunction.html
        aws_lambda.CfnFunction(self, "lambda-python-helloworld",
            code=aws_lambda.CfnFunction.CodeProperty(
                image_uri=None,
                s3_bucket="useast1-package-bucket",
                s3_key="python-helloworld.zip",
                s3_object_version=None,
                zip_file=None),
            role=iam_roles["python-helloworld"].attr_arn,
            architectures=[
                "x86_64", # arm64 , x86_64
            ],
            code_signing_config_arn=None,
            dead_letter_config=None,
            description="description",
            environment=aws_lambda.CfnFunction.EnvironmentProperty(
                variables={
                    "Key01": "Value01",
                }),
            function_name="python-helloworld",
            handler="lambda_function.lambda_handler",
            image_config=None, # container settings
            kms_key_arn=None,
            layers=None,
            runtime="python3.9", # https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
            package_type="Zip", # Image, Zip
            reserved_concurrent_executions=None,
            memory_size=128, # unit: MB
            timeout=60, # unit: seconds
            ephemeral_storage=aws_lambda.CfnFunction.EphemeralStorageProperty(
                size=512 #  /tmp directory size, unit: MB
            ),
            file_system_configs=None, # EFS
            tags=[
                CfnTag(
                    key="Name",
                    value="python-helloworld"
                )
            ],
            tracing_config=None, # X-Ray
            vpc_config=None)