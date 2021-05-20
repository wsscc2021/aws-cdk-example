'''
    Dependency: None
    IAM Role은 Corss Reference 시에 Circular Dependency 문제가 자주 생기기 떄문에
    되도록이면 적용할 서비스 스택에서 생성해주는 것이 좋습니다.
'''
from aws_cdk import (
    core, aws_iam
)

class IamStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, project: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # initial
        self.policy = dict()
        self.role = dict()

        # AWS Custom Policy
        self.policy["sample"] = aws_iam.ManagedPolicy(self, "policy-sample",
            managed_policy_name = f"{project['prefix']}-policy-sample",
            description         = "",
            statements=[
                aws_iam.PolicyStatement(
                    sid="AllowObjectInBucket",
                    effect=aws_iam.Effect.ALLOW,
                    actions=[
                        "s3:ListBucket"
                    ],
                    resources=[
                        "arn:aws:s3:::sample-bucket-asdokfk"
                    ]
                    # principals=None,
                    # conditions=None
                ),
                aws_iam.PolicyStatement(
                    sid="AllObjectActions",
                    effect=aws_iam.Effect.ALLOW,
                    actions=[
                        "s3:GetObject",
                        "s3:PutObject"
                    ],
                    resources=[
                        "arn:aws:s3:::sample-bucket-asdokfk/*"
                    ]
                    # principals=None,
                    # conditions=None
                )
            ]
        )

        # Existing Role
        self.role['team'] = aws_iam.Role.from_role_arn(self, "team",
            role_arn="arn:aws:iam::242593025403:role/AdministratorRole",
            mutable=True)
        
        # AWS Custom Role
        self.role['foo-app'] = aws_iam.Role(self, "foo-app",
            role_name   = f"{project['prefix']}-role-foo-app",
            description = "",
            assumed_by  = aws_iam.ServicePrincipal("ec2.amazonaws.com"),
            # external_id=None,
            # external_ids=None,
            inline_policies={
                "s3-read-write-object-policy": aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            sid="AllowObjectInBucket",
                            effect=aws_iam.Effect.ALLOW,
                            actions=[
                                "s3:ListBucket"
                            ],
                            resources=[
                                "arn:aws:s3:::sample-bucket-asdokfk"
                            ]
                            # principals=None,
                            # conditions=None
                        ),
                        aws_iam.PolicyStatement(
                            sid="AllObjectActions",
                            effect=aws_iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject"
                            ],
                            resources=[
                                "arn:aws:s3:::sample-bucket-asdokfk/*"
                            ]
                            # principals=None,
                            # conditions=None
                        ),
                    ]
                )
            }
            # max_session_duration=None,
            # path=None,
            # permissions_boundary=None,
            # managed_policies=[]
        )

        # Attach AWS Managed Policy
        self.role['foo-app'].add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM"))
        
        # Attach Custom Managed Policy
        self.role['foo-app'].add_managed_policy(
            self.policy['sample'])