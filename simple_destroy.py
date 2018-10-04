#!/home/dave/tutorial/ansible/bin/python
import sys
import os
import digitalocean as do
from time import sleep
from multiprocessing import Pool, Queue
def usage():
	print 'simple.py node1 node2 ...'
	print 'export token="validtokenfrom digitalocean"'
	print 'need to run from ansible venv'
	sys.exit(1)
def create_droplet(desc):
	try:
		droplet=do.Droplet(**desc)
	except:
		print 'failed to create droplet'
		sys.exit(1)
	droplet.create()
	actions = droplet.get_actions()
	for action in actions:
		check_droplet(action)
	droplet.load()
	for k,v in droplet.__dict__.iteritems():
		print k,v
	q.put(droplet.ip_address)

def check_droplet(action):
	action.load()
	print action.status
	while( action.status != 'completed'):
		sys.stdout.write('.')
		sleep(5)
		action.load()
	
def destroy_droplet(drop):
	try:
		drop.destroy()
	except:
		'problem destroying droplet {}'.format(drop.name)	
	
	
if __name__ == '__main__':
	print 'length', len(sys.argv)
	if len(sys.argv) < 2 :
		usage()
	if not os.environ['token']:
		usage()
	token = os.environ['token']
	#print token
	names=[]
	for arg in sys.argv:
	#	print arg
		names.append(arg)
	# remove first element 'simple.py' from names list
	del names[0]
	#centos7={'name': 'node2', 'region': 'sfo2', 'size_slug': 's-1vcpu-1gb', 'token': '', 'backups': False, 'size': 's-1vcpu-1gb', 'image': 'centos-7-x64', 'ssh_keys': ''}
	#print 'updating config ... \n'
	# set name
	#centos7['name']=names[0]
	#centos7['token']=token
	#print 'getting ssh keys \n'
	# get ssh keys
	#manager = do.Manager(token=token)
	#keys = manager.get_all_sshkeys()
	#centos7['ssh_keys']=keys
	#print centos7
	q= Queue()
	#get a list of all droplets
	try:
		manager = do.Manager(token=token)
	except:
		print 'could not get a list of all droplets'
		sys.exit(1)
	do_drops=[]
	drops = manager.get_all_droplets()
	for drop in drops:
		if drop.name in names:
			do_drops.append(drop)
	print 'Found {} droplets out of {}'.format(len(do_drops), len(names))
	# create list of centos7 customized by name
	#do_configs=[]
	##for name in names:
	#	temp = dict(centos7)
	#	temp['name']= name
	#	do_configs.append(temp)
	# multi process create droplets
	p = Pool(len(do_drops))
	if do_drops:
		p.map(destroy_droplet, do_drops)
	else:
		print 'did not find any droplets to destroy!'

	# multi process check droplet status
	# write hosts file for ansible use
	#print 'writing hosts file'
	#fname = 'hosts_' + names[0]
	#with open(fname, 'w') as fd:
	#	fd.write('[digitialocean]')
	#	fd.write("\n")
	#	while not q.empty():
	#		fd.write(q.get())
	#		fd.write("\n")
	print 'done'
