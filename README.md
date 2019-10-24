1.) Докерный образ должен поддерживать apt-get (то есть debian-подобный линух. openjdk:9 точно пойдёт, дефолтный образ с maven не тестил)

2.) После всех стадий сборки (в разделе stages) добавить

````
stages:
  <....>
    - testEnvInit
    - test
````

3.) Добавить описания задач тестирования:


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
Вместо фигурных скобок и их содержимого необходимо написать строку запуска программы, считая, что текущий каталог repo_root/lab3-tester 
(ну то есть .. в путь надо добавить или что-то подобное)
4.) Требования к программе:  
*печатать сообщения в виде -------Username: message  
*сообщения без префикса ------- игнорируются (но если будет очень много мусора, тестер может подавиться)  
*параметры: USERNAME LISTENPORT LOSSES PARENT_IP PARENT_PORT  
