from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    aws_elasticloadbalancingv2,
)

class ElasticLoadBalancerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, subnets, security_groups, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # init
        self.target_groups = dict()
        self.elb = dict()

        # resources
        self.application_load_balancer(vpc, subnets, security_groups)
        self.network_load_balancer(vpc, subnets)

    
    def application_load_balancer(self, vpc, subnets, security_groups):
        # Target Groups
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/CfnTargetGroup.html
        self.target_groups["product-api-ext"] = aws_elasticloadbalancingv2.CfnTargetGroup(self, "tg-product-api-ext",
            # application load balancer target group
            # 
            health_check_enabled=True,
            health_check_interval_seconds=10,
            health_check_path="/health",
            health_check_port="traffic-port", # traffic-port, 8080, 80 ...
            health_check_protocol="HTTP", # TCP, HTTP, HTTPS
            health_check_timeout_seconds=5,
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
            ip_address_type="ipv4", # ipv4, ipv6
            name="product-api-ext-tg",
            port=8080,
            protocol="HTTP", # HTTP, HTTPS
            protocol_version="HTTP1", # GRPC, HTTP1, HTTP2
            tags=[
                CfnTag(
                    key="Name",
                    value="product-api-ext-tg"
                )
            ],
            target_group_attributes=[
                aws_elasticloadbalancingv2.CfnTargetGroup.TargetGroupAttributeProperty(
                    key="deregistration_delay.timeout_seconds",
                    value="30"),
            ],
            targets=None,
            target_type="instance", # instance, ip, lambda
            vpc_id=vpc.ref)
        
        # load balancer
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/CfnLoadBalancer.html
        self.elb["product-ext"] = aws_elasticloadbalancingv2.CfnLoadBalancer(self, "elb-product-ext",
            type="application", # application, network, gateway
            scheme="internet-facing", # internal, internet-facing
            ip_address_type="ipv4", # ipv4 , dualstack
            load_balancer_attributes=[
                aws_elasticloadbalancingv2.CfnLoadBalancer.LoadBalancerAttributeProperty(
                    key="deletion_protection.enabled",
                    value="false"),
                aws_elasticloadbalancingv2.CfnLoadBalancer.LoadBalancerAttributeProperty(
                    key="routing.http2.enabled",
                    value="true"),
            ],
            name="product-ext",
            security_groups=[
                security_groups["product-ext"].ref,
            ],
            subnets=[
                subnets["public-a"].ref,
                subnets["public-b"].ref,
            ],
            tags=[
                CfnTag(
                    key="Name",
                    value="product-ext"
                )
            ],)
        
        # listener
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/CfnListener.html
        listners = dict()
        listners["product-ext-http"] = aws_elasticloadbalancingv2.CfnListener(self, "listener-product-ext-http",
            # application load balancer listener
            #
            default_actions=[
                aws_elasticloadbalancingv2.CfnListener.ActionProperty(
                    type="fixed-response", # forward, redirect, fixed-response
                    fixed_response_config=aws_elasticloadbalancingv2.CfnListener.FixedResponseConfigProperty(
                        status_code="404",
                        content_type="text/plain",
                        message_body="404 Not Found"),
                    order=1,),
            ],
            load_balancer_arn=self.elb["product-ext"].ref,
            certificates=None,
            ssl_policy=None,
            protocol="HTTP", # HTTP, HTTPS
            port=80,)

        # application load balancer additional rule
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/CfnListenerRule.html
        aws_elasticloadbalancingv2.CfnListenerRule(self, "listener-rule-product-ext-http-r1",
            actions=[
                aws_elasticloadbalancingv2.CfnListenerRule.ActionProperty(
                    type="forward", # forward, redirect, fixed-response
                    forward_config=aws_elasticloadbalancingv2.CfnListenerRule.ForwardConfigProperty(
                        target_groups=[
                            aws_elasticloadbalancingv2.CfnListenerRule.TargetGroupTupleProperty(
                                target_group_arn=self.target_groups["product-api-ext"].ref,
                                weight=100)
                        ],),
                    order=1,),
            ],
            conditions=[
                aws_elasticloadbalancingv2.CfnListenerRule.RuleConditionProperty(
                    # http-header, http-request-method, host-header, 
                    # path-pattern, query-string, source-ip
                    field="path-pattern",
                    host_header_config=None,
                    http_header_config=None,
                    http_request_method_config=None,
                    path_pattern_config=aws_elasticloadbalancingv2.CfnListenerRule.PathPatternConfigProperty(
                        values=[
                            "/health",
                            "/region",
                            "/v1/product",
                        ]),
                    query_string_config=None,
                    source_ip_config=None,
                    values=None),
            ],
            listener_arn=listners["product-ext-http"].ref,
            priority=10)

    def network_load_balancer(self, vpc, subnets):
        # Target Groups
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/CfnTargetGroup.html
        self.target_groups["product-api-int"] = aws_elasticloadbalancingv2.CfnTargetGroup(self, "tg-product-api-int",
            # netwrok load balancer target group
            # 
            health_check_enabled=True,
            health_check_interval_seconds=10, # 10, 30
            health_check_path="/health",
            health_check_port="traffic-port", # traffic-port, 8080, 80 ...
            health_check_protocol="HTTP", # TCP, HTTP, HTTPS
            health_check_timeout_seconds=None, # TCP Targetgroup can not support
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
            ip_address_type="ipv4", # ipv4, ipv6
            name="product-api-int-tg",
            port=8080,
            protocol="TCP", # TCP, TLS, UDP, TCP_UDP
            protocol_version=None, # only HTTP, HTTPS
            tags=[
                CfnTag(
                    key="Name",
                    value="product-api-int-tg"
                )
            ],
            target_group_attributes=[
                aws_elasticloadbalancingv2.CfnTargetGroup.TargetGroupAttributeProperty(
                    key="deregistration_delay.timeout_seconds",
                    value="30"),
                aws_elasticloadbalancingv2.CfnTargetGroup.TargetGroupAttributeProperty(
                    key="deregistration_delay.connection_termination.enabled",
                    value="true"),
            ],
            targets=None,
            target_type="instance", # instance, ip, lambda
            vpc_id=vpc.ref)

        # load balancer
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/CfnLoadBalancer.html
        self.elb["product-int"] = aws_elasticloadbalancingv2.CfnLoadBalancer(self, "elb-product-int",
            type="network", # application, network, gateway
            scheme="internal", # internal, internet-facing
            ip_address_type="ipv4", # ipv4 , dualstack
            load_balancer_attributes=[
                aws_elasticloadbalancingv2.CfnLoadBalancer.LoadBalancerAttributeProperty(
                    key="deletion_protection.enabled",
                    value="false"),
                aws_elasticloadbalancingv2.CfnLoadBalancer.LoadBalancerAttributeProperty(
                    key="load_balancing.cross_zone.enabled",
                    value="false"),
            ],
            name="product-int",
            security_groups=None, # only ALB
            subnets=[
                subnets["private-a"].ref,
                subnets["private-b"].ref,
            ],
            tags=[
                CfnTag(
                    key="Name",
                    value="product-int"
                )
            ],)
        
        # listener
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/CfnListener.html
        listners = dict()
        listners["product-int-http"] = aws_elasticloadbalancingv2.CfnListener(self, "listener-product-int-http",
            # network load balancer listener
            #
            default_actions=[
                aws_elasticloadbalancingv2.CfnListener.ActionProperty(
                    type="forward", # forward
                    forward_config = aws_elasticloadbalancingv2.CfnListener.ForwardConfigProperty(
                        target_groups=[
                            aws_elasticloadbalancingv2.CfnListener.TargetGroupTupleProperty(
                                target_group_arn=self.target_groups["product-api-int"].ref,),
                        ],
                        target_group_stickiness_config=None),
                    order=1,),
            ],
            load_balancer_arn=self.elb["product-int"].ref,
            certificates=None,
            ssl_policy=None,
            protocol="TCP", # TCP, TLS, UDP, TCP_UDP
            port=80,)
        
        