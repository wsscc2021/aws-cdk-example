'''
    security group은 VPC에 의존성이 있습니다.
    security group stack을 생성하기에 앞서 VPC stack을 생성하고, vpc를 argument로 넣어야합니다.
    
    security_group_stack = SecurityGroupStack(
        scope        = app,
        construct_id = f"{project['prefix']}-security-group",
        project      = project,
        vpc          = vpc_stack.vpc,
        env          = cdk_environment)
'''
from aws_cdk import (
    core, aws_ec2
)

class SecurityGroupStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Init
        self.vpc = vpc
        self.project = project
        self.security_group = dict()

        # Security Group
        self.add_security_group(
            name = "ext-alb",
            description = "",
            allow_all_outbound = False)
        self.add_security_group(
            name = "app",
            description = "",
            allow_all_outbound = True)
        
        '''
            Security Group Rules
            1. Ingress
            1-1. TCP, Chained Security Group
            1-2. All Traffic, IPv4 CIDR
            2. Egress
            2-1. TCP, Chained Security Group
            2-2. All Traffic, IPv4 CIDR for Specific address
        '''
        self.security_group['ext-alb'].add_ingress_rule(
            peer = aws_ec2.Peer.ipv4('0.0.0.0/0'),
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="1", # Unique value
                from_port=80,
                to_port=80),
            description = "")
        self.security_group['ext-alb'].add_egress_rule(
            peer = self.security_group['app'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="2", # Unique value
                from_port=80,
                to_port=80),
            description = "")

        self.security_group['app'].add_ingress_rule(
            peer = self.security_group['ext-alb'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="1", # Unique value
                from_port=80,
                to_port=80),
            description = "")
        
        

    '''
        Security Group에 태그를 쉽게 붙이기 위해서 함수로 생성합니다.
    '''
    def add_security_group(self, name: str, description: str, allow_all_outbound: bool):
        self.security_group[name] = aws_ec2.SecurityGroup(self, name,
            vpc                 = self.vpc,
            security_group_name = f"{self.project['prefix']}-sg-{name}",
            description         = description,
            allow_all_outbound  = allow_all_outbound)
        core.Tags.of(self.security_group[name]).add(
            "Name",
            f"{self.project['prefix']}-sg-{name}")