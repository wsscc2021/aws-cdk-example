'''
    Dependency: vpc, security_group
'''
from aws_cdk import (
    core, aws_cloudfront, aws_cloudfront_origins, aws_certificatemanager
)

class CloudFrontStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, elb, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # initial
        self.project = project
        
        # cache policy
        cache_policy = aws_cloudfront.CachePolicy(self, "cloudfront-cache-policy",
            cache_policy_name="cloudfront-cache-policy",
            comment="",
            cookie_behavior=aws_cloudfront.CacheCookieBehavior.none(),
            header_behavior=aws_cloudfront.CacheHeaderBehavior.none(),
            query_string_behavior=aws_cloudfront.CacheQueryStringBehavior.all(),
            default_ttl=None,
            max_ttl=None,
            min_ttl=None,
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True)

        # origin request policy
        origin_request_policy = aws_cloudfront.OriginRequestPolicy(self, "cloudfront-origin-request-policy",
            origin_request_policy_name="cloudfront-origin-request-policy",
            comment="",
            cookie_behavior=aws_cloudfront.OriginRequestCookieBehavior.none(),
            header_behavior=aws_cloudfront.OriginRequestHeaderBehavior.none(),
            query_string_behavior=aws_cloudfront.OriginRequestQueryStringBehavior.all())

        # distribution
        aws_cloudfront.Distribution(self, "cloudfront",
            default_behavior=aws_cloudfront.BehaviorOptions(
                origin=aws_cloudfront_origins.LoadBalancerV2Origin(
                    load_balancer=elb['ext-alb'],
                    origin_path=None,
                    http_port=80,
                    https_port=443,
                    connection_attempts=None,
                    connection_timeout=None,
                    read_timeout=None,
                    keepalive_timeout=None,
                    origin_ssl_protocols=None,
                    protocol_policy=aws_cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                    custom_headers=None),
                allowed_methods=aws_cloudfront.AllowedMethods.ALLOW_ALL,
                cached_methods=aws_cloudfront.CachedMethods.CACHE_GET_HEAD,
                viewer_protocol_policy=aws_cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cache_policy,
                origin_request_policy=origin_request_policy,
                smooth_streaming=None,
                compress=True,
                trusted_key_groups=None,
                edge_lambdas=None),
            additional_behaviors=None,
            enabled=True,
            enable_ipv6=True,
            http_version=aws_cloudfront.HttpVersion.HTTP2,
            price_class=aws_cloudfront.PriceClass.PRICE_CLASS_ALL,
            # certificate=aws_certificatemanager.Certificate.from_certificate_arn(self, "certificate",
            #     certificate_arn="arn:aws:acm:us-east-1:242593025403:certificate/099e74ff-1a17-4b79-b1bc-6b3fe2c85dfd"),
            certificate=None,
            # domain_names=["color.skill53.cloud"],
            domain_names=None,
            web_acl_id=None,
            default_root_object=None,
            error_responses=None,
            geo_restriction=None,
            comment=None,
            enable_logging=None,
            log_bucket=None,
            log_file_prefix=None,
            log_includes_cookies=None,
            minimum_protocol_version=None)