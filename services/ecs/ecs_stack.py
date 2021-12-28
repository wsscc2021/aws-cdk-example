'''
    Dependency: vpc, security_group
'''
from constructs import Construct
from aws_cdk import Stack, Duration, aws_ec2, aws_autoscaling, aws_iam, aws_ecr, aws_ecs

class EcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, vpc, security_group, target_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.project = project
        self.vpc = vpc
        self.security_group = security_group
        self.target_group = target_group
        self.task_definition = dict()
        self.role = dict()
        self.service = dict()
        self.scalableTask = dict()
        
        # Resources
        self.create_ecs_cluster()
        self.create_ecs_asg()
        self.create_ec2_task_definition()
        self.create_ec2_service()
        self.create_fargate_task_definition()
        self.create_fargate_service()

    def create_ecs_cluster(self):
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/Cluster.html
        self.ecs_cluster = aws_ecs.Cluster(self, "ecs-cluster",
            capacity=None,
            cluster_name="ecs-cluster",
            container_insights=True,
            default_cloud_map_namespace=None,
            enable_fargate_capacity_providers=None,
            execute_command_configuration=None,
            vpc=self.vpc)

    def create_ecs_asg(self):
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/Cluster.html
        # 생성되는 asg에 security group을 지정할 수 없습니다.
        self.ecs_cluster.add_capacity("ecs-nodegroup",
            auto_scaling_group_name="ecs-nodegroup",
            instance_type=aws_ec2.InstanceType("c5.xlarge"),
            machine_image=None,
            machine_image_type=None,
            block_devices=[
                aws_autoscaling.BlockDevice(
                    device_name="/dev/xvda",
                    volume=aws_autoscaling.BlockDeviceVolume.ebs(
                        volume_type=aws_autoscaling.EbsDeviceVolumeType.GP3,
                        # iops=3000,
                        volume_size=50, # expect size >= 30GB
                        encrypted=True,
                        delete_on_termination=True,
                    )
                )
            ],
            can_containers_access_instance_role=None,
            spot_instance_draining=None,
            topic_encryption_key=None,
            allow_all_outbound=None,
            associate_public_ip_address=None,
            cooldown=Duration.seconds(120),
            group_metrics=None,
            health_check=None,
            ignore_unmodified_size_properties=None,
            instance_monitoring=None,
            key_name=self.project['keypair'],
            min_capacity=3,
            max_capacity=20,
            desired_capacity=None,
            max_instance_lifetime=None,
            new_instances_protected_from_scale_in=None,
            notifications=None,
            signals=None,
            spot_price=None,
            update_policy=None,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT))
    
    def create_ec2_task_definition(self):
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/Role.html
        self.role['foo'] = aws_iam.Role(self, "role-foo",
            role_name   = f"{self.project['prefix']}-role-foo",
            description = "",
            assumed_by  = aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
            ])
        
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/Ec2TaskDefinition.html
        self.task_definition['foo'] = aws_ecs.Ec2TaskDefinition(self, "td-foo", 
            inference_accelerators=None,
            ipc_mode=None,
            network_mode=aws_ecs.NetworkMode.AWS_VPC,
            pid_mode=None,
            placement_constraints=None,
            execution_role=None,
            family="td-foo",
            proxy_configuration=None,
            task_role=self.role['foo'],
            volumes=None)
        
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/Ec2TaskDefinition.html
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecr/Repository.html#aws_cdk.aws_ecr.Repository.arn_for_local_repository
        self.task_definition['foo'].add_container("foo-helloworld-container",
            command=None,
            container_name="webapp-container",
            cpu=1024,
            disable_networking=None,
            dns_search_domains=None,
            dns_servers=None,
            docker_labels=None,
            docker_security_options=None,
            entry_point=None,
            environment=None,
            environment_files=None,
            essential=None,
            extra_hosts=None,
            gpu_count=None,
            health_check=None,
            hostname=None,
            image=aws_ecs.ContainerImage.from_ecr_repository(
                repository = aws_ecr.Repository.from_repository_name(self, "ecr-helloworld-app",
                    repository_name="helloworld-app"),
                tag = "20211227.163900"
            ),
            inference_accelerator_resources=None,
            linux_parameters=None,
            logging=None,
            memory_limit_mib=2048,
            memory_reservation_mib=2048,
            port_mappings=[
                aws_ecs.PortMapping(
                    container_port=5000,
                    host_port=5000,
                    protocol=aws_ecs.Protocol.TCP)
            ],
            privileged=None,
            readonly_root_filesystem=None,
            secrets=None,
            start_timeout=Duration.seconds(10),
            stop_timeout=Duration.seconds(120),
            system_controls=None,
            user=None,
            working_directory=None)
    
    def create_ec2_service(self):
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/Ec2Service.html
        self.service['foo'] = aws_ecs.Ec2Service(self, "service-foo",
            task_definition=self.task_definition['foo'],
            assign_public_ip=False,
            daemon=None,
            placement_constraints=None,
            placement_strategies=None,
            security_groups=[
                self.security_group['example']
            ],
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT),
            capacity_provider_strategies=None,
            circuit_breaker=None,
            cloud_map_options=None,
            cluster=self.ecs_cluster,
            deployment_controller=None,
            desired_count=3,
            enable_ecs_managed_tags=None,
            enable_execute_command=None,
            health_check_grace_period=None,
            max_healthy_percent=600,
            min_healthy_percent=100,
            propagate_tags=None,
            service_name="service-foo")
        
        # attach elb
        self.service['foo'].attach_to_application_target_group(
            target_group=self.target_group['foo-app'])
        
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/ScalableTaskCount.html#aws_cdk.aws_ecs.ScalableTaskCount
        self.scalableTask['foo'] = self.service['foo'].auto_scale_task_count(
            max_capacity=30,
            min_capacity=3)
        self.scalableTask['foo'].scale_on_cpu_utilization("foo-scale-on-cpu",
            target_utilization_percent=60,
            disable_scale_in=False,
            policy_name=None,
            scale_in_cooldown=Duration.seconds(180),
            scale_out_cooldown=Duration.seconds(60))
    
    def create_fargate_task_definition(self):
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/Role.html
        self.role['bar'] = aws_iam.Role(self, "role-bar",
            role_name   = f"{self.project['prefix']}-role-bar",
            description = "",
            assumed_by  = aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
            ])

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/FargateTaskDefinition.html
        self.task_definition['bar'] = aws_ecs.FargateTaskDefinition(self, "td-bar",
            cpu=1024,
            ephemeral_storage_gib=None,
            memory_limit_mib=2048,
            execution_role=None,
            family="td-bar",
            proxy_configuration=None,
            task_role=self.role['bar'],
            volumes=None)
        
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/FargateTaskDefinition.html
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecr/Repository.html#aws_cdk.aws_ecr.Repository.arn_for_local_repository
        self.task_definition['bar'].add_container("bar-helloworld-container",
            command=None,
            container_name="webapp-container",
            cpu=1024,
            disable_networking=None,
            dns_search_domains=None,
            dns_servers=None,
            docker_labels=None,
            docker_security_options=None,
            entry_point=None,
            environment=None,
            environment_files=None,
            essential=None,
            extra_hosts=None,
            gpu_count=None,
            health_check=None,
            hostname=None,
            image=aws_ecs.ContainerImage.from_ecr_repository(
                repository = aws_ecr.Repository.from_repository_name(self, "ecr-helloworld-app-2",
                    repository_name="helloworld-app"),
                tag = "20211227.163900"
            ),
            inference_accelerator_resources=None,
            linux_parameters=None,
            logging=None,
            memory_limit_mib=2048,
            memory_reservation_mib=2048,
            port_mappings=[
                aws_ecs.PortMapping(
                    container_port=5000,
                    host_port=5000,
                    protocol=aws_ecs.Protocol.TCP)
            ],
            privileged=None,
            readonly_root_filesystem=None,
            secrets=None,
            start_timeout=Duration.seconds(10),
            stop_timeout=Duration.seconds(120),
            system_controls=None,
            user=None,
            working_directory=None)
    
    def create_fargate_service(self):
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/FargateService.html
        self.service['bar'] = aws_ecs.FargateService(self, "service-bar",
            task_definition=self.task_definition['bar'],
            assign_public_ip=None,
            platform_version=None,
            security_groups=[
                self.security_group['example']
            ],
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT),
            capacity_provider_strategies=None,
            circuit_breaker=None,
            cloud_map_options=None,
            cluster=self.ecs_cluster,
            deployment_controller=None,
            desired_count=3,
            enable_ecs_managed_tags=None,
            enable_execute_command=None,
            health_check_grace_period=None,
            max_healthy_percent=600,
            min_healthy_percent=100,
            propagate_tags=None,
            service_name="service-bar")
        
        # attach target group
        self.service['bar'].attach_to_application_target_group(
            target_group=self.target_group['foo-app'])
        
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/ScalableTaskCount.html#aws_cdk.aws_ecs.ScalableTaskCount
        self.scalableTask['bar'] = self.service['bar'].auto_scale_task_count(
            max_capacity=30,
            min_capacity=3)
        self.scalableTask['bar'].scale_on_request_count("bar-scale-on-request-count",
            requests_per_target=3000,
            target_group=self.target_group['foo-app'],
            disable_scale_in=False,
            policy_name=None,
            scale_in_cooldown=Duration.seconds(180),
            scale_out_cooldown=Duration.seconds(60))