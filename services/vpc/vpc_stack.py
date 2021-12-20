'''
    Dependency: None
'''
from constructs import Construct
from aws_cdk import Stack, aws_ec2

class VpcStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Vpc
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Vpc.html
        self.vpc = aws_ec2.Vpc(self, "vpc",
            cidr="10.0.0.0/16",
            max_azs=2,
            nat_gateways=2,
            # nat_gateway_provider=ec2.NatProvider.gateway(),
            # configuration will create 3 groups in 3 AZs = 9 subnets.
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=20
                ), aws_ec2.SubnetConfiguration(
                    subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT,
                    name="Private",
                    cidr_mask=20
                ), aws_ec2.SubnetConfiguration(
                    subnet_type=aws_ec2.SubnetType.PRIVATE_ISOLATED,
                    name="Data",
                    cidr_mask=20
                )
            ]
        )
        self.vpc.add_flow_log(id=f"{project['prefix']}-vpc-flow-log")
        self.add_vpc_endpoint()

    def add_vpc_endpoint(self):
        # Vpc endpoint(Gateway)
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/GatewayVpcEndpointAwsService.html
        aws_ec2.GatewayVpcEndpoint(self, "vpc-endpoint-s3-gateway",
            vpc=self.vpc,
            service=aws_ec2.GatewayVpcEndpointAwsService.S3,
            subnets=self.vpc.private_subnets)
        # Vpc endpoint(Interface)
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/InterfaceVpcEndpointAwsService.html
        aws_ec2.InterfaceVpcEndpoint(self, "vpc-endpoint-ssm-interface",
            vpc=self.vpc,
            service=aws_ec2.InterfaceVpcEndpointAwsService.SSM,
            lookup_supported_azs=None,
            open=None,
            private_dns_enabled=None,
            security_groups=None,
            subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT))