import boto3

def handler(event, context):
    instance_id = event['detail']['instance-id']
    spotfleet_request_id = get_spot_fleet_request_id(instance_id)
    target_groups        = get_target_groups(spotfleet_request_id)
    deregister_targets(instance_id, target_groups)


def get_spot_fleet_request_id(instance_id):
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_instances(
            Filters=None,
            InstanceIds=[
                instance_id,
            ],
            DryRun=False,
            MaxResults=123,
            NextToken=None,
        )
        return response['Reservations'][0]['Instances'][0]['SpotInstanceRequestId']
    except Exception as error:
        print("Error occur describe_instances")
        print(error)

def get_target_groups(spot_fleet_request_id):
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_spot_fleet_requests(
            DryRun=False,
            MaxResults=123,
            NextToken=None,
            SpotFleetRequestIds=[
                spot_fleet_request_id,
            ]
        )
        return response['SpotFleetRequestConfigs'][0]['LoadBalancersConfig']['TargetGroupsConfig']['TargetGroups']
    except Exception as error:
        print("Error occur describe_spot_fleet_requests")
        print(error)

def deregister_targets(instance_id, target_groups):
    try:
        elbv2_client = boto3.client('elbv2')
        for target_group in target_groups:
            elbv2_client.deregister_targets(
                TargetGroupArn=target_group['arn'],
                Targets=[
                    {
                        'Id': instance_id
                    },
                ]
            )
    except Exception as error:
        print("Error occur deregister_targets")
        print(error)