'''
    Dependency: vpc, security_group
'''
from constructs import Construct
from aws_cdk import Stack, Duration, RemovalPolicy, Tags, aws_ec2, aws_iam, aws_kms, aws_eks
import json

class EksStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, vpc, security_group: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Init
        self.vpc            = vpc
        self.project        = project
        self.security_group = security_group
        # Create resource
        # It needs a long time about 30~60 minutes to is created EKS cluster
        # Therefore, It important that create in turn resource each in order to that can easier and faster rollback
        self.create_kms()
        self.create_iam()
        self.create_eks_cluster()
        self.create_launch_template()
        self.create_nodegroup()
        self.create_service_account()
        self.install_helm_chart()

    def create_kms(self):
        # KMS CMK for EKS
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_kms/Key.html
        self.kms_key = dict()
        self.kms_key['eks-cluster'] = aws_kms.Key(self, "cmk-eks-cluster",
            alias                    = f"alias/{self.project['prefix']}-cmk-eks-cluster",
            description              = "description in this field",
            admins                   = None,
            enabled                  = True,
            enable_key_rotation      = True,
            pending_window           = Duration.days(7),
            removal_policy           = RemovalPolicy.DESTROY,
            policy                   = None)

    def create_iam(self):
        # IAM role
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/Role.html
        self.role = dict()
        # Existing role
        self.role['admin'] = aws_iam.Role.from_role_arn(self, "role-admin",
            role_arn="arn:aws:iam::242593025403:role/AdministratorRole",
            mutable=True)
        # Create role
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
        # EkS cluster
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_eks/Cluster.html
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
            # place_cluster_handler_in_vpc=None,xxxxxxxxxxxxxxxxxxxxxxx
            # prune=None,
            secrets_encryption_key=self.kms_key['eks-cluster'],
            version=aws_eks.KubernetesVersion.V1_21,
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
        # EC2 launch template
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/LaunchTemplate.html
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
            key_name=self.project['keypair'],
            launch_template_name=f"{self.project['prefix']}-nodegroup-core-lt",
            security_group=self.security_group['eks-nodegroup'])
        
    def create_nodegroup(self):
        # managed node group
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_eks/Nodegroup.html
        self.nodegroup = dict()
        self.nodegroup['core'] = aws_eks.Nodegroup(self, "nodegroup-core", 
            cluster=self.eks_cluster,
            nodegroup_name=f"{self.project['prefix']}-nodegroup-core",
            tags={
                "Name": f"{self.project['prefix']}-nodegroup-core"
            },
            labels={
                "management": "core"
            },
            taints=None,
            ami_type=aws_eks.NodegroupAmiType.BOTTLEROCKET_X86_64,
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
                subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_NAT
            ))

    def create_service_account(self):
        # service account
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_eks/ServiceAccount.html
        self.service_account = dict()
        self.add_service_account(
            name        = "aws-load-balancer-controller",
            namespace   = "kube-system",
            policy_file = "eks/policy/aws-load-balancer-controller.json")
        # self.add_service_account(
        #     name        = "cluster-autoscaler",
        #     namespace   = "kube-system",
        #     policy_file = "eks/policy/cluster-autoscaler.json")
        # self.add_service_account(
        #     name        = "external-dns",
        #     namespace   = "kube-system",
        #     policy_file = "eks/policy/external-dns.json")
        # self.add_service_account(
        #     name        = "aws-cloudwatch-metrics",
        #     namespace   = "kube-system",
        #     managed_policies = [
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")
        #     ])
        # self.add_service_account(
        #     name        = "appmesh-controller",
        #     namespace   = "kube-system",
        #     managed_policies = [
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSAppMeshFullAccess"),
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSCloudMapFullAccess")
        #     ])
        # self.add_service_account(
        #     name        = "appmesh-application",
        #     namespace   = "kube-system",
        #     managed_policies = [
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSAppMeshEnvoyAccess"),
        #         aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSXrayWriteOnlyAccess")
        #     ])

    def add_service_account(self, name, namespace, policy_file=None, managed_policies=[]):
        # service account
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_eks/ServiceAccount.html
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
        # Helm chart into EkS Cluster
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_eks/Cluster.html
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
            "helm-metrics-server",
            repository="https://kubernetes-sigs.github.io/metrics-server/",
            chart="metrics-server",
            release="metrics-server",
            version=None, 
            create_namespace=None,
            namespace="kube-system",
            values={
                'replicas': 3,
                'topologySpreadConstraints': [
                    {
                        'maxSkew': 1,
                        'whenUnsatisfiable': 'ScheduleAnyway',
                        'labelSelector': {
                            'app.kubernetes.io/name': 'metrics-server'
                        }
                    }
                ]
            },
            timeout=None,
            wait=None)

        self.eks_cluster.add_helm_chart(
            "helm-argo-cd",
            repository="https://argoproj.github.io/argo-helm",
            chart="argo-cd",
            release="argo-cd",
            version=None,
            create_namespace=None,
            namespace="kube-system",
            values={
                'redis-ha': {
                    'enabled': True
                },
                'controller': {
                    'enableStateFulSet': True
                },
                'server': {
                    'service': {
                        'type': 'LoadBalancer'
                    },
                    'autoscaling': {
                        'enabled': True,
                        'minReplicas': 2
                    }
                },
                'repoServer': {
                    'autoscaling': {
                        'enabled': True,
                        'minReplicas': 2
                    }
                }
            },
            timeout=None,
            wait=None)

        # self.eks_cluster.add_helm_chart(
        #     "helm-argo-rollouts",
        #     repository="https://argoproj.github.io/argo-helm",
        #     chart="argo-rollouts",
        #     release="argo-rollouts",
        #     version=None,
        #     create_namespace=None,
        #     namespace="kube-system",
        #     values={
        #         'clusterInstall': False,
        #         'controller': {
        #             'replicas': 2
        #         }
        #     },
        #     timeout=None,
        #     wait=None)

        # self.eks_cluster.add_helm_chart(
        #     "helm-cluster-autoscaler",
        #     repository="https://kubernetes.github.io/autoscaler",
        #     chart="cluster-autoscaler",
        #     release="aws-cluster-autoscaler",
        #     version=None, 
        #     create_namespace=None,
        #     namespace="kube-system",
        #     values={
        #         'autoDiscovery': {
        #             'clusterName': self.eks_cluster.cluster_name,
        #         },
        #         'awsRegion': self.project['region'],
        #         'rbac': {
        #             'serviceAccount': {
        #                 'create': False,
        #                 'name': 'cluster-autoscaler'
        #             }
        #         }
        #     },
        #     timeout=None,
        #     wait=None)
        # self.eks_cluster.add_helm_chart(
        #     "helm-external-dns",
        #     repository="https://charts.bitnami.com/bitnami",
        #     chart="external-dns",
        #     release="external-dns",
        #     version=None, 
        #     create_namespace=None,
        #     namespace="kube-system",
        #     values={
        #         'serviceAccount': {
        #             'create': False,
        #             'name': 'external-dns'
        #         }
        #     },
        #     timeout=None,
        #     wait=None)
        # self.eks_cluster.add_helm_chart(
        #     "helm-aws-cloudwatch-metrics",
        #     repository="https://aws.github.io/eks-charts",
        #     chart="aws-cloudwatch-metrics",
        #     release="aws-cloudwatch-metrics",
        #     version=None, 
        #     create_namespace=None,
        #     namespace="kube-system",
        #     values={
        #         'clusterName': self.eks_cluster.cluster_name,
        #         'serviceAccount': {
        #             'create': False,
        #             'name': 'aws-cloudwatch-metrics'
        #         }
        #     },
        #     timeout=None,
        #     wait=None)
        # self.eks_cluster.add_helm_chart(
        #     "helm-appmesh-controller",
        #     repository="https://aws.github.io/eks-charts",
        #     chart="appmesh-controller",
        #     release="appmesh-controller",
        #     version=None, 
        #     create_namespace=None,
        #     namespace="kube-system",
        #     values={
        #         'serviceAccount': {
        #             'create': False,
        #             'name': 'appmesh-controller'
        #         },
        #         'tracing': {
        #             'enabled': True,
        #             'provider': 'x-ray'
        #         }
        #     },
        #     timeout=None,
        #     wait=None)