'''
    Dependency: vpc, security_group
'''
from constructs import Construct
from aws_cdk import Stack, Tags, aws_iam, aws_ec2

class EC2InstanceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, vpc, security_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Initial
        self.project        = project
        self.vpc            = vpc
        self.security_group = security_group
        self.create_security_group() # Demostration code, Recommend create from security-group stack
        # IAM role
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/Role.html
        self.role = dict()
        self.role['foo-app'] = aws_iam.Role(self, "foo-app-role",
            role_name   = f"{self.project['prefix']}-foo-app-role",
            description = "",
            assumed_by  = aws_iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM")
            ],
            inline_policies={
                "s3-read-only": aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            sid="AllowObjectInBucket",
                            effect=aws_iam.Effect.ALLOW,
                            actions=[
                                "s3:ListBucket"
                            ],
                            resources=[
                                "arn:aws:s3:::apnortheast2-application-artifact-z01k3m2oaks"
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
                                "arn:aws:s3:::apnortheast2-application-artifact-z01k3m2oaks/*"
                            ]
                            # principals=None,
                            # conditions=None
                        ),
                    ]
                )
            })
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
        # userdata
        # with open("./ec2/userdata.sh") as f:
        #     userdata = f.read()
        # EC2 Instance
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/Instance.html
        aws_ec2.Instance(self, "foo-app-ec2",
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
            instance_name=f"{self.project['prefix']}-foo-app-ec2",
            key_name=self.project['keypair'],
            private_ip_address=None,
            resource_signal_timeout=None,
            role=self.role['foo-app'],
            security_group=self.security_group['foo-app'],
            source_dest_check=None,
            user_data=None,
            # user_data=aws_ec2.UserData.custom(userdata),
            user_data_causes_replacement=None,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE))

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