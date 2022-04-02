
from constructs import Construct
from aws_cdk import (
    CfnTag,
    Stack,
    aws_s3
)

class S3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 - Bucket
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_s3/CfnBucket.html
        aws_s3.CfnBucket(self, "s3-usdev-bucket",
            bucket_name="usdev-bucket",
            bucket_encryption=aws_s3.CfnBucket.BucketEncryptionProperty(
                server_side_encryption_configuration=[
                    aws_s3.CfnBucket.ServerSideEncryptionRuleProperty(
                        bucket_key_enabled=True,
                        server_side_encryption_by_default=aws_s3.CfnBucket.ServerSideEncryptionByDefaultProperty(
                            sse_algorithm="aws:kms", # aws:kms , AES256
                            kms_master_key_id=None)
                    )
                ]
            ),
            versioning_configuration=aws_s3.CfnBucket.VersioningConfigurationProperty(
                status="Enabled"),
            ownership_controls=aws_s3.CfnBucket.OwnershipControlsProperty(
                rules=[
                    aws_s3.CfnBucket.OwnershipControlsRuleProperty(
                        object_ownership="BucketOwnerEnforced"),
                ]
            ),
            public_access_block_configuration=aws_s3.CfnBucket.PublicAccessBlockConfigurationProperty(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            ),
            tags=[
                CfnTag(
                    key="key01",
                    value="value01"
                ),
            ],
        )