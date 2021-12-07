import boto3
import time

session = boto3.session.Session(profile_name='dev-session')
ec2 = session.client('ec2', region_name='us-east-1')

ami_us_west_2 = 'ami-013a129d325529d4d'
ami_ap_northeast_2 = 'ami-0e4a9ad2eb120e054'
ami_us_east_1 = 'ami-0ed9277fb7eb570c9'

launch_spec = {
    'ImageId': ami_us_east_1, # Amazon Linux 2 AMI (HVM), SSD Volume Type
    'InstanceType': 'inf1.xlarge',
    'Placement': {
        'AvailabilityZone': 'us-east-1a',
    }
}

response = ec2.request_spot_instances(
    InstanceCount=1,
    LaunchSpecification=launch_spec,
    SpotPrice='0.1', # Current Price: 0.0965 (us-east-1a)
    Type='one-time',
)

request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
time.sleep(1) # sleep for waiting settings
describe = ec2.describe_spot_instance_requests(SpotInstanceRequestIds=[request_id])
code = describe['SpotInstanceRequests'][0]['Status']['Code']
print(code)

while True:
    # get current status of spot request
    describe = ec2.describe_spot_instance_requests(SpotInstanceRequestIds=[request_id])
    
    # if code was changed, print code
    if code != describe['SpotInstanceRequests'][0]['Status']['Code']:
        code = describe['SpotInstanceRequests'][0]['Status']['Code']
        print(code)
    
    # if code is "price-too-low", cancel and break
    if code == 'price-too-low':
        print("Cancel Spot Request")
        cancel_state = ec2.cancel_spot_instance_requests(SpotInstanceRequestIds=[request_id])
        print(cancel_state)
        break

    # if code is "fulfilled", cancel and break
    if code == 'fulfilled':
        instance_id = describe['SpotInstanceRequests'][0]['InstanceId']
        print("Terminate Spot Instance")
        terminate_status = ec2.terminate_instances(InstanceIds=[instance_id])
        print(terminate_status)
        print("Cancel Spot Request")
        cancel_state = ec2.cancel_spot_instance_requests(SpotInstanceRequestIds=[request_id])
        print(cancel_state)
        break
