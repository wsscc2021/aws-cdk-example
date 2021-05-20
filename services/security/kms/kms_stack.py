'''
    KMS CMK는 Corss Reference 시에 Circular Dependency 문제가 자주 생기기 떄문에
    되도록이면 적용할 서비스 스택에서 생성해주는 것이 좋습니다.
'''
from aws_cdk import (
    core, aws_iam, aws_kms
)

class KmsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # init
        self.kms_key = dict()
        
        # KMS CMK for EKS
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_kms/Key.html
        self.kms_key['eks-cluster'] = aws_kms.Key(self, "eks-cluster",
            alias                    = f"alias/{project['prefix']}-eks-cluster",
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
                            aws_iam.AccountRootPrincipal(),
                            aws_iam.ArnPrincipal(arn="arn:aws:iam::242593025403:role/AdministratorRole"),
                            aws_iam.ArnPrincipal(arn="arn:aws:iam::242593025403:role/PowerUserRole")
                        ],
                        resources=["*"]
                    )
                ]
            )
        )