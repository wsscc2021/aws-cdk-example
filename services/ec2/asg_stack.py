'''
    Dependency: vpc, security_group, elb
'''
from aws_cdk import (
    core, aws_iam, aws_ec2, aws_autoscaling
)

class AutoScalingGroupStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, security_group, target_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Initial
        self.project        = project
        self.vpc            = vpc
        self.security_group = security_group
        self.target_group   = target_group
        self.create_security_group() # 원래는 security-group stack에서 생성함

        # Create Role
        self.role = dict()
        self.role['foo-app'] = aws_iam.Role(self, "role-foo-app",
            role_name   = f"{self.project['prefix']}-role-foo-app",
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
        # ami = aws_ec2.MachineImage.genericLinux({
        #     'us-east-1': 'ami-97785bed',
        #     'eu-west-1': 'ami-12345678',
        #     })

        # Auto Scaling Group
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_autoscaling/AutoScalingGroup.html
        aws_autoscaling.AutoScalingGroup(self, "asg-foo-app",
            auto_scaling_group_name=f"{self.project['prefix']}-asg-foo-app",
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
            user_data=None,
            # asg options
            desired_capacity=2,
            min_capacity=2,
            max_capacity=20,
            health_check=aws_autoscaling.HealthCheck.elb(grace=core.Duration.seconds(120)),
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
        ).attach_to_application_target_group(
            target_group=self.target_group['foo-app']
        )


    def create_security_group(self):
        # 원래는 security group stack에서 별도로 생성해줍시다!
        self.security_group['foo-app'] = aws_ec2.SecurityGroup(self, 'sg-foo-app',
            vpc                 = self.vpc,
            security_group_name = f"{self.project['prefix']}-sg-foo-app",
            description         = "",
            allow_all_outbound  = True)
        core.Tags.of(self.security_group['foo-app']).add(
            "Name",
            f"{self.project['prefix']}-sg-foo-app")