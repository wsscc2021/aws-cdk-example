'''
    Dependency: vpc, security-group
'''
from constructs import Construct
from aws_cdk import Stack, Duration, RemovalPolicy, aws_ec2, aws_iam, aws_kms, aws_elasticache

class ElasticacheStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, vpc, security_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Init
        self.vpc = vpc
        self.project = project
        self.security_group = security_group
        self.role = dict()
        self.kms_key = dict()

        # subnet group
        self.subnet_group = aws_elasticache.CfnSubnetGroup(self, "redis_subnet_group",
            cache_subnet_group_name=f"{self.project['prefix']}-redis-subnetgroup",
            description="",
            subnet_ids=[ subnet.subnet_id for subnet in self.vpc.isolated_subnets ]
        )

        # kms
        self.kms_key['redis'] = aws_kms.Key(self, "kms-redis",
            alias               = f"alias/{project['prefix']}-redis",
            description         = "",
            admins              = None,
            enabled             = True,
            enable_key_rotation = True,
            pending_window      = Duration.days(7),
            removal_policy      = RemovalPolicy.DESTROY,
            policy              = aws_iam.PolicyDocument(
                statements=[
                    aws_iam.PolicyStatement(
                        sid="Enable IAM User Permission",
                        actions=[
                            "kms:*"
                        ],
                        conditions=None,
                        effect=aws_iam.Effect.ALLOW,
                        not_actions=None,
                        not_principals=None,
                        not_resources=None,
                        principals=[
                            aws_iam.AccountRootPrincipal()
                        ],
                        resources=["*"]
                    )
                ]
            )
        )

        # database
        self.add_redis()
        self.add_memcached()
    
    def add_redis(self):
        aws_elasticache.CfnReplicationGroup(self, "redis-cluster",
            #identify
            replication_group_id=f"{self.project['prefix']}-redis-cluster",
            global_replication_group_id=None,
            primary_cluster_id=None,
            replication_group_description="",
            #speicific
            cache_node_type="cache.t3.small",
            engine="redis",
            engine_version=None,
            num_node_groups=3, # number of shard
            replicas_per_node_group=2, # number of replica
            port=6379,
            multi_az_enabled=True,
            automatic_failover_enabled=True,
            cache_parameter_group_name=None,
            #network
            cache_subnet_group_name=self.subnet_group.cache_subnet_group_name,
            security_group_ids=[self.security_group['example'].security_group_id],
            #security
            at_rest_encryption_enabled=True,
            transit_encryption_enabled=True,
            kms_key_id=self.kms_key['redis'].key_id,
            auth_token=None,
            #maintain
            auto_minor_version_upgrade=None,
            # log_delivery_configurations=None,
            notification_topic_arn=None,
            preferred_maintenance_window=None,
            #advanced
            snapshot_arns=None,
            snapshot_name=None,
            snapshot_retention_limit=None,
            snapshotting_cluster_id=None,
            snapshot_window=None,
            tags=None,
            user_group_ids=None
        ).add_depends_on(self.subnet_group)
    
    def add_memcached(self):
        aws_elasticache.CfnCacheCluster(self, "memcached-cluster",
            #identify
            cluster_name=f"{self.project['prefix']}-memcached-cluster",
            #specify
            cache_node_type="cache.t3.small",
            engine="memcached",
            engine_version=None,
            num_cache_nodes=3,
            #network
            az_mode="cross-az",
            cache_parameter_group_name=None,
            cache_security_group_names=None,
            cache_subnet_group_name=self.subnet_group.cache_subnet_group_name,
            vpc_security_group_ids=[self.security_group['example'].security_group_id],
            port=11211,
            #advanced
            auto_minor_version_upgrade=None,
            # log_delivery_configurations=None,
            notification_topic_arn=None,
            snapshot_arns=None,
            snapshot_name=None,
            snapshot_retention_limit=None,
            snapshot_window=None,
            tags=None
        ).add_depends_on(self.subnet_group)