from constructs import Construct
from aws_cdk import (
    Stack,
    aws_apigateway,
    aws_apigatewayv2,
)

class ApiGatewayStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # apigateway - REST-API
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_apigateway/CfnRestApi.html
        aws_apigateway.CfnRestApi(self, "apigateway-rest-api",
            endpoint_configuration=aws_apigateway.CfnRestApi.EndpointConfigurationProperty(
                types=["REGIONAL"], # EDGE , REGIONAL , PRIVATE
                vpc_endpoint_ids=None),
            name="REST-API",)

        # apigatewayv2 - HTTP-API
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_apigatewayv2/CfnApi.html
        aws_apigatewayv2.CfnApi(self, "apigatewayv2-http-api",
            protocol_type="HTTP", # HTTP , WEBSOCKET
            name="HTTP-API",)