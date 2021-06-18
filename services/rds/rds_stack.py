'''
    Dependency: vpc, security-group
'''
from aws_cdk import (
    core, aws_iam, aws_kms, aws_ec2, aws_logs, aws_rds
)

class RdsStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, security_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Init
        self.vpc = vpc
        self.project = project
        self.security_group = security_group
        self.role = dict()
        self.kms_key = dict()
        
        # subnet group
        self.subnet_group = aws_rds.SubnetGroup(self, "rds-subnetgroup",
            subnet_group_name=f"{self.project['prefix']}-rds-subnetgroup",
            description="vpc's description",
            vpc=self.vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.ISOLATED),
            removal_policy=core.RemovalPolicy.DESTROY)
        
        # IAM Role for cloudwatch to monitoring and logging
        self.role['monitoring'] = aws_iam.Role(self, "rds-monitoring-role",
            role_name   = f"{project['prefix']}-role-rds-monitoring",
            description = "",
            assumed_by  = aws_iam.ServicePrincipal("monitoring.rds.amazonaws.com"),
            external_id=None,
            external_ids=None,
            inline_policies=None,
            max_session_duration=None,
            path=None,
            permissions_boundary=None,
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonRDSEnhancedMonitoringRole")
            ]
        )
        
        # kms
        self.kms_key['rds'] = aws_kms.Key(self, "cmk-rds",
            alias                    = f"alias/{project['prefix']}-rds",
            description              = "",
            admins                   = None,
            enabled                  = True,
            enable_key_rotation      = True,
            pending_window           = core.Duration.days(7),
            removal_policy           = core.RemovalPolicy.DESTROY,
            policy                   = aws_iam.PolicyDocument(
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
        # self.add_aurora_mysql()
        # self.add_aurora_postgres()
        self.add_mysql()
        # self.add_postgres()
    
    def add_aurora_mysql(self):
        # Parameter group
        parameter_group = aws_rds.ParameterGroup(self, "aurora_mysql_parameter_group", 
            engine=aws_rds.DatabaseClusterEngine.aurora_mysql(
                version=aws_rds.AuroraMysqlEngineVersion.VER_2_09_2),
            description="aurora-mysql's paramter-group",
            parameters={
                "max_connections": "1500"
            })
        # database cluster
        aws_rds.DatabaseCluster(self, "aurora_mysql",
            cluster_identifier=f"{self.project['prefix']}-rds-aurora-mysql",
            instance_identifier_base=None,
            engine=aws_rds.DatabaseClusterEngine.aurora_mysql(
                version=aws_rds.AuroraMysqlEngineVersion.VER_2_09_2),
            instances=3,
            instance_props=aws_rds.InstanceProps(
                vpc=self.vpc,
                instance_type=aws_ec2.InstanceType.of(
                    instance_class=aws_ec2.InstanceClass.BURSTABLE3,
                    instance_size=aws_ec2.InstanceSize.SMALL
                ),
                parameter_group=parameter_group,
                delete_automated_backups=None,
                allow_major_version_upgrade=None,
                auto_minor_version_upgrade=None,
                enable_performance_insights=None, # mysql 2.10 and postgresql 9.6 higher, 
                performance_insight_encryption_key=None, # default aws managed master key
                performance_insight_retention=None, # default 7 days
                publicly_accessible=False,
                security_groups=[
                    self.security_group['example']
                ],
                vpc_subnets=None # default not specified
            ),
            subnet_group=self.subnet_group,
            parameter_group=parameter_group,
            storage_encrypted=True,
            storage_encryption_key=self.kms_key['rds'], # default aws managed master key
            port=3306,
            default_database_name="db", # Default, Database is not created in cluster
            credentials=None, # Default, username: 'admin', password is generated by secret manager
            # iam_authentication=False,
            deletion_protection=False,
            backup=None, # Default, retention everyday and preffered 30 minute
            cloudwatch_logs_exports=["audit","error","slowquery"], # ["audit","error","general","slowquery"]
            cloudwatch_logs_retention=aws_logs.RetentionDays.TWO_WEEKS,
            cloudwatch_logs_retention_role=None, # Default, created new role
            monitoring_interval=core.Duration.seconds(60), # default, no enhanced monitoring
            monitoring_role=self.role['monitoring'],
            preferred_maintenance_window=None,
            removal_policy=core.RemovalPolicy.DESTROY,
            s3_export_buckets=None, # default none
            s3_export_role=None, # default none
            s3_import_buckets=None, # default none
            s3_import_role=None # default none
        )


    def add_aurora_postgres(self):
        # Parameter group
        parameter_group = aws_rds.ParameterGroup(self, "aurora_postgres_parameter_group", 
            engine=aws_rds.DatabaseClusterEngine.aurora_postgres(
                version=aws_rds.AuroraPostgresEngineVersion.VER_12_4),
            description="aurora-postgres's paramter-group",
            parameters={
                "max_connections": "1500"
            })
        # database cluster
        aws_rds.DatabaseCluster(self, "aurora_postgres",
            cluster_identifier=f"{self.project['prefix']}-rds-aurora-postgres",
            instance_identifier_base=None,
            engine=aws_rds.DatabaseClusterEngine.aurora_postgres(
                version=aws_rds.AuroraPostgresEngineVersion.VER_12_4),
            instances=3,
            instance_props=aws_rds.InstanceProps(
                vpc=self.vpc,
                instance_type=aws_ec2.InstanceType.of(
                    instance_class=aws_ec2.InstanceClass.BURSTABLE3,
                    instance_size=aws_ec2.InstanceSize.MEDIUM
                ),
                parameter_group=parameter_group,
                delete_automated_backups=None,
                allow_major_version_upgrade=None,
                auto_minor_version_upgrade=None,
                enable_performance_insights=None, # mysql 2.10 and postgresql 9.6 higher, 
                performance_insight_encryption_key=None, # default aws managed master key
                performance_insight_retention=None, # default 7 days
                publicly_accessible=False,
                security_groups=[
                    self.security_group['example']
                ],
                vpc_subnets=None # default not specified
            ),
            subnet_group=self.subnet_group,
            parameter_group=parameter_group,
            storage_encrypted=True,
            storage_encryption_key=self.kms_key['rds'], # default aws managed master key
            port=5432,
            default_database_name="example", # Default, Database is not created in cluster
            credentials=None, # Default, username: 'admin', password is generated by secret manager
            # iam_authentication=False,
            deletion_protection=False,
            backup=None, # Default, retention everyday and preffered 30 minute
            cloudwatch_logs_exports=["postgresql"], # ["postgresql"]
            cloudwatch_logs_retention=aws_logs.RetentionDays.TWO_WEEKS,
            cloudwatch_logs_retention_role=None, # Default, created new role
            monitoring_interval=core.Duration.seconds(60), # default, no enhanced monitoring
            monitoring_role=self.role['monitoring'],
            preferred_maintenance_window=None,
            removal_policy=core.RemovalPolicy.DESTROY,
            s3_export_buckets=None, # default none
            s3_export_role=None, # default none
            s3_import_buckets=None, # default none
            s3_import_role=None # default none
        )
    
    def add_mysql(self):
        # Parameter group
        parameter_group = aws_rds.ParameterGroup(self, "mysql_parameter_group", 
            engine=aws_rds.DatabaseInstanceEngine.mysql(
                version=aws_rds.MysqlEngineVersion.VER_8_0_21),
            description="mysql paramter-group",
            parameters={
                "max_connections": "1500"
            })
        # database instance
        mysql_instance = aws_rds.DatabaseInstance(self, "mysql",
            engine=aws_rds.DatabaseInstanceEngine.mysql(
                version=aws_rds.MysqlEngineVersion.VER_8_0_21),
            instance_identifier=f"{self.project['prefix']}-mysql",
            instance_type=aws_ec2.InstanceType.of(
                instance_class=aws_ec2.InstanceClass.BURSTABLE3,
                instance_size=aws_ec2.InstanceSize.MICRO
            ),
            # Storage
            storage_type=aws_rds.StorageType.GP2,
            allocated_storage=20,
            max_allocated_storage=1000,
            iops=None,
            storage_encrypted=True,
            storage_encryption_key=self.kms_key['rds'],
            # Network
            vpc=self.vpc,
            multi_az=True,
            availability_zone=None,
            port=3306,
            subnet_group=self.subnet_group,
            vpc_placement=None,
            vpc_subnets=None,
            publicly_accessible=False,
            security_groups=[self.security_group['example']],
            # Authentication
            credentials=None, # Default, username: 'admin', password is generated by secret manager
            iam_authentication=None,
            domain=None, # kerberos authentication
            domain_role=None,
            # monitoring and logging
            monitoring_interval=core.Duration.seconds(60),
            monitoring_role=self.role['monitoring'],
            enable_performance_insights=None,
            performance_insight_encryption_key=None,
            performance_insight_retention=None,
            cloudwatch_logs_exports=["error","slowquery"], # ["error","general","slowquery"]
            cloudwatch_logs_retention=aws_logs.RetentionDays.TWO_WEEKS,
            cloudwatch_logs_retention_role=None, # Default, create new role
            # Advanced
            database_name="example",
            parameter_group=parameter_group,
            option_group=None,
            removal_policy=core.RemovalPolicy.DESTROY,
            deletion_protection=False,
            character_set_name=None,
            timezone=None,
            license_model=None,
            processor_features=None,
            s3_export_buckets=None,
            s3_export_role=None,
            s3_import_buckets=None,
            s3_import_role=None,
            allow_major_version_upgrade=None,
            auto_minor_version_upgrade=None,
            # backup
            backup_retention=None,
            copy_tags_to_snapshot=None,
            delete_automated_backups=None,   
            preferred_backup_window=None,
            preferred_maintenance_window=None,
        )
        # read-replica        
        # aws_rds.DatabaseInstanceReadReplica(self, "mysql-read-replica",
        #     source_database_instance=mysql_instance,
        #     instance_identifier=f"{self.project['prefix']}-mysql-rr1",
        #     instance_type=aws_ec2.InstanceType.of(
        #         instance_class=aws_ec2.InstanceClass.BURSTABLE3,
        #         instance_size=aws_ec2.InstanceSize.MICRO
        #     ),
        #     # Storage
        #     storage_type=aws_rds.StorageType.GP2,
        #     max_allocated_storage=1000,
        #     iops=None,
        #     storage_encrypted=True,
        #     storage_encryption_key=self.kms_key['rds'],
        #     # Network
        #     vpc=self.vpc,
        #     multi_az=True,
        #     availability_zone=None,
        #     port=3306,
        #     subnet_group=self.subnet_group,
        #     vpc_placement=None,
        #     vpc_subnets=None,
        #     publicly_accessible=False,
        #     security_groups=[self.security_group['example']],
        #     # Authentication
        #     iam_authentication=None,
        #     domain=None, # kerberos authentication
        #     domain_role=None,
        #     # monitoring and logging
        #     monitoring_interval=core.Duration.seconds(60),
        #     monitoring_role=self.role['monitoring'],
        #     enable_performance_insights=None,
        #     performance_insight_encryption_key=None,
        #     performance_insight_retention=None,
        #     cloudwatch_logs_exports=["error","slowquery"], # ["error","general","slowquery"]
        #     cloudwatch_logs_retention=aws_logs.RetentionDays.TWO_WEEKS,
        #     cloudwatch_logs_retention_role=None, # Default, create new role
        #     # Advanced
        #     removal_policy=core.RemovalPolicy.DESTROY,
        #     deletion_protection=False,
        #     processor_features=None,
        #     s3_export_buckets=None,
        #     s3_export_role=None,
        #     s3_import_buckets=None,
        #     s3_import_role=None,
        #     auto_minor_version_upgrade=None,
        #     # backup
        #     backup_retention=None,
        #     copy_tags_to_snapshot=None,
        #     delete_automated_backups=None,   
        #     preferred_backup_window=None,
        #     preferred_maintenance_window=None,
        # )
    
    def add_postgres(self):
        # Parameter group
        parameter_group = aws_rds.ParameterGroup(self, "postgres_parameter_group", 
            engine=aws_rds.DatabaseInstanceEngine.postgres(
                version=aws_rds.PostgresEngineVersion.VER_13_1),
            description="postgres paramter-group",
            parameters={
                "max_connections": "1500"
            })
        # database instance
        aws_rds.DatabaseInstance(self, "postgres",
            engine=aws_rds.DatabaseInstanceEngine.postgres(
                version=aws_rds.PostgresEngineVersion.VER_13_1),
            instance_identifier=f"{self.project['prefix']}-postgres",
            instance_type=aws_ec2.InstanceType.of(
                instance_class=aws_ec2.InstanceClass.BURSTABLE3,
                instance_size=aws_ec2.InstanceSize.MICRO
            ),
            # Storage
            storage_type=aws_rds.StorageType.GP2,
            allocated_storage=20,
            max_allocated_storage=1000,
            iops=None,
            storage_encrypted=True,
            storage_encryption_key=self.kms_key['rds'],
            # Network
            vpc=self.vpc,
            multi_az=True,
            availability_zone=None,
            port=5432,
            subnet_group=self.subnet_group,
            vpc_placement=None,
            vpc_subnets=None,
            publicly_accessible=False,
            security_groups=[self.security_group['example']],
            # Authentication
            credentials=None, # Default, username: 'admin', password is generated by secret manager
            iam_authentication=None,
            domain=None, # kerberos authentication
            domain_role=None,
            # monitoring and logging
            monitoring_interval=core.Duration.seconds(60),
            monitoring_role=self.role['monitoring'],
            enable_performance_insights=None,
            performance_insight_encryption_key=None,
            performance_insight_retention=None,
            cloudwatch_logs_exports=["postgresql","upgrade"], # ["postgresql","upgrade"]
            cloudwatch_logs_retention=aws_logs.RetentionDays.TWO_WEEKS,
            cloudwatch_logs_retention_role=None, # Default, create new role
            # Advanced
            database_name="example",
            parameter_group=parameter_group,
            option_group=None,
            removal_policy=core.RemovalPolicy.DESTROY,
            deletion_protection=False,
            character_set_name=None,
            timezone=None,
            license_model=None,
            processor_features=None,
            s3_export_buckets=None,
            s3_export_role=None,
            s3_import_buckets=None,
            s3_import_role=None,
            allow_major_version_upgrade=None,
            auto_minor_version_upgrade=None,
            # backup
            backup_retention=None,
            copy_tags_to_snapshot=None,
            delete_automated_backups=None,   
            preferred_backup_window=None,
            preferred_maintenance_window=None,
        )