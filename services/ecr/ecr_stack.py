'''
    Dependency: vpc, security_group
'''
from constructs import Construct
from aws_cdk import Stack, RemovalPolicy, aws_ecr

class EcrStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.ecr_repository = dict()
        self.ecr_repository['helloworld-app'] = aws_ecr.Repository(self, "repo-helloworld-app",
            repository_name="helloworld-app",
            image_scan_on_push=True,
            image_tag_mutability=aws_ecr.TagMutability.IMMUTABLE,
            lifecycle_registry_id=None,
            lifecycle_rules=None,
            removal_policy=RemovalPolicy.DESTROY)
