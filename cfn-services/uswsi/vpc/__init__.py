
from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    aws_ec2
)

class VPCStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # vpc
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnVPC.html
        self.vpc = aws_ec2.CfnVPC(self, "vpc",
            cidr_block="10.30.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            instance_tenancy="default", # "default", "dedicated"
            tags=[
                CfnTag(
                    key="Name",
                    value="USWSI"
                )
            ])

        # subnet
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSubnet.html
        self.subnets = dict()
        self.subnets['public-a'] = aws_ec2.CfnSubnet(self, "subnet-public-a",
            vpc_id=self.vpc.ref,
            cidr_block="10.30.1.0/24",
            availability_zone="us-east-1a",
            map_public_ip_on_launch=True,
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-pub-a"
                )
            ])
        self.subnets['public-b'] = aws_ec2.CfnSubnet(self, "subnet-public-b",
            vpc_id=self.vpc.ref,
            cidr_block="10.30.2.0/24",
            availability_zone="us-east-1b",
            map_public_ip_on_launch=True,
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-pub-b"
                )
            ])
        self.subnets['private-a'] = aws_ec2.CfnSubnet(self, "subnet-private-a",
            vpc_id=self.vpc.ref,
            cidr_block="10.30.11.0/24",
            availability_zone="us-east-1a",
            map_public_ip_on_launch=False,
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-priv-a"
                )
            ])
        self.subnets['private-b'] = aws_ec2.CfnSubnet(self, "subnet-private-b",
            vpc_id=self.vpc.ref,
            cidr_block="10.30.12.0/24",
            availability_zone="us-east-1b",
            map_public_ip_on_launch=False,
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-priv-b"
                )
            ])
        
        # internet gateway
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnInternetGateway.html
        internet_gateway = aws_ec2.CfnInternetGateway(self, "InternetGateway",
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-igw"
                )
            ])
        aws_ec2.CfnVPCGatewayAttachment(self, "InternetGatewayAttachment",
            vpc_id=self.vpc.ref,
            internet_gateway_id=internet_gateway.ref)
        
        # eip
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnEIP.html
        eip = dict()
        eip['natgw-a'] = aws_ec2.CfnEIP(self, "EipNatGatewayA",
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-natgw-a-eip"
                )
            ])
        eip['natgw-b'] = aws_ec2.CfnEIP(self, "EipNatGatewayB",
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-natgw-b-eip"
                )
            ])

        # nat gateway
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnNatGateway.html
        nat_gateways = dict()
        nat_gateways['public-a'] = aws_ec2.CfnNatGateway(self, "NatGatewayA",
            subnet_id=self.subnets['public-a'].ref,
            allocation_id=eip['natgw-a'].attr_allocation_id,
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-natgw-a"
                )
            ])
        nat_gateways['public-b'] = aws_ec2.CfnNatGateway(self, "NatGatewayB",
            subnet_id=self.subnets['public-b'].ref,
            allocation_id=eip['natgw-b'].attr_allocation_id,
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-natgw-b"
                )
            ])

        # route table
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnRouteTable.html
        self.route_tables = dict()
        self.route_tables['public'] = aws_ec2.CfnRouteTable(self, "RoutTablePublic",
            vpc_id=self.vpc.ref,
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-pub-rt"
                )
            ])
        self.route_tables['private-a'] = aws_ec2.CfnRouteTable(self, "RoutTablePrivateA",
            vpc_id=self.vpc.ref,
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-priv-a-rt"
                )
            ])
        self.route_tables['private-b'] = aws_ec2.CfnRouteTable(self, "RoutTablePrivateB",
            vpc_id=self.vpc.ref,
            tags=[
                CfnTag(
                    key="Name",
                    value="uswsi-priv-b-rt"
                )
            ])
        
        # route
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnRoute.html
        routes = [
            aws_ec2.CfnRoute(self, "RouteDefaultPublic",
                route_table_id=self.route_tables['public'].ref,
                destination_cidr_block="0.0.0.0/0",
                gateway_id=internet_gateway.ref
            ),
            aws_ec2.CfnRoute(self, "RouteDefaultPrivateA",
                route_table_id=self.route_tables["private-a"].ref,
                destination_cidr_block="0.0.0.0/0",
                nat_gateway_id=nat_gateways["public-a"].ref
            ),
            aws_ec2.CfnRoute(self, "RouteDefaultPrivateB",
                route_table_id=self.route_tables["private-b"].ref,
                destination_cidr_block="0.0.0.0/0",
                nat_gateway_id=nat_gateways["public-b"].ref
            ),
        ]
        
        # subnet route table association
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSubnetRouteTableAssociation.html
        subnet_route_table_associations = [
            aws_ec2.CfnSubnetRouteTableAssociation(self,
                "SubnetRouteTableAssociationPublicA",
                route_table_id=self.route_tables["public"].ref,
                subnet_id=self.subnets["public-a"].ref
            ),
            aws_ec2.CfnSubnetRouteTableAssociation(self,
                "SubnetRouteTableAssociationPublicB",
                route_table_id=self.route_tables["public"].ref,
                subnet_id=self.subnets["public-b"].ref
            ),
            aws_ec2.CfnSubnetRouteTableAssociation(self,
                "SubnetRouteTableAssociationPrivateA",
                route_table_id=self.route_tables["private-a"].ref,
                subnet_id=self.subnets["private-a"].ref
            ),
            aws_ec2.CfnSubnetRouteTableAssociation(self,
                "SubnetRouteTableAssociationPrivateB",
                route_table_id=self.route_tables["private-b"].ref,
                subnet_id=self.subnets["private-b"].ref
            ),
        ]
        