'''
    Dependency: vpc, security_group
    긁적;; Launch_Template을 쓸떄가 없다니... 일단 저장해두니 나중에 쓸일 있으면 쓰세요~
'''
from aws_cdk import (
    core, aws_iam, aws_ec2
)

class LaunchTemplateStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, security_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Initial
        self.project        = project
        self.vpc            = vpc
        self.security_group = security_group

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

        # read user-data
        # with open("./ec2/userdata.sh") as f:
        #     userdata = f.read()

        # LaunchTemplate
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/LaunchTemplate.html
        self.launch_template = dict()
        self.launch_template['foo-app'] = aws_ec2.LaunchTemplate(self, "lt-foo-app",
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
            cpu_credits=None,
            detailed_monitoring=None,
            disable_api_termination=None,
            ebs_optimized=None,
            hibernation_configured=None,
            instance_initiated_shutdown_behavior=None,
            instance_type=aws_ec2.InstanceType("t3.xlarge"),
            key_name=self.project['keypair'],
            launch_template_name=f"{self.project['prefix']}-lt-foo-app",
            machine_image=ami,
            nitro_enclave_enabled=None,
            role=self.role['foo-app'],
            security_group=self.security_group['foo-app'],
            spot_options=None,
            # user_data=aws_ec2.UserData.custom(userdata),
            user_data=None)