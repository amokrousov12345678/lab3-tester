1.) Докерный образ должен поддерживать apt-get (то есть debian-подобный линух. openjdk:9 точно пойдёт, дефолтный образ с maven не тестил)

2.) После всех стадий сборки (в разделе stages) добавить

<code>
stages:<br>
  <....><br>
- testEnvInit<br>
- test<br>
</code>

3.) Добавить описания задач тестирования:

<code>
testEnvInit:<br>
  stage: testEnvInit<br>
  artifacts:<br>
    untracked: true<br>
    paths: <br>
      - lab3-tester/<br>
  script:<br>
    - apt-get update<br>
    - apt-get -y install python3<br>
    - apt-get -y install git<br>
    - git clone https://github.com/amokrousov12345678/lab3-tester<br>
    - cd lab3-tester<br>
    - python3 env_test.py<br>

test:<br>
  stage: test<br>
  dependencies:<br>
    - build<br>
    - testEnvInit<br>
  script:<br>
    - apt-get update<br>
    - apt-get -y install python3<br>
    - cd lab3-tester<br>
    - python3 env_test.py<br>
    - python3 tester.py 1 {java -cp ../  edu.amokrousov.udp_tree.Main}<br>
</code>

Вместо фигурных скобок и их содержимого необходимо написать строку запуска программы, считая, что текущий каталог repo_root/lab3-tester 
(ну то есть .. в путь надо добавить или что-то подобное)
