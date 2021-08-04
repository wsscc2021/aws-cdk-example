'''
    Dependency: None
    If you will create KMS cmk object, you must create it in each service stack that using role.
    Otherwise it occur error of circular dependency.
'''
from constructs import Construct
from aws_cdk import Stack, Duration, RemovalPolicy, aws_iam, aws_kms

class KmsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Init
        self.kms_key = dict()
        # KMS CMK for EKS
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_kms/Key.html
        self.kms_key['eks-cluster'] = aws_kms.Key(self, "eks-cluster",
            alias                    = f"alias/{project['prefix']}-eks-cluster",
            description              = "",
            admins                   = None,
            enabled                  = True,
            enable_key_rotation      = True,
            pending_window           = Duration.days(7),
            removal_policy           = RemovalPolicy.DESTROY,
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