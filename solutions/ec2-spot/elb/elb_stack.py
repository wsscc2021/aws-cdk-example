'''
    Dependency: vpc, security_group
'''
from aws_cdk import (
    core, aws_ec2, aws_elasticloadbalancingv2
)

class ElasticLoadBalancerStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, security_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # initial
        self.project = project
        self.vpc = vpc
        self.security_group = security_group
        self.target_group = dict()
        self.elb = dict()

        # Target Group
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_elasticloadbalancingv2/TargetGroupBase.html
        self.target_group['app'] = aws_elasticloadbalancingv2.ApplicationTargetGroup(self, "tg-app",
            port=80,
            protocol=aws_elasticloadbalancingv2.ApplicationProtocol.HTTP,
            protocol_version=aws_elasticloadbalancingv2.ApplicationProtocolVersion.HTTP1,
            slow_start=core.Duration.seconds(30),
            stickiness_cookie_duration=None,
            stickiness_cookie_name=None,
            targets=None,
            deregistration_delay=core.Duration.seconds(60),
            health_check=aws_elasticloadbalancingv2.HealthCheck(
                enabled=True,
                healthy_grpc_codes=None,
                healthy_http_codes=None,
                healthy_threshold_count=2,
                unhealthy_threshold_count=2,
                interval=core.Duration.seconds(10),
                path="/",
                port="80",
                protocol=aws_elasticloadbalancingv2.Protocol.HTTP,
                timeout=core.Duration.seconds(5)),
            target_group_name=f"{self.project['prefix']}-tg-app",
            target_type=aws_elasticloadbalancingv2.TargetType.INSTANCE,
            vpc=self.vpc)
        
        # ALB
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_elasticloadbalancingv2/ApplicationLoadBalancer.html        
        self.elb['ext-alb'] = aws_elasticloadbalancingv2.ApplicationLoadBalancer(self, "ext-alb",
            http2_enabled=True,
            idle_timeout=None,
            ip_address_type=aws_elasticloadbalancingv2.IpAddressType.IPV4,
            security_group=self.security_group['ext-alb'],
            vpc=self.vpc,
            deletion_protection=None,
            internet_facing=True,
            load_balancer_name=f"{self.project['prefix']}-ext-alb",
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PUBLIC))
        self.elb['ext-alb'].add_listener("listener-ext-alb",
            certificate_arns=None,
            certificates=None,
            default_action=aws_elasticloadbalancingv2.ListenerAction.fixed_response(
                status_code=404,
                content_type="text/plain",
                message_body="Content not found"
            ),
            default_target_groups=None,
            open=None,
            port=80,
            protocol=None,
            ssl_policy=None
        ).add_action(
            "listner-ext-alb-action1",
            action=aws_elasticloadbalancingv2.ListenerAction.weighted_forward(
                target_groups=[
                    aws_elasticloadbalancingv2.WeightedTargetGroup(
                        target_group=self.target_group['app'],
                        weight=100)
                ]
            ),
            conditions=None,
            host_header=None,
            path_pattern=None,
            path_patterns=["/*"],
            priority=10
        )