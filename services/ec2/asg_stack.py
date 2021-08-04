'''
    Dependency: vpc, security_group, elb
'''
from constructs import Construct
from aws_cdk import Stack, Duration, Tags, aws_iam, aws_ec2, aws_autoscaling

class AutoScalingGroupStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, vpc, security_group, target_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Init
        self.project        = project
        self.vpc            = vpc
        self.security_group = security_group
        self.target_group   = target_group
        self.create_security_group() # Demostration code, Recommend create from security_group stack
        # IAM role
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/Role.html
        self.role = dict()
        self.role['foo-app'] = aws_iam.Role(self, "foo-app-role",
            role_name   = f"{self.project['prefix']}-foo-app-role",
            description = "",
            assumed_by  = aws_iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM")
            ])
        # AMI
        # https://github.com/aws/aws-cdk/blob/master/packages/%40aws-cdk/aws-ec2/test/example.images.lit.ts
        ami = aws_ec2.MachineImage.latest_amazon_linux(
            generation=aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=aws_ec2.AmazonLinuxEdition.STANDARD,
            virtualization=aws_ec2.AmazonLinuxVirt.HVM,
            storage=aws_ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            cpu_type=aws_ec2.AmazonLinuxCpuType.X86_64)
        # ami = aws_ec2.MachineImage.from_ssm_parameter("/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2")
        # ami = aws_ec2.MachineImage.generic_linux(
        #     ami_map={
        #         'us-east-1': 'ami-97785bed',
        #         'eu-west-1': 'ami-12345678',
        #     })
        # user-data
        with open("./ec2/userdata.sh") as f:
            userdata = f.read()
        # Auto Scaling Group
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_autoscaling/AutoScalingGroup.html
        aws_autoscaling.AutoScalingGroup(self, "foo-app-asg",
            auto_scaling_group_name=f"{self.project['prefix']}-foo-app-asg",
            # tpye of instance
            instance_type=aws_ec2.InstanceType("t3.xlarge"),
            machine_image=ami,
            # network
            vpc=self.vpc,
            associate_public_ip_address=None,
            security_group=self.security_group['foo-app'],
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE),
            # advanced options
            key_name=self.project['keypair'],
            role=self.role['foo-app'],
            # ebs
            block_devices=[
                aws_autoscaling.BlockDevice(
                    device_name="/dev/xvda",
                    volume=aws_autoscaling.BlockDeviceVolume(
                        virtual_name=None,
                        ebs_device=aws_autoscaling.EbsDeviceProps(
                            delete_on_termination=True,
                            iops=None,
                            volume_type=aws_autoscaling.EbsDeviceVolumeType.GP2,
                            volume_size=20,
                            snapshot_id=None
                        )
                    )
                )
            ],
            # user-data
            user_data=aws_ec2.UserData.custom(userdata),
            # asg options
            desired_capacity=2,
            min_capacity=2,
            max_capacity=20,
            health_check=aws_autoscaling.HealthCheck.elb(grace=Duration.seconds(120)),
            cooldown=Duration.seconds(300),
            group_metrics=None,
            ignore_unmodified_size_properties=None,
            instance_monitoring=None,
            max_instance_lifetime=None,
            notifications=None,
            signals=None,
            spot_price=None,
            update_policy=None,
        ).attach_to_application_target_group(
            target_group=self.target_group['foo-app']
        )

    def create_security_group(self):
        # Demostration code, Recommend create from security_group stack.
        self.security_group['foo-app'] = aws_ec2.SecurityGroup(self, 'foo-app-sg',
            vpc                 = self.vpc,
            security_group_name = f"{self.project['prefix']}-foo-app-sg",
            description         = "",
            allow_all_outbound  = True)
        Tags.of(self.security_group['foo-app']).add(
            "Name",
            f"{self.project['prefix']}-foo-app-sg")