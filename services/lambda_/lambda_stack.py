'''
    Dependency: None
'''
from constructs import Construct
from aws_cdk import Stack, aws_iam, aws_lambda

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Init
        self.project = project
        self.role = dict()
        # IAM role
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/Role.html
        self.role['functionA'] = aws_iam.Role(self, "functionA-role",
            role_name   = f"{project['prefix']}-role-lambda-functionA",
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
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        # Functions
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/Function.html
        functionA = aws_lambda.Function(self, "lambda-functionA",
            function_name=f"{self.project['prefix']}-lambda-functionA",
            code=aws_lambda.Code.from_asset("./lambda_/source"),
            handler="index.handler",
            runtime=aws_lambda.Runtime.NODEJS_14_X,
            role=self.role['functionA'],
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