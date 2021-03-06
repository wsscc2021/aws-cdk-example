from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    Fn,
    aws_iam,
    aws_ec2,
    aws_autoscaling,
)

class AutoScalingGroupStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, subnets, 
                       security_groups, target_groups, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # IAM Role
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/CfnRole.html
        iam_roles = dict()
        iam_roles["product-api"] = aws_iam.CfnRole(self, "role-product-api",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "ec2.amazonaws.com"
                            ]
                        },
                        "Action": [
                            "sts:AssumeRole"
                        ]
                    }
                ]
            },
            description="description",
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
                "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
                "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
            ],
            max_session_duration=3600,
            path="/",
            permissions_boundary=None,
            policies=None,
            role_name="product-api-role",
            tags=[
                CfnTag(
                    key="Name",
                    value="product-api-role"
                )
            ])

        # instance profile
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/CfnInstanceProfile.html
        iam_instance_profile = dict()
        iam_instance_profile["product-api"] = aws_iam.CfnInstanceProfile(self,
            "instance-profile-product-api",
            roles=[
                iam_roles["product-api"].ref
            ],
            path="/")

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
        with open("./usdev/ec2/was_userdata.sh") as f:
            userdata = f.read()

        # Launch Template
        # https://docs.aws.amazon.com/cdk/pi/v2/python/aws_cdk.aws_ec2/CfnLaunchTemplate.html
        launch_templates = dict()
        launch_templates["product-api"] = aws_ec2.CfnLaunchTemplate(self, "lt-product-api",
            launch_template_name="product-api-lt",
            tag_specifications=[
                aws_ec2.CfnLaunchTemplate.LaunchTemplateTagSpecificationProperty(
                    resource_type="launch-template",
                    tags=[
                        CfnTag(
                            key="Name",
                            value="product-api-lt"
                        )
                    ]),
            ],
            launch_template_data=aws_ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                image_id=ami_id,
                instance_type="t3.small",
                ebs_optimized=None,
                block_device_mappings=[
                    aws_ec2.CfnLaunchTemplate.BlockDeviceMappingProperty(
                        device_name="/dev/xvda",
                        ebs=aws_ec2.CfnLaunchTemplate.EbsProperty(
                            volume_type="gp3", # gp2 , gp3 , io1 , io2
                            volume_size=30,
                            iops=3000,        # gp3 , io1 , io2
                            throughput=125,   # gp3 , io1 , io2
                            encrypted=True,
                            kms_key_id=None,
                            delete_on_termination=True,
                            snapshot_id=None,),),
                ],
                disable_api_termination=None,
                iam_instance_profile=aws_ec2.CfnLaunchTemplate.IamInstanceProfileProperty(
                    arn=iam_instance_profile["product-api"].attr_arn,),
                key_name="useast1-keypair",
                monitoring=None, # detail monitoring
                security_group_ids=[
                    security_groups["example"].ref,
                ],
                tag_specifications=[
                    aws_ec2.CfnLaunchTemplate.TagSpecificationProperty(
                        resource_type="instance",
                        tags=[
                            CfnTag(
                                key="Name",
                                value="product-api"
                            )
                        ]),
                    aws_ec2.CfnLaunchTemplate.TagSpecificationProperty(
                        resource_type="volume",
                        tags=[
                            CfnTag(
                                key="Name",
                                value="product-api"
                            )
                        ]),
                ],
                user_data=Fn.base64(userdata)),
        )

        # auto scaling group
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_autoscaling/CfnAutoScalingGroup.html
        aws_autoscaling.CfnAutoScalingGroup(self, "product-api-asg",
            auto_scaling_group_name="product-api-asg",
            min_size="2",
            max_size="20",
            capacity_rebalance=None, # spot
            cooldown="120", # default cool down time
            desired_capacity_type="units", # units , vcpu , memory-mib
            health_check_grace_period=60,
            health_check_type="ELB", # EC2 , ELB
            target_group_arns=[
                target_groups["product-api-ext"].ref,
                target_groups["product-api-int"].ref,
            ],
            launch_template=aws_autoscaling.CfnAutoScalingGroup.LaunchTemplateSpecificationProperty(
                version=Fn.get_att(
                    logical_name_of_resource=launch_templates["product-api"].logical_id,
                    attribute_name="LatestVersionNumber"
                ).to_string(),
                launch_template_id=launch_templates["product-api"].ref,),
            metrics_collection=None,
            mixed_instances_policy=None,
            new_instances_protected_from_scale_in=None,
            tags=[
                aws_autoscaling.CfnAutoScalingGroup.TagPropertyProperty(
                    propagate_at_launch=True,
                    key="Name",
                    value="product-api"),
            ],
            # OldestInstance , OldestLaunchConfiguration , NewestInstance , 
            # ClosestToNextInstanceHour , Default , OldestLaunchTemplate 
            termination_policies=[
                "Default",
            ],
            vpc_zone_identifier=[
                subnets["private-a"].ref,
                subnets["private-b"].ref,
            ])