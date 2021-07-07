'''
    Dependency: vpc, security_group, elb
'''
from aws_cdk import (
    core, aws_iam, aws_ec2, aws_kms, aws_autoscaling
)

class AutoScalingGroupStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, security_group, target_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Initial
        self.project        = project
        self.vpc            = vpc
        self.security_group = security_group
        self.target_group   = target_group

        self.add_role()
        self.add_cmk()
        self.add_asg()
        self.attach_target_group()

    def add_role(self):
        # Create Role
        self.role = dict()
        self.role['app'] = aws_iam.Role(self, "role-app",
            role_name   = f"{self.project['prefix']}-role-app",
            description = "",
            assumed_by  = aws_iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM")
            ],
            inline_policies={
                "s3-useast1-artifact-read-only": aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            sid="AllowObjectInBucket",
                            effect=aws_iam.Effect.ALLOW,
                            actions=[
                                "s3:ListBucket"
                            ],
                            resources=[
                                "arn:aws:s3:::useast1-artifact"
                            ]
                            # principals=None,
                            # conditions=None
                        ),
                        aws_iam.PolicyStatement(
                            sid="AllObjectActions",
                            effect=aws_iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject"
                            ],
                            resources=[
                                "arn:aws:s3:::useast1-artifact/*"
                            ]
                            # principals=None,
                            # conditions=None
                        ),
                    ]
                )
            })

    def add_cmk(self):
        self.kms_key = dict()
        self.kms_key['ebs'] = aws_kms.Key(self, "ebs_cmk",
            alias               = f"alias/{self.project['prefix']}-ebs",
            description         = "",
            admins              = None,
            enabled             = True,
            enable_key_rotation = True,
            pending_window      = core.Duration.days(7),
            removal_policy      = core.RemovalPolicy.DESTROY,
            policy              = aws_iam.PolicyDocument(
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
                        sid="Enable AutoScalingGroup Permission",
                        actions=[
                            "kms:Encrypt",
                            "kms:Decrypt",
                            "kms:ReEncrypt*",
                            "kms:GenerateDataKey*",
                            "kms:DescribeKey"
                        ],
                        conditions=None,
                        effect=aws_iam.Effect.ALLOW,
                        not_actions=None,
                        not_principals=None,
                        not_resources=None,
                        principals=[
                            aws_iam.ArnPrincipal(arn="arn:aws:iam::242593025403:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"),
                        ],
                        resources=["*"]
                    ),
                    aws_iam.PolicyStatement(
                        sid="Enable AutoScalingGroup Permission",
                        actions=[
                            "kms:CreateGrant",
                            "kms:ListGrants",
                            "kms:RevokeGrant"
                        ],
                        conditions={
                            "Bool": {
                                "kms:GrantIsForAWSResource": "true"
                            }
                        },
                        effect=aws_iam.Effect.ALLOW,
                        not_actions=None,
                        not_principals=None,
                        not_resources=None,
                        principals=[
                            aws_iam.ArnPrincipal(arn="arn:aws:iam::242593025403:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"),
                        ],
                        resources=["*"]
                    ),
                ]
            )
        )

    def add_asg(self):
        # AMI
        # https://github.com/aws/aws-cdk/blob/master/packages/%40aws-cdk/aws-ec2/test/example.images.lit.ts
        # ami = aws_ec2.MachineImage.latest_amazon_linux(
        #     generation=aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
        #     edition=aws_ec2.AmazonLinuxEdition.STANDARD,
        #     virtualization=aws_ec2.AmazonLinuxVirt.HVM,
        #     storage=aws_ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        #     cpu_type=aws_ec2.AmazonLinuxCpuType.X86_64)
        # ami = aws_ec2.MachineImage.from_ssm_parameter("/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2")
        ami = aws_ec2.MachineImage.generic_linux(
            ami_map={
                'us-east-1': 'ami-0f7275afc60d2bb3d'
            })

        # read user-data
        with open("./ec2/userdata.sh") as f:
            userdata = f.read()

        # Auto Scaling Group
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_autoscaling/AutoScalingGroup.html
        self.auto_scaling_group = aws_autoscaling.AutoScalingGroup(self, "asg-app",
            auto_scaling_group_name=f"{self.project['prefix']}-asg-app",
            # tpye of instance
            instance_type=aws_ec2.InstanceType("t3.xlarge"),
            machine_image=ami,
            # network
            vpc=self.vpc,
            associate_public_ip_address=None,
            security_group=self.security_group['app'],
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE),
            # advanced options
            key_name=self.project['keypair'],
            role=self.role['app'],
            # ebs
            block_devices=None,
            # user-data
            user_data=None,
            # user_data=aws_ec2.UserData.custom(userdata),
            # asg options
            desired_capacity=2,
            min_capacity=2,
            max_capacity=20,
            # health_check=aws_autoscaling.HealthCheck.ec2(grace=core.Duration.seconds(180)),
            health_check=aws_autoscaling.HealthCheck.elb(grace=core.Duration.seconds(180)),
            cooldown=core.Duration.seconds(300),
            group_metrics=None,
            ignore_unmodified_size_properties=None,
            instance_monitoring=None,
            max_instance_lifetime=None,
            notifications=None,
            notifications_topic=None,
            replacing_update_min_successful_instances_percent=None,
            resource_signal_count=None,
            resource_signal_timeout=None,
            rolling_update_configuration=None,
            signals=None,
            spot_price=None,
            update_policy=None,
            update_type=None,
        )
    
    def attach_target_group(self):
        self.auto_scaling_group.attach_to_application_target_group(
            target_group=self.target_group['app']
        )