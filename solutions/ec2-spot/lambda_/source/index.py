import boto3

def handler(event, context):
    instance_id = event['detail']['instance-id']
    spot_fleet_request_id = get_spot_fleet_request_id(instance_id)
    target_groups         = get_target_groups(spot_fleet_request_id)
    deregister_targets(instance_id, target_groups)

def get_spot_fleet_request_id(instance_id):
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_instances(
            DryRun=False,
            InstanceIds=[
                instance_id,
            ]
        )
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        return next(tag['Value'] for tag in tags if tag['Key'] == 'aws:ec2spot:fleet-request-id')
    except Exception as error:
        print("Error occur describe_instances")
        print(error)

def get_target_groups(spot_fleet_request_id):
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_spot_fleet_requests(
            DryRun=False,
            SpotFleetRequestIds=[
                spot_fleet_request_id
            ]
        )
        return response['SpotFleetRequestConfigs'][0]['SpotFleetRequestConfig']['LoadBalancersConfig']['TargetGroupsConfig']['TargetGroups']
    except Exception as error:
        print("Error occur describe_spot_fleet_requests")
        print(error)

def deregister_targets(instance_id, target_groups):
    try:
        elbv2_client = boto3.client('elbv2')
        for target_group in target_groups:
            elbv2_client.deregister_targets(
                TargetGroupArn=target_group['Arn'],
                Targets=[
                    {
                        'Id': instance_id
                    },
                ]
            )
    except Exception as error:
        print("Error occur deregister_targets")
        print(error)