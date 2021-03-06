'''
    Dependency: None
'''
from aws_cdk import (
    core, aws_iam, aws_lambda
)

class LambdaStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, project: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Init
        self.project = project
        self.role = dict()
        self.function = dict()
        
        # IAM
        self.role['sigv4-request-to-s3'] = aws_iam.Role(self, "sigv4-request-to-s3-role",
            role_name   = f"{project['prefix']}-role-lambda-sigv4-request-to-s3",
            description = "",
            assumed_by  = aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal("lambda.amazonaws.com"),
                aws_iam.ServicePrincipal("edgelambda.amazonaws.com")
            ),
            # external_id=None,
            # external_ids=None,
            inline_policies=None,
            # max_session_duration=None,
            # path=None,
            # permissions_boundary=None,
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
            ]
        )

        # Functions
        self.function['sigv4-request-to-s3'] = aws_lambda.Function(self, "lambda-sigv4-request-to-s3",
            function_name=f"{self.project['prefix']}-lambda-sigv4-request-to-s3",
            code=aws_lambda.Code.asset("./lambda_/source"),
            handler="index.handler",
            runtime=aws_lambda.Runtime.NODEJS_14_X,
            role=self.role['sigv4-request-to-s3'],
            allow_all_outbound=None,
            allow_public_subnet=None,
            code_signing_config=None,
            current_version_options=None,
            dead_letter_queue=None,
            dead_letter_queue_enabled=None,
            description=None,
            environment=None,
            environment_encryption=None,
            events=None,
            filesystem=None,
            initial_policy=None,
            layers=None,
            log_retention=None,
            log_retention_retry_options=None,
            log_retention_role=None,
            memory_size=None,
            profiling=None,
            profiling_group=None,
            reserved_concurrent_executions=None,
            security_group=None,
            security_groups=None,
            timeout=None,
            tracing=None,
            vpc=None,
            vpc_subnets=None,
            max_event_age=None,
            on_failure=None,
            on_success=None,
            retry_attempts=None
        )