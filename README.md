# lab3-tester
Automated tester for a chat tree (laboratory work for [Network technologies](http://fit.ippolitov.me/CN_2/2019/3.html) course of [FIT NSU](https://www.nsu.ru/n/information-technologies-department/))

A chat tree should maintain connected tree structure and transfer messages using it. When some node isn't alive, connectivity should be restored automatically.
This tool executes some scripts (defined in ```TESTS_DIR``` directory) and checks if tested program works correctly (delivers messages without losses and duplication)

**Tool doesn't work on Windows, because of using ```select.poll```**

# Scripts commands
* ```add ID [PARENT]``` - add node with given integer ```ID``` (and ```PARENT``` if specified). Waits ```NODES_CREATION_TIMEOUT``` after operation
* ```add_instant ID [PARENT]``` - same as ```add``` but without waiting after operation
* ```kill ID``` - kill node. Waits ```NODES_DELETION_TIMEOUT``` after operation
* ```check ID ID1 [ID2 ID3 ...]``` - check if message sent from ```ID``` node received on ```ID1```, ```ID2``` and so on. Waits at most ```DELIVERY_WAIT_TIMEOUT```
* any other command is ignored

# How to add tool to Gitlab CI
1. Ensure that base docker image supports ```apt-get``` (openjdk:9 is ok)

2. Add the following steps at the end of ```stages``` section

````
stages:
  <....>
    - testEnvInit
    - test
````

3. Define testing steps


````
testEnvInit:  
  stage: testEnvInit  
  artifacts:  
    untracked: true  
    paths:   
      - lab3-tester/  
  script:  
    - apt-get update  
    - apt-get -y install python3  
    - apt-get -y install git  
    - git clone https://github.com/amokrousov12345678/lab3-tester  
    - cd lab3-tester  
    - python3 env_test.py  

test:  
  stage: test  
  dependencies:  
    - build  
    - testEnvInit  
  script:  
    - apt-get update  
    - apt-get -y install python3  
    - cd lab3-tester  
    - python3 env_test.py  
    - python3 tester.py 1 {java -cp ../  edu.amokrousov.udp_tree.Main}  
````
Write command to run tested program in braces, considering current directory as ```repo_root/lab3-tester``` (usually it means you need to add ```..``` to path)

4. Tested program should meet the following requirements:  
* All messages should have format ```-------Username: message``` (messages without prefix ```-------``` are ignored by tester). Prefix is defined by ```MESSAGE_PREFIX``` constant.
* Command line arguments should be in the following order: ```USERNAME LISTENPORT LOSSES PARENT_IP PARENT_PORT```
