import boto3

def handler(event, context):
    instance_id = event['detail']['instance-id']
    spot_fleet_request_id, auto_scaling_group_name = describe_instance(instance_id)
    target_group_arns = get_target_group_arns(spot_fleet_request_id, auto_scaling_group_name)
    deregister_targets(instance_id, target_group_arns)

def describe_instance(instance_id):
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_instances(
            DryRun=False,
            InstanceIds=[
                instance_id,
            ]
        )
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        spot_fleet_request_id   = ''.join([ tag['Value'] for tag in tags if tag['Key'] == 'aws:ec2spot:fleet-request-id' ])
        auto_scaling_group_name = ''.join([ tag['Value'] for tag in tags if tag['Key'] == 'aws:autoscaling:groupName' ])
        return spot_fleet_request_id, auto_scaling_group_name
    except Exception as error:
        print("Error occur describe_instances")
        print(error)

def get_target_group_arns(spot_fleet_request_id, auto_scaling_group_name):
    try:
        if spot_fleet_request_id:
            ec2_client = boto3.client('ec2')
            response = ec2_client.describe_spot_fleet_requests(
                DryRun=False,
                SpotFleetRequestIds=[
                    spot_fleet_request_id
                ]
            )
            return [ target_group['Arn'] for target_group in 
                response['SpotFleetRequestConfigs'][0]['SpotFleetRequestConfig']['LoadBalancersConfig']['TargetGroupsConfig']['TargetGroups'] ]
        elif auto_scaling_group_name:
            asg_client = boto3.client('autoscaling')
            response = asg_client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[
                    auto_scaling_group_name,
                ]
            )
            return response['AutoScalingGroups'][0]['TargetGroupARNs']
        else:
            return None
    except Exception as error:
        print("Error occur describe_spot_fleet_requests")
        print(error)

def deregister_targets(instance_id, target_group_arns):
    try:
        elbv2_client = boto3.client('elbv2')
        for target_group_arn in target_group_arns:
            elbv2_client.deregister_targets(
                TargetGroupArn=target_group_arn,
                Targets=[
                    {
                        'Id': instance_id
                    },
                ]
            )
    except Exception as error:
        print("Error occur deregister_targets")
        print(error)