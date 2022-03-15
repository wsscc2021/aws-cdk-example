import base64
from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    Fn,
    aws_ec2
)

class EC2InstanceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, subnets, security_groups, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Machine Image
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/MachineImage.html
        # ami = aws_ec2.MachineImage.from_ssm_parameter("/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2")
        # ami = aws_ec2.MachineImage.generic_linux(
        #     ami_map={
        #         'us-east-1': 'ami-97785bed',
        #         'eu-west-1': 'ami-12345678',
        #     })
        ami = aws_ec2.MachineImage.latest_amazon_linux(
            generation=aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=aws_ec2.AmazonLinuxEdition.STANDARD,
            virtualization=aws_ec2.AmazonLinuxVirt.HVM,
            storage=aws_ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            cpu_type=aws_ec2.AmazonLinuxCpuType.X86_64)
        ami_id = ami.get_image(self).image_id

        # userdata
        with open("./ec2/userdata.sh") as f:
            userdata = f.read()
        
        # instance
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnInstance.html
        self.instances = dict()
        self.instances["bastion"] = aws_ec2.CfnInstance(self, "ec2-bastion",
            image_id=ami_id, # AMI
            instance_type="t3.small", # Instance Type
            ebs_optimized=None, # EBS Optimized
            block_device_mappings=[ # can support root volume
                aws_ec2.CfnInstance.BlockDeviceMappingProperty(
                    device_name="/dev/xvda",
                    ebs=aws_ec2.CfnInstance.EbsProperty(
                        volume_type="gp3",
                        volume_size=30, 
                        iops=None,
                        delete_on_termination=True,
                        encrypted=True,
                        kms_key_id=None, # default is managed key
                        snapshot_id=None, # snapshot load
                    ),
                )
            ],
            iam_instance_profile=None, # IAM Instance profile
            subnet_id=subnets["public-a"].ref, # Subnet
            security_group_ids=[ # Security groups
                security_groups["bastion"].ref
            ],
            monitoring=None, # detailed monitoring
            network_interfaces=None, # ENI
            propagate_tags_to_volume_on_creation=True,
            source_dest_check=True,
            disable_api_termination=None,
            tags=[
                CfnTag(
                    key="Name",
                    value="bastion"
                )
            ],
            key_name="bastion-keypair", # key-pair
            user_data=Fn.base64(userdata),)