# list_namespaced_resource_api

namespace 의 resource들을(ingress, service, pod) 가지고 오는 api

Python 기반. 
Django restframework 사용. 
kubenetes에서 제공하는 api 사용. 
docker image 파일로 만들어, kubenetes를 통해 서버에 띄움.

로컬 환경에 python, pip 가 설치되어 있어아 함.
소스코드를 다운 받은 후, 
pip3 install -r pkg/pip-requirement.txt
명령어를 통해, 로컬환경 구성에 필요한 패키지 다운로드

소스 수정 후, docker image 파일로 배포 하기 위해서는 로컬환경에 docker와 kubenetes 환경이 설치되어 있어야 한다.
