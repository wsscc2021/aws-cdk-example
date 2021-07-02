'''
    Dependency: vpc, security-group
'''
from aws_cdk import (
    core, aws_ec2, aws_iam, aws_kms, aws_efs
)

class EfsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, security_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Init
        self.vpc = vpc
        self.project = project
        self.security_group = security_group
        self.role = dict()
        self.kms_key = dict()

        # kms
        self.kms_key['efs'] = aws_kms.Key(self, "efs_cmk",
            alias               = f"alias/{project['prefix']}-efs",
            description         = "",
            admins              = None,
            enabled             = True,
            enable_key_rotation = True,
            pending_window      = core.Duration.days(7),
            removal_policy      = core.RemovalPolicy.DESTROY,
            policy              = None
        )

        # efs
        aws_efs.FileSystem(self, "efs",
            vpc=self.vpc,
            file_system_name=f"{self.project['prefix']}-efs",
            enable_automatic_backups=True,
            encrypted=True,
            kms_key=self.kms_key['efs'],
            lifecycle_policy=aws_efs.LifecyclePolicy.AFTER_30_DAYS,
            performance_mode=aws_efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=aws_efs.ThroughputMode.BURSTING,
            provisioned_throughput_per_second=None,
            removal_policy=core.RemovalPolicy.DESTROY,
            security_group=self.security_group['efs'],
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.ISOLATED)
        )