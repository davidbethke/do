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
    q.put((droplet.name, droplet.ip_address))

def check_droplet(action):
    action.load()
    print action.status
    while( action.status != 'completed'):
        sys.stdout.write('.')
        sleep(5)
        action.load()
    print action.status
    
    
    
    
if __name__ == '__main__':
    print 'length', len(sys.argv)
    if len(sys.argv) < 2 :
        usage()
    if not os.environ['token']:
        usage()
    token = os.environ['token']
    print token
    names=[]
    for arg in sys.argv:
    #   print arg
        names.append(arg)
    # remove first element 'simple.py' from names list
    del names[0]
    centos7={'name': 'node2', 'region': 'sfo2', 'size_slug': 's-1vcpu-1gb', 'token': '', 'backups': False, 'private_networking': True, 'size': 's-1vcpu-1gb', 'image': 'centos-7-x64', 'ssh_keys': ''}
    print 'updating config ... \n'
    # set name
    centos7['name']=names[0]
    centos7['token']=token
    print 'getting ssh keys \n'
    # get ssh keys
    manager = do.Manager(token=token)
    keys = manager.get_all_sshkeys()
    centos7['ssh_keys']=keys
    #print centos7
    q= Queue()
    # create list of centos7 customized by name
    do_configs=[]
    for name in names:
        temp = dict(centos7)
        temp['name']= name
        if 'master' in name:
            temp['size_slug']= 's-2vcpu-2gb'
        do_configs.append(temp)
    # multi process create droplets
    p = Pool(len(do_configs))
    p.map(create_droplet, do_configs)

    # multi process check droplet status
    # write hosts file for ansible use
    print 'writing hosts file'
    fname = 'hosts_' + names[0]
    with open(fname, 'w') as fd:
        fd.write('[workers]')
        fd.write("\n")
        while not q.empty():
            #fd.write(q.get())
            name, ip = q.get()
            fd.write(" {0} ansible_host={1} ansible_user=root ansible_ssh_private_key_file=/home/dave/.ssh/id_rsa_do".format(name, ip))
            fd.write("\n")
        fd.write("[masters]\n")
    print 'done'
    
''' 
    # create droplet
    print 'creating droplet ...\n'
    droplet= do.Droplet(**centos7)
    droplet.create()    

    # check status
    print 'checking status ... \n'
    actions = droplet.get_actions()
    for action in actions:
        action.load()
        while( action.status != 'completed'):
            print action.status
            print '\n'
            sleep(5)
            action.load()
'''
