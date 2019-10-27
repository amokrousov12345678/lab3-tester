#because of select.poll won't work on Windows

import os
import subprocess
import time
import sys
import select
import signal

current_time_seconds = lambda: int(round(time.time()))

if (len(sys.argv)<2):
	print("Specify program executable")
	exit(1)

TESTS_DIR = "tests/"
NAME_PREFIX = "Node"
NODES_CREATION_TIMEOUT = 2
NODES_DELETION_TIMEOUT = 15
DELIVERY_WAIT_TIMEOUT = 10
POLL_TIMEOUT = 1

BASE_PORT = 2000

EXECUTABLE = sys.argv[2:]

ESUCCESS = 0
EDUPMSG = 1
ELOSTMSG = 2
EEXTRAMSG = 3
EINVALIDTEST = 4

VERBOSE = 1

nodes = {}


error_codes = {ESUCCESS: "OK", EDUPMSG: "Msg duplicated", ELOSTMSG: "Msg lost", EEXTRAMSG: "Unexpected message in output", EINVALIDTEST: "Test is invalid"}

prog_response = ""
expected_response = ""

def cleanup(nodes):
	for item in nodes:
		nodes[item].kill()

def do_test_cmd(cmd_params, nodes, fd_to_stream, fd_to_nodeid, verbosity, send_msg):
	global prog_response
	global expected_response
	if cmd_params[0]=="add" or cmd_params[0]=="add_instant":
		my_id = int(cmd_params[1])
		par_id = None
		if len(cmd_params)>=3:
			par_id = int(cmd_params[2])

		if verbosity==VERBOSE:
			if par_id!=None:
				print("	Add node "+str(my_id)+" to parent "+str(par_id)+"...", end=" ")
				sys.stdout.flush()
			else: 
				print("	Add node "+str(my_id)+"...", end=" ")
				sys.stdout.flush()

		if my_id in nodes:
			print("Attempt to create existing node,", end=" ")
			return EINVALIDTEST

		if par_id!=None and not par_id in nodes:
			print("Attempt to create node with nonexisting parent,", end=" ")
			return EINVALIDTEST

		cur_params = EXECUTABLE.copy()
		cur_params.append(NAME_PREFIX+str(my_id))
		cur_params.append(str(BASE_PORT+my_id))
		cur_params.append(str(0))

		if par_id!=None:
			cur_params.append("127.0.0.1")
			cur_params.append(str(BASE_PORT+par_id))

		nodes[my_id] = subprocess.Popen(cur_params, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
		fd_to_stream[nodes[my_id].stdout.fileno()] = nodes[my_id].stdout
		fd_to_nodeid[nodes[my_id].stdout.fileno()] = my_id

		if cmd_params[0]!="add_instant":
			time.sleep(NODES_CREATION_TIMEOUT)
	elif cmd_params[0]=="check":
		from_id = int(cmd_params[1])
		to_ids = [int(x) for x in cmd_params[2:]]

		if (verbosity==VERBOSE):
			print("	Check connectivity from node "+str(from_id)+" to ", end=" ")
			print(*(cmd_params[2:]), end=" ")
			print("...", end=" ")
			sys.stdout.flush()

		if not from_id in nodes:
				print("Attempt to check connectivity from nonexisting node,", end=" ")
				return EINVALIDTEST
		nodes[from_id].stdin.write(send_msg.encode("utf-8"))
		nodes[from_id].stdin.flush()
		expected_response = NAME_PREFIX+str(from_id)+": "+send_msg
		expected_response = expected_response.rstrip()

		poller = select.poll()

		
		for node_id in to_ids:
			if not node_id in nodes:
				print("Attempt to check connectivity to nonexisting node,", end=" ")
				return EINVALIDTEST
			poller.register(nodes[node_id].stdout, select.POLLIN)

		t2 = current_time_seconds()+DELIVERY_WAIT_TIMEOUT
		received_acks = {}
		while (current_time_seconds()<t2 and len(received_acks)!=len(to_ids)):
			poll_result = poller.poll(POLL_TIMEOUT*1000)
			for fd,event in poll_result:
				
				if(event!=select.POLLIN): 
					continue
				line = fd_to_stream[fd].readline().decode("utf-8")
				if (line[0:8]!='--------'):
					continue
				prog_response = line[8:]
				prog_response = prog_response.rstrip().rstrip('\x00')
				if (prog_response!=expected_response):
					return EEXTRAMSG
				if (fd in received_acks):
					return EDUPMSGS
				received_acks[fd] = 1
				if (verbosity):
					print("Ack from "+str(fd_to_nodeid[fd]), end=" ")
					sys.stdout.flush()

		for node_id in to_ids:
			if not nodes[node_id].stdout.fileno() in received_acks:
				return ELOSTMSG
	elif cmd_params[0]=="kill":
		node_id = int(cmd_params[1])
		if (verbosity==VERBOSE):
			print("	Kill node "+str(node_id)+"...", end=" ")
			sys.stdout.flush()
		nodes.pop(node_id).send_signal(signal.SIGINT)
		time.sleep(NODES_DELETION_TIMEOUT)
	return ESUCCESS

def check_test(fname, verbosity):
	global nodes
	nodes = {}
	fd_to_stream = {}
	fd_to_nodeid = {}
	errno = ESUCCESS
	with open(fname) as f:
		send_msg = f.readline()
		for line in f:
			cmd_params = line.split()
			verdict = do_test_cmd(cmd_params, nodes, fd_to_stream, fd_to_nodeid, verbosity, send_msg)
			if (verbosity==VERBOSE):
				print(error_codes[verdict])
				if (verdict==EEXTRAMSG):
					print("	Expected: "+str(expected_response))
					print("	Found:	"+str(prog_response))
			if (verdict!=ESUCCESS):
				errno = verdict
				break
	cleanup(nodes)
	return errno

def sig_int_callback(signum, frame):
	cleanup(nodes)
	exit(0)

def main():
	signal.signal(signal.SIGINT, sig_int_callback)
	verbosity = int(sys.argv[1])
	failed = False
	test_list = os.listdir(TESTS_DIR)
	test_list.sort()
	for entry in test_list:
		if (verbosity==VERBOSE):
			print("Processing test "+entry+"...")
		else:
			print("Processing test "+entry+"...", end =" ")
			
		sys.stdout.flush()
		verdict = check_test(TESTS_DIR+entry, verbosity)
		if not verbosity:
			print(error_codes[verdict])
		if (verdict!=ESUCCESS):
			failed = True;
	if (failed):
		exit(1)
	else:
		exit(0)
main()
