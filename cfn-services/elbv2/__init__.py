from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    aws_elasticloadbalancingv2,
)

class ElasticLoadBalancerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, subnets, security_groups, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Target Groups
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/CfnTargetGroup.html
        self.target_groups = dict()
        self.target_groups["product-api"] = aws_elasticloadbalancingv2.CfnTargetGroup(self, "tg-product-api",
            health_check_enabled=True,
            health_check_interval_seconds=15,
            health_check_path="/health",
            health_check_port="8080",
            health_check_protocol="HTTP", # TCP, HTTP, HTTPS
            health_check_timeout_seconds=5,
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
            ip_address_type="ipv4", # ipv4, ipv6
            name="product-api-tg",
            port=8080,
            protocol="HTTP", # HTTP, HTTPS
            protocol_version="HTTP1", # GRPC, HTTP1, HTTP2
            tags=[
                CfnTag(
                    key="Name",
                    value="product-api-tg"
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
        self.elb = dict()
        self.elb["product-ext"] = aws_elasticloadbalancingv2.CfnLoadBalancer(self, "elb-product-ext",
            type="application",
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
        
        # listener rule
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/CfnListenerRule.html
        aws_elasticloadbalancingv2.CfnListenerRule(self, "listener-rule-product-ext-http-r1",
            actions=[
                aws_elasticloadbalancingv2.CfnListenerRule.ActionProperty(
                    type="forward", # forward, redirect, fixed-response
                    forward_config=aws_elasticloadbalancingv2.CfnListenerRule.ForwardConfigProperty(
                        target_groups=[
                            aws_elasticloadbalancingv2.CfnListenerRule.TargetGroupTupleProperty(
                                target_group_arn=self.target_groups["product-api"].ref,
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