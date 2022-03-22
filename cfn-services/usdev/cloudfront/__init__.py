from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    aws_cloudfront,
)

class CloudfrontStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, elb, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # resources
        self.policy()
        self.distribution_elb(elb)
        self.distribution_s3()
        

    def policy(self):
        # cache policy
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/CfnCachePolicy.html
        self.cache_policy = aws_cloudfront.CfnCachePolicy(self, "cache-policy",
            cache_policy_config=aws_cloudfront.CfnCachePolicy.CachePolicyConfigProperty(
                name="custom-cache-policy",
                comment=None,
                default_ttl=86400, # default
                max_ttl=3153600, # default
                min_ttl=1, # default
                parameters_in_cache_key_and_forwarded_to_origin=aws_cloudfront.CfnCachePolicy.ParametersInCacheKeyAndForwardedToOriginProperty(
                    cookies_config=aws_cloudfront.CfnCachePolicy.CookiesConfigProperty(
                        cookie_behavior="none", # none, all, whitelist, allExcept
                        cookies=None, # list[str]
                    ), 
                    headers_config=aws_cloudfront.CfnCachePolicy.HeadersConfigProperty(
                        header_behavior="none", # none, whitelist
                        headers=None, # list[str]
                    ),
                    query_strings_config=aws_cloudfront.CfnCachePolicy.QueryStringsConfigProperty(
                        query_string_behavior="none", # none, all, whitelist, allExcept
                        query_strings=None, # list[str]
                    ),
                    enable_accept_encoding_gzip=True,
                    enable_accept_encoding_brotli=True
                ),
            )
        )

        # origin request policy
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/CfnOriginRequestPolicy.html
        self.origin_request_policy = aws_cloudfront.CfnOriginRequestPolicy(self, "origin-request-policy",
            origin_request_policy_config=aws_cloudfront.CfnOriginRequestPolicy.OriginRequestPolicyConfigProperty(
                name="custom-origin-request-policy",
                comment=None,
                cookies_config=aws_cloudfront.CfnOriginRequestPolicy.CookiesConfigProperty(
                    cookie_behavior="none", # none, all, whitelist
                    cookies=None, # list[str]
                ),
                headers_config=aws_cloudfront.CfnOriginRequestPolicy.HeadersConfigProperty(
                    header_behavior="none", # none, whitelist, allViewer, allViewerAndWhitelistCloudFront
                    headers=None
                ),
                query_strings_config=aws_cloudfront.CfnOriginRequestPolicy.QueryStringsConfigProperty(
                    query_string_behavior="none", # none, all, whitelist
                    query_strings=None
                ),
            )
        )
    
    
    def distribution_elb(self, elb):
        # Distribution
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/CfnDistribution.html
        aws_cloudfront.CfnDistribution(self, "cloudfront-distribution-elb",
            distribution_config=aws_cloudfront.CfnDistribution.DistributionConfigProperty(
                enabled=True,
                comment=None,
                origin_groups=None,
                origins=[
                    aws_cloudfront.CfnDistribution.OriginProperty(
                        id="OriginELB",
                        domain_name=elb["product-ext"].attr_dns_name,
                        connection_attempts=3, # 1 ~ 3
                        connection_timeout=10, # 1 ~ 10
                        custom_origin_config=aws_cloudfront.CfnDistribution.CustomOriginConfigProperty(
                            origin_protocol_policy="http-only", # http-only, https-only, match-viewer
                            http_port=80,
                            https_port=None,
                            origin_keepalive_timeout=5, # 1 ~ 60
                            origin_read_timeout=30, # 1 ~ 60
                            origin_ssl_protocols=None # list[str] ; SSLv3, TLSv1, TLSv1.1 TLSv1.2
                        ),
                        origin_custom_headers=[
                            aws_cloudfront.CfnDistribution.OriginCustomHeaderProperty(
                                header_name="X-custom-header",
                                header_value="value1402"),
                        ],
                        origin_path=None, # str
                        origin_shield=aws_cloudfront.CfnDistribution.OriginShieldProperty(
                            enabled=True,
                            origin_shield_region="us-east-1"
                        ),
                        s3_origin_config=None,
                    ),
                ],
                default_cache_behavior=aws_cloudfront.CfnDistribution.DefaultCacheBehaviorProperty(
                    target_origin_id="OriginELB",
                    viewer_protocol_policy="redirect-to-https", # allow-all, redirect-to-https, https-only
                    allowed_methods=[
                        "GET", "HEAD", "OPTIONS", "PUT", "PATCH", "POST", "DELETE"
                    ],
                    cached_methods=[
                        "GET", "HEAD", "OPTIONS"
                    ],
                    compress=True,
                    # managed cache policy id
                    # https://docs.aws.amazon.com/ko_kr/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html
                    # managed origin request policy id
                    # https://docs.aws.amazon.com/ko_kr/AmazonCloudFront/latest/DeveloperGuide/using-managed-origin-request-policies.html
                    cache_policy_id=self.cache_policy.ref,
                    origin_request_policy_id=self.origin_request_policy.ref,
                    response_headers_policy_id=None,
                    field_level_encryption_id=None,
                    function_associations=None,
                    lambda_function_associations=None,
                    realtime_log_config_arn=None,
                    smooth_streaming=None,
                    trusted_key_groups=None,
                    trusted_signers=None,
                ),
                cache_behaviors=None,
                cnam_es=None, # CNAMEs
                aliases=None, # CNAMEs (alternate domain names)
                default_root_object=None, # str
                http_version="http2", # http1.1 , http2
                ipv6_enabled=True,
                price_class="PriceClass_All", # PriceClass_All, PriceClass_100 , PriceClass_200
                logging=None,
            ),
            tags=None)
    

    def distribution_s3(self):
        # OAI
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/CfnCloudFrontOriginAccessIdentity.html
        oai = aws_cloudfront.CfnCloudFrontOriginAccessIdentity(self, "oai-us-static-contents-bucket.s3.us-east-1.amazonaws.com",
            cloud_front_origin_access_identity_config=aws_cloudfront.CfnCloudFrontOriginAccessIdentity.CloudFrontOriginAccessIdentityConfigProperty(
                comment="oai-us-static-contents-bucket.s3.us-east-1.amazonaws.com"))

        # Distribution
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/CfnDistribution.html
        aws_cloudfront.CfnDistribution(self, "cloudfront-distribution-s3",
            distribution_config=aws_cloudfront.CfnDistribution.DistributionConfigProperty(
                enabled=True,
                comment=None,
                origin_groups=None,
                origins=[
                    aws_cloudfront.CfnDistribution.OriginProperty(
                        id="OriginS3",
                        domain_name="us-static-contents-bucket.s3.us-east-1.amazonaws.com",
                        connection_attempts=3, # 1 ~ 3
                        connection_timeout=10, # 1 ~ 10
                        custom_origin_config=None,
                        origin_custom_headers=None,
                        origin_path=None, # str
                        origin_shield=aws_cloudfront.CfnDistribution.OriginShieldProperty(
                            enabled=True,
                            origin_shield_region="us-east-1"
                        ),
                        s3_origin_config=aws_cloudfront.CfnDistribution.S3OriginConfigProperty(
                            origin_access_identity=f"origin-access-identity/cloudfront/{oai.ref}"),
                    ),
                ],
                default_cache_behavior=aws_cloudfront.CfnDistribution.DefaultCacheBehaviorProperty(
                    target_origin_id="OriginS3",
                    viewer_protocol_policy="redirect-to-https", # allow-all, redirect-to-https, https-only
                    allowed_methods=[
                        "GET", "HEAD", "OPTIONS"
                    ],
                    cached_methods=[
                        "GET", "HEAD", "OPTIONS"
                    ],
                    compress=True,
                    # managed cache policy id
                    # https://docs.aws.amazon.com/ko_kr/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html
                    # managed origin request policy id
                    # https://docs.aws.amazon.com/ko_kr/AmazonCloudFront/latest/DeveloperGuide/using-managed-origin-request-policies.html
                    cache_policy_id=self.cache_policy.ref,
                    origin_request_policy_id=self.origin_request_policy.ref,
                    response_headers_policy_id=None,
                    field_level_encryption_id=None,
                    function_associations=None,
                    lambda_function_associations=None,
                    realtime_log_config_arn=None,
                    smooth_streaming=None,
                    trusted_key_groups=None,
                    trusted_signers=None,
                ),
                cache_behaviors=None,
                cnam_es=None, # CNAMEs
                aliases=None, # CNAMEs (alternate domain names)
                default_root_object=None, # str
                http_version="http2", # http1.1 , http2
                ipv6_enabled=True,
                price_class="PriceClass_All", # PriceClass_All, PriceClass_100 , PriceClass_200
                logging=None,
            ),
            tags=None)