'''
    Dependency: None
'''
from aws_cdk import (
    core, aws_kms, aws_iam, aws_s3
)

class S3Stack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, project: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Init
        self.project = project
        self.kms_key = dict()
        self.s3_bucket = dict()

        # KMS
        self.kms_key['s3-bucket'] = aws_kms.Key(self, "kms-s3-bucket",
            alias                    = f"alias/{project['prefix']}-s3-bucket",
            description              = "",
            admins                   = None,
            enabled                  = True,
            enable_key_rotation      = True,
            pending_window           = core.Duration.days(7),
            removal_policy           = core.RemovalPolicy.DESTROY,
            policy                   = aws_iam.PolicyDocument(
                statements=[
                    aws_iam.PolicyStatement(
                        sid="Enable IAM User Permission",
                        actions=[
                            "kms:*"
                        ],
                        conditions=None,
                        effect=aws_iam.Effect.ALLOW,
                        not_actions=None,
                        not_principals=None,
                        not_resources=None,
                        principals=[
                            aws_iam.AccountRootPrincipal()
                        ],
                        resources=["*"]
                    ),
                    aws_iam.PolicyStatement(
                        sid="Allow access through S3 for all principals in the account that are authorized to use S3",
                        actions=[
                            "kms:Encrypt",
                            "kms:Decrypt",
                            "kms:ReEncrypt*",
                            "kms:GenerateDataKey*",
                            "kms:DescribeKey"
                        ],
                        conditions={
                            "StringEquals": {
                                "kms:CallerAccount": "242593025403",
                                "kms:ViaService": "s3.us-east-1.amazonaws.com"
                            }
                        },
                        effect=aws_iam.Effect.ALLOW,
                        not_actions=None,
                        not_principals=None,
                        not_resources=None,
                        principals=[
                            aws_iam.ArnPrincipal("*")
                        ],
                        resources=["*"]
                    ),
                ]
            )
        )


        # Bucket
        self.s3_bucket['sample'] = aws_s3.Bucket(self, "bucket-sample",
            bucket_name="useast1-sample-bucket-as1nkaozosw",
            access_control=aws_s3.BucketAccessControl.PRIVATE,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True),
            public_read_access=False,
            encryption=aws_s3.BucketEncryption.KMS,
            encryption_key=self.kms_key['s3-bucket'],
            bucket_key_enabled=False,
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
            removal_policy=core.RemovalPolicy.DESTROY,
            auto_delete_objects=False,
        )

        # Bucket policy for vpc_endpoint 
        # self.s3_bucket['sample'].add_to_resource_policy(
        #     permission=aws_iam.PolicyStatement(
        #         sid="Access-to-specific-VPCE-only",
        #         effect=aws_iam.Effect.DENY,
        #         actions=[
        #             "s3:*"
        #         ],
        #         principals=[
        #             aws_iam.ArnPrincipal("*")
        #         ],
        #         resources=[
        #             f"{self.s3_bucket['sample'].bucket_arn}",
        #             f"{self.s3_bucket['sample'].bucket_arn}/*"
        #         ],
        #         conditions={
        #             "StringNotEquals": {
        #                 "aws:SourceVpce": "vpce-1a2b3c4d"
        #             }
        #         },
        #         not_actions=None,
        #         not_principals=None,
        #         not_resources=None,
        #     )
        # )