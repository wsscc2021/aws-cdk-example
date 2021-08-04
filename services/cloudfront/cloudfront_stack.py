'''
    Dependency: origin(s3 or elb)...
    origin structure:
        {
            's3': {
                'bucket_name1',
                'bucket_name2',
                'bucket_name3',
                ...
            }
        }
'''
from constructs import Construct
from aws_cdk import Stack, aws_cloudfront, aws_cloudfront_origins, aws_certificatemanager

class CloudFrontStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, origin, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Init
        self.project = project
        self.origin = origin
        
        # Cache policy
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/CachePolicy.html
        cache_policy = aws_cloudfront.CachePolicy(self, "cloudfront-cache-policy",
            cache_policy_name="cloudfront-cache-policy",
            comment="",
            cookie_behavior=aws_cloudfront.CacheCookieBehavior.all(),
            header_behavior=aws_cloudfront.CacheHeaderBehavior.none(),
            query_string_behavior=aws_cloudfront.CacheQueryStringBehavior.all(),
            default_ttl=None,
            max_ttl=None,
            min_ttl=None,
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True)

        # Origin request policy
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/OriginRequestPolicy.html
        origin_request_policy = aws_cloudfront.OriginRequestPolicy(self, "cloudfront-origin-request-policy",
            origin_request_policy_name="cloudfront-origin-request-policy",
            comment="",
            cookie_behavior=aws_cloudfront.OriginRequestCookieBehavior.all(),
            header_behavior=aws_cloudfront.OriginRequestHeaderBehavior.all(),
            query_string_behavior=aws_cloudfront.OriginRequestQueryStringBehavior.all())

        # Distribution
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/Distribution.html
        aws_cloudfront.Distribution(self, "cloudfront",
            default_behavior=aws_cloudfront.BehaviorOptions(
                origin=aws_cloudfront_origins.S3Origin(
                    bucket=self.origin['s3']['sample'],
                    origin_access_identity=None,
                    origin_path=None),
                allowed_methods=aws_cloudfront.AllowedMethods.ALLOW_ALL,
                cached_methods=aws_cloudfront.CachedMethods.CACHE_GET_HEAD,
                viewer_protocol_policy=aws_cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
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
            certificate=None,
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