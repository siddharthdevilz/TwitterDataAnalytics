
import boto
import time
from boto.ec2.regioninfo import RegionInfo

region=RegionInfo(name='melbourne', endpoint='nova.rc.nectar.org.au')
ec2_connection = boto.connect_ec2(aws_access_key_id='04478e91abec4434b19df3a46e0ea02c', aws_secret_access_key='6b6d5686e6fb4246a16c55aa7f4eb4f6', is_secure=True, 
	region=region, port=8773, path='/services"})/Cloud', validate_certs=False)

VM_IPs = []
volume_IDs = []
print("connection is successed!")

def verify_group_status(groupname):
	check = False
	group = ec2_connection.get_all_security_groups()
	for g in group:
	    if g.name == groupname:
	        check = True
	return check

def create_volume():
    for k in range(4):
	    ec2_connection.create_volume(50,"melbourne-qh")

def create_instance(num_of_instance):
	count = num_of_instance
	for i in range(count):
		ec2_connection.run_instances('ami-000037b9', key_name='tweetbrand', placement='melbourne',instance_type='m1.small', security_groups=['http','ssh'])

def verify_state():
	print("Start creating instances")
	create_instance(4)
	current_volume = ec2_connection.get_all_volumes()
	for vol in current_volume:
	    volume_IDs.append(vol.id)
	reservations = ec2_connection.get_all_reservations()
	for i in range(len(reservations)):
		instance = reservations[i].instances[0]
		instance_state = reservations[i].instances[0].update()
		while instance_state == 'pending':
			time.sleep(30)
			print("Instance%s is %s" %(i,instance_state))
			instance_state = reservations[i].instances[0].update()
		if instance_state == 'running':
			instance.add_tag("Name","Instance%s"%i)
			VM_IPs.append(instance.ip_address)
			print("Instance %s is now ready to use" %i)
		else:
			print('Instance %s instance_state:' %i + instance_state)		

def printing_host():
    info = '\n'.join(VM_IPs)
    path = '/Users/sunshine/desktop/Nectarhost'
    user = 'ansible_user=ubuntu'
    key = 'ansible_private_key_file=/Users/sunshine/Desktop/tweetbrand.pem'

create_volume()
verify_state()
printing_host()
print("Successful!")