from aws_cdk import (
    core, aws_ec2, aws_iam, aws_kms, aws_eks
)
import json

class EksStack(core.Stack):
    '''
        1. EKS Stack은 VPC Stack과 Security Group Stack에 의존적입니다.
           argument로 vpc와 security group를 넣어줘야 합니다.
        2. kms key와 role은 eks stack 내에서 생성해줍니다.
        3. key pair를 미리 생성해야 합니다.
    '''
    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, security_group: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # init
        self.vpc            = vpc
        self.project        = project
        self.security_group = security_group
        self.keypair_name   = "dev-useast1"

        # create resource
        # EKS Cluster는 생성되는 데 오랜 시간이 소모됩니다. Rollback 시간을 줄이려면 순차적으로 하나씩 생성해야합니다. 
        self.create_security_group() # 원래는 security_group_stack에서 생성해야합니다.
        self.create_kms()
        self.create_iam()
        self.create_eks_cluster()
        self.create_launch_template()
        self.create_nodegroup()
        self.create_service_account()
        self.install_helm_chart()

    def create_kms(self):
        # KMS CMK for EKS
        self.kms_key = dict()
        self.kms_key['eks-cluster'] = aws_kms.Key(self, "cmk-eks-cluster",
            alias                    = f"alias/{self.project['prefix']}-cmk-eks-cluster",
            description              = "description in this field",
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
                            aws_iam.AccountRootPrincipal(),
                            aws_iam.ArnPrincipal(arn="arn:aws:iam::242593025403:role/AdministratorRole"),
                            aws_iam.ArnPrincipal(arn="arn:aws:iam::242593025403:role/PowerUserRole")
                        ],
                        resources=["*"]
                    )
                ]
            )
        )

    def create_iam(self):
        # IAM Role for EKS
        self.role = dict()
        # Existing role
        self.role['admin'] = aws_iam.Role.from_role_arn(self, "role-admin",
            role_arn="arn:aws:iam::242593025403:role/AdministratorRole",
            mutable=True)
        # Create Role
        self.role['eks-cluster'] = aws_iam.Role(self, "role-eks-cluster",
            role_name   = f"{self.project['prefix']}-role-eks-cluster",
            description = "",
            assumed_by  = aws_iam.ServicePrincipal("eks.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy")
            ])
        self.role['nodegroup'] = aws_iam.Role(self, "role-nodegroup",
            role_name   = f"{self.project['prefix']}-role-nodegroup",
            description = "",
            assumed_by  = aws_iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKS_CNI_Policy"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSWorkerNodePolicy")                
            ])

    def create_eks_cluster(self):
        # EkS Cluster
        self.eks_cluster = aws_eks.Cluster(self, "eks-cluster",
            default_capacity=0,
            # default_capacity_instance=None,
            # default_capacity_type=None,
            # cluster_handler_environment=None,
            # core_dns_compute_type=None,
            endpoint_access=aws_eks.EndpointAccess.PUBLIC_AND_PRIVATE,
            # kubectl_environment=None,
            # kubectl_layer=None,
            # kubectl_memory=None,
            masters_role=self.role['admin'],
            output_masters_role_arn=True,
            # place_cluster_handler_in_vpc=None,
            # prune=None,
            secrets_encryption_key=self.kms_key['eks-cluster'],
            version=aws_eks.KubernetesVersion.V1_19,
            cluster_name=f"{self.project['prefix']}-eks-cluster",
            output_cluster_name=True,
            output_config_command=True,
            role=self.role['eks-cluster'],
            security_group=self.security_group['eks-cluster-controlplane'],
            vpc=self.vpc,
            vpc_subnets=[
                aws_ec2.SubnetSelection(subnets=[subnet for subnet in self.vpc.public_subnets]),
                aws_ec2.SubnetSelection(subnets=[subnet for subnet in self.vpc.private_subnets])
            ])

    def create_launch_template(self):
        self.launch_template = dict()
        self.launch_template['core'] = aws_ec2.LaunchTemplate(self, "lt-nodegroup-core",
            block_devices=[
                aws_ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=aws_ec2.BlockDeviceVolume.ebs(
                        volume_type=aws_ec2.EbsDeviceVolumeType.GP3,
                        # iops=3000,
                        volume_size=20,
                        encrypted=True,
                        delete_on_termination=True,
                    )
                )
            ],
            instance_type=aws_ec2.InstanceType("t3.xlarge"),
            key_name=self.keypair_name,
            launch_template_name=f"{self.project['prefix']}-lt-nodegroup-core",
            security_group=self.security_group['eks-nodegroup'])
        
    def create_nodegroup(self):
        self.nodegroup = dict()
        self.nodegroup['core'] = aws_eks.Nodegroup(self, "nodegroup-core", 
            cluster=self.eks_cluster,
            nodegroup_name=f"{self.project['prefix']}-nodegroup-core",
            tags={
                "Name": f"{self.project['prefix']}-nodegroup-core"
            },
            labels={
                "Key1": "Value1"
            },
            # disk_size=20,
            capacity_type=aws_eks.CapacityType.ON_DEMAND,
            max_size=20,
            min_size=3,
            desired_size=3,
            force_update=False,
            launch_template_spec=aws_eks.LaunchTemplateSpec(
                id      = self.launch_template['core'].launch_template_id,
                version = self.launch_template['core'].default_version_number
            ),
            node_role=self.role['nodegroup'],
            # remote_access=None,
            subnets=aws_ec2.SubnetSelection(
                subnet_type=aws_ec2.SubnetType.PRIVATE
            ))

    def create_service_account(self):
        self.service_account = dict()
        self.add_service_account(
            name        = "aws-load-balancer-controller",
            namespace   = "kube-system",
            policy_file = "eks/policy/aws-load-balancer-controller.json")
        self.add_service_account(
            name        = "cluster-autoscaler",
            namespace   = "kube-system",
            policy_file = "eks/policy/cluster-autoscaler.json")
        self.add_service_account(
            name        = "external-dns",
            namespace   = "kube-system",
            policy_file = "eks/policy/external-dns.json")
        self.add_service_account(
            name        = "aws-cloudwatch-metrics",
            namespace   = "kube-system",
            managed_policies = [
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")
            ])
        self.add_service_account(
            name        = "appmesh-controller",
            namespace   = "kube-system",
            managed_policies = [
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSAppMeshFullAccess"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSCloudMapFullAccess")
            ])
        self.add_service_account(
            name        = "appmesh-application",
            namespace   = "kube-system",
            managed_policies = [
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSAppMeshEnvoyAccess"),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSXrayWriteOnlyAccess")
            ])

    def add_service_account(self, name, namespace, policy_file=None, managed_policies=[]):
        self.service_account[name] = aws_eks.ServiceAccount(
            self, f"sa-{name}",
            cluster=self.eks_cluster,
            name=name,
            namespace=namespace)
        if policy_file:
            with open(policy_file) as json_file:
                json_data = json.load(json_file)
            for statement in json_data['Statement']:
                self.service_account[name].add_to_principal_policy(
                    aws_iam.PolicyStatement.from_json(statement))
        for policy in managed_policies:
            self.service_account[name].role.add_managed_policy(policy)

    def install_helm_chart(self):
        self.eks_cluster.add_helm_chart(
            "helm-aws-load-balancer-controller",
            repository="https://aws.github.io/eks-charts",
            chart="aws-load-balancer-controller",
            release="aws-load-balancer-controller",
            version=None, 
            create_namespace=None,
            namespace="kube-system",
            values={
                'serviceAccount': {
                    'create': False,
                    'name': 'aws-load-balancer-controller'
                },
                'clusterName': self.eks_cluster.cluster_name
            },
            timeout=None,
            wait=None)

        self.eks_cluster.add_helm_chart(
            "helm-cluster-autoscaler",
            repository="https://kubernetes.github.io/autoscaler",
            chart="cluster-autoscaler",
            release="aws-cluster-autoscaler",
            version=None, 
            create_namespace=None,
            namespace="kube-system",
            values={
                'autoDiscovery': {
                    'clusterName': self.eks_cluster.cluster_name,
                },
                'awsRegion': self.project['region'],
                'rbac': {
                    'serviceAccount': {
                        'create': False,
                        'name': 'cluster-autoscaler'
                    }
                }
            },
            timeout=None,
            wait=None)
        
        self.eks_cluster.add_helm_chart(
            "helm-external-dns",
            repository="https://charts.bitnami.com/bitnami",
            chart="external-dns",
            release="external-dns",
            version=None, 
            create_namespace=None,
            namespace="kube-system",
            values={
                'serviceAccount': {
                    'create': False,
                    'name': 'external-dns'
                }
            },
            timeout=None,
            wait=None)

        self.eks_cluster.add_helm_chart(
            "helm-aws-cloudwatch-metrics",
            repository="https://aws.github.io/eks-charts",
            chart="aws-cloudwatch-metrics",
            release="aws-cloudwatch-metrics",
            version=None, 
            create_namespace=None,
            namespace="kube-system",
            values={
                'clusterName': self.eks_cluster.cluster_name,
                'serviceAccount': {
                    'create': False,
                    'name': 'aws-cloudwatch-metrics'
                }
            },
            timeout=None,
            wait=None)
        
        self.eks_cluster.add_helm_chart(
            "helm-appmesh-controller",
            repository="https://aws.github.io/eks-charts",
            chart="appmesh-controller",
            release="appmesh-controller",
            version=None, 
            create_namespace=None,
            namespace="kube-system",
            values={
                'serviceAccount': {
                    'create': False,
                    'name': 'appmesh-controller'
                },
                'tracing': {
                    'enabled': True,
                    'provider': 'x-ray'
                }
            },
            timeout=None,
            wait=None)

    def create_security_group(self):
         # Security Group
        self.add_security_group(
            name = "eks-cluster-controlplane",
            description = "",
            allow_all_outbound = False)
        self.add_security_group(
            name = "eks-nodegroup",
            description = "",
            allow_all_outbound = True)
        
        # eks-cluster-controlplane
        self.security_group['eks-cluster-controlplane'].add_ingress_rule(
            peer = self.security_group['eks-nodegroup'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="eks-cluster-controlplane-1",
                from_port=443,
                to_port=443),
            description = "")
        self.security_group['eks-cluster-controlplane'].add_egress_rule(
            peer = self.security_group['eks-nodegroup'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="eks-cluster-controlplane-2",
                from_port=1025,
                to_port=65535),
            description = "")
        
        # eks nodegroup
        self.security_group['eks-nodegroup'].add_ingress_rule(
            peer = self.security_group['eks-nodegroup'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.ALL,
                string_representation="eks-nodegroup-1",
                from_port=None,
                to_port=None),
            description = "")
        self.security_group['eks-nodegroup'].add_ingress_rule(
            peer = self.security_group['eks-cluster-controlplane'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="eks-nodegroup-2",
                from_port=443,
                to_port=443),
            description = "")
        self.security_group['eks-nodegroup'].add_ingress_rule(
            peer = self.security_group['eks-cluster-controlplane'],
            connection=aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="eks-nodegroup-3",
                from_port=1025,
                to_port=65535),
            description = "",)

    def add_security_group(self, name: str, description: str, allow_all_outbound: bool):
        self.security_group[name] = aws_ec2.SecurityGroup(self, name,
            vpc                 = self.vpc,
            security_group_name = f"{self.project['prefix']}-sg-{name}",
            description         = description,
            allow_all_outbound  = allow_all_outbound)
        core.Tags.of(self.security_group[name]).add(
            "Name",
            f"{self.project['prefix']}-sg-{name}")