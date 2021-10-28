import boto3
import time

session = boto3.session.Session(profile_name='my-session')
ec2 = session.client('ec2', region_name='us-west-2')

launch_spec = {
    'ImageId': 'ami-013a129d325529d4d', # Amazon Linux 2 AMI (HVM), SSD Volume Type
    'InstanceType': 't2.micro',
    'Placement': {
        'AvailabilityZone': 'us-west-2a',
    },
    'SecurityGroupIds': [
        'sg-************',
    ],
}

response = ec2.request_spot_instances(
    InstanceCount=1,
    LaunchSpecification=launch_spec,
    SpotPrice='0.004', # current: 0.0035
    Type='one-time',
)
request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']

while True:
    describe = ec2.describe_spot_instance_requests(SpotInstanceRequestIds=[request_id])
    print(describe['SpotInstanceRequests'][0]['Status'])
    
    code = describe['SpotInstanceRequests'][0]['Status']['Code']
    if code == 'fulfilled':
        break
        
    time.sleep(1)
