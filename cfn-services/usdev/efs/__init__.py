from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    aws_ec2,
    aws_efs,
)

class EFSStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, security_groups, subnets, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # EFS - file system
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_efs/CfnFileSystem.html
        efs = aws_efs.CfnFileSystem(self, "efs",
            availability_zone_name=None, # if one-zone
            backup_policy=aws_efs.CfnFileSystem.BackupPolicyProperty(
                status="ENABLED"),
            bypass_policy_lockout_safety_check=None,
            encrypted=True,
            kms_key_id=None,
            file_system_policy=None,
            file_system_tags=[
                aws_efs.CfnFileSystem.ElasticFileSystemTagProperty(
                    key="Name",
                    value="usdev-efs")
            ],
            lifecycle_policies=[
                aws_efs.CfnFileSystem.LifecyclePolicyProperty(
                    transition_to_ia="AFTER_14_DAYS",
                    transition_to_primary_storage_class=None),
                aws_efs.CfnFileSystem.LifecyclePolicyProperty(
                    transition_to_ia=None,
                    transition_to_primary_storage_class="AFTER_1_ACCESS")
            ],
            performance_mode="generalPurpose", # generalPurpose , maxIO
            throughput_mode="bursting", # bursting , provisioned
            provisioned_throughput_in_mibps=None,
        )

        # EFS - mount target
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_efs/CfnMountTarget.html
        aws_efs.CfnMountTarget(self, "efs-mount-data-a",
            file_system_id=efs.attr_file_system_id,
            security_groups=[
                security_groups["example"].ref
            ],
            subnet_id=subnets['data-a'].ref,
            ip_address=None)

        aws_efs.CfnMountTarget(self, "efs-mount-data-b",
            file_system_id=efs.attr_file_system_id,
            security_groups=[
                security_groups["example"].ref
            ],
            subnet_id=subnets['data-b'].ref,
            ip_address=None)