'''
    VPC와 Security Group에 의존적이다.
    Instance profile은 해당 스택 내부에서 별도로 만들어주는 게 좋다
'''
from aws_cdk import (
    core, aws_iam, aws_ec2
)

class EC2InstanceStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, security_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Initial
        self.project        = project
        self.vpc            = vpc
        self.security_group = security_group
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

        # EC2 Instance
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Instance.html
        aws_ec2.Instance(self, "ec2-foo-app",
            instance_type=aws_ec2.InstanceType("t3.xlarge"),
            machine_image=ami,
            vpc=self.vpc,
            allow_all_outbound=None,
            availability_zone=None,
            block_devices=[
                aws_ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=aws_ec2.BlockDeviceVolume.ebs(
                        volume_type=aws_ec2.EbsDeviceVolumeType.GP3,
                        # iops=3000,
                        volume_size=20,
                        encrypted=True,
                        delete_on_termination=True,
                    )
                )
            ],
            init=None,
            init_options=None,
            instance_name=f"{self.project['prefix']}-ec2-foo-app",
            key_name=self.project['keypair'],
            private_ip_address=None,
            resource_signal_timeout=None,
            role=self.role['foo-app'],
            security_group=self.security_group['foo-app'],
            source_dest_check=None,
            user_data=None,
            user_data_causes_replacement=None,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE))


    def create_security_group(self):
        # 원래는 security group stack에서 별도로 생성해준다.
        # ㅇㅇ
        self.security_group['foo-app'] = aws_ec2.SecurityGroup(self, 'sg-foo-app',
            vpc                 = self.vpc,
            security_group_name = f"{self.project['prefix']}-sg-foo-app",
            description         = "",
            allow_all_outbound  = True)
        core.Tags.of(self.security_group['foo-app']).add(
            "Name",
            f"{self.project['prefix']}-sg-foo-app")