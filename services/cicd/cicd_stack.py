'''
    Dependency: vpc, security-group
    You should be:
        1. modify the bucket_name in "codebuild_s3_policy.json" file
        2. modify the bucket_name in  __init__ function.
'''
from constructs import Construct
from aws_cdk import Stack, Duration, RemovalPolicy, aws_ec2, aws_kms, aws_s3, aws_iam, aws_codecommit, aws_codebuild
import json

class CiCdStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, vpc, security_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Init
        self.project        = project
        self.vpc            = vpc
        self.security_group = security_group

        # artifact s3 bucket
        artifact_s3_bucket = self.create_artifact_s3_bucket(bucket_name="useast1-dev-cdkworkshop-artifact")
        
        # codecommit repository
        codecommit_repository = aws_codecommit.Repository(self, "codecommit-account-app",
            repository_name="account-app",
            description="This project for worldskills account")

        # codebuild project
        codebuild_project = aws_codebuild.Project(self, "codebuild-account-app",
            project_name="account-app",
            description=None,
            badge=None,
            concurrent_build_limit=None,
            source=aws_codebuild.Source.code_commit(
                repository=codecommit_repository,
                branch_or_ref=None, # select master branch
                clone_depth=None,
                fetch_submodules=None,
                identifier=None
            ),
            environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
                compute_type=aws_codebuild.ComputeType.SMALL,
                environment_variables=None,
                privileged=True # it's required when docker image build
            ),
            environment_variables={
                "IMAGE_REPO_NAME": aws_codebuild.BuildEnvironmentVariable(
                    value="account-app",
                    type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT),
                "AWS_DEFAULT_REGION": aws_codebuild.BuildEnvironmentVariable(
                    value=self.project["region"],
                    type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT),
                "AWS_ACCOUNT_ID": aws_codebuild.BuildEnvironmentVariable(
                    value=self.project["account"],
                    type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT),
            },
            # network options
            vpc=self.vpc,
            subnet_selection=aws_ec2.SubnetSelection(
                availability_zones=None,
                one_per_az=None,
                subnet_filters=None,
                subnet_group_name=None,
                subnets=None,
                subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT),
            security_groups=[self.security_group["example"]],
            allow_all_outbound=None,
            timeout=None,
            role=None, # default: will be created
            build_spec=None, # default: empty build_spec
            file_system_locations=None,
            # artifacts options
            artifacts=None,
            secondary_artifacts=None,
            secondary_sources=None,
            encryption_key=None,
            cache=None,
            # other options
            check_secrets_in_plain_text_env_variables=False,
            grant_report_group_permissions=None,
            logging=None,
            queued_timeout=None)
        self.add_codebuild_iam_policy(codebuild_project.role)

    def create_artifact_s3_bucket(self, bucket_name):
        # KMS
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_kms/Key.html
        kms_key = aws_kms.Key(self, f"kms-s3-{bucket_name}",
            alias                    = f"alias/{self.project['prefix']}-s3-{bucket_name}",
            description              = "",
            admins                   = None,
            enabled                  = True,
            enable_key_rotation      = True,
            pending_window           = Duration.days(7),
            removal_policy           = RemovalPolicy.DESTROY,
            policy                   = None
        )
        # S3 bucket
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_s3/Bucket.html
        s3_bucket = aws_s3.Bucket(self, f"s3-{bucket_name}",
            bucket_name=bucket_name,
            access_control=aws_s3.BucketAccessControl.PRIVATE,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True),
            public_read_access=False,
            encryption=aws_s3.BucketEncryption.KMS,
            encryption_key=kms_key,
            bucket_key_enabled=True,
            enforce_ssl=True,
            versioned=True,
            cors=None,
            inventories=None,
            lifecycle_rules=None,
            metrics=None,
            object_ownership=None,
            server_access_logs_bucket=None,
            server_access_logs_prefix=None,
            website_error_document=None,
            website_index_document=None,
            website_redirect=None,
            website_routing_rules=None,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=False,
        )
        return s3_bucket

    def add_codebuild_iam_policy(self, role):
        iam_policy = dict()
        with open("cicd/codebuild_s3_policy.json",mode="r") as file:
            # should modify the bucket name in json file
            iam_policy["s3"] = aws_iam.ManagedPolicy(self, "iam-policy-s3", 
                description=None,
                document=aws_iam.PolicyDocument.from_json(
                    json.load(file)
                ))
        with open("cicd/codebuild_ecr_policy.json",mode="r") as file:
            iam_policy["ecr"] = aws_iam.ManagedPolicy(self, "iam-policy-ecr", 
                description=None,
                document=aws_iam.PolicyDocument.from_json(
                    json.load(file)
                ))
        role.add_managed_policy(iam_policy["s3"])
        role.add_managed_policy(iam_policy["ecr"])