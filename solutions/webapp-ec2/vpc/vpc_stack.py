from aws_cdk import (
    core, aws_ec2
)

class VpcStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = aws_ec2.Vpc(self, "vpc",
            cidr="10.0.0.0/16",
            max_azs=3,
            nat_gateways=3,
            # nat_gateway_provider=ec2.NatProvider.gateway(),
            # configuration will create 3 groups in 3 AZs = 9 subnets.
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=20
                ), aws_ec2.SubnetConfiguration(
                    subnet_type=aws_ec2.SubnetType.PRIVATE,
                    name="Private",
                    cidr_mask=20
                ), aws_ec2.SubnetConfiguration(
                    subnet_type=aws_ec2.SubnetType.ISOLATED,
                    name="Data",
                    cidr_mask=20
                )
            ]
        )

        self.vpc.add_flow_log(id=f"{project['prefix']}-vpc-flow-log")