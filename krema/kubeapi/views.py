from kubernetes import client, config
from rest_framework.decorators import api_view
from rest_framework.response import Response


import json
from collections import OrderedDict


@api_view(["GET"])
def get_name_of_namespace_api(request):
    """ ## 모든 namespace의 name 정보를 배열로 리턴해주는 API ##
        params :
        return : ['defualt', 'spaceone', ...]
    """
    # config.load_kube_config()       # 로컬환경에서 테스트시 사용.
    config.load_incluster_config()  # 서버에 올릴 때 사용.

    v1 = client.CoreV1Api()  # kudenetes에서 namespace 관련 정보들을 얻을 수 있게 제공해주는 API

    ret = v1.list_namespace(watch=False)  # namespace list 가져오기.

    res_arr = []  # return data

    # namespace list parsing logic
    for item in ret.items:
        res_arr.append(item.metadata.name)      # namespace 의 name 저장

    return Response(res_arr)


@api_view(["GET"])
def get_resource_of_namespace_api(request):
    """ ## namespace의 resource 정보를 제공해주는 API ##
        * namespace의 name을 입력받는다.
        * 입력 받은 name에 대한 namespace의 resource를 리턴해준다.
        params : name
        return : {'ingresses': [], 'services': [], 'pods': []}
    """
    # config.load_kube_config()       # 로컬환경에서 테스트시 사용.
    config.load_incluster_config()    # 서버에 올릴 때 사용.

    v1 = client.CoreV1Api()  # kudenetes에서 namespace 관련 정보들을 얻을 수 있게 제공해주는 API
    extension_v1 = client.ExtensionsV1beta1Api()  # ingress에 대한 정보를 가지고 오기 위한 API

    namespace_json = OrderedDict()  # namespace json 객체 초기화

    # 필수 패러미터 validation check
    if request.query_params.get('name') is not None:
        if request.query_params.get('name') != '':
            namespace_name = request.query_params.get('name')
        else:
            return Response(namespace_json)
    else:
        return Response(namespace_json)

    # #########  namespace 별 ingress 값 parsing START ##########
    ingresses_list = extension_v1.list_namespaced_ingress(namespace_name, watch=False)  # namespace의 ingress list 불러오기
    ingresses_arr = []  # ingress 객체들을 담을 배열 초기화

    # ingresses data parsing logic
    for ing_item in ingresses_list.items:

        ingress_json = OrderedDict()  # ingress item 객체를 담을 객체 초기화

        # ingress에 대한 정보 저장
        ingress_json['name'] = ing_item.metadata.name
        ingress_json['domain_name'] = ing_item.spec.rules[0].host
        ingress_json['target_service'] = ing_item.spec.rules[0].http.paths[0].backend.service_name

        # parsing 된 json 형식의 dict data를 ingress 배열에 저장
        ingresses_arr.append(ingress_json)

    namespace_json['ingresses'] = ingresses_arr  # ingress 배열의 결과값 저장.
    # #########  namespace 별 ingress 값 parsing END ##########

    # #########  namespace 별 service 값 parsing START ##########
    services_list = v1.list_namespaced_service(namespace_name, watch=False)  # namespace의 service list 불러오기
    services_arr = []  # service 객체들을 담을 배열 초기화

    # services data parsing logic
    for ser_item in services_list.items:

        service_json = OrderedDict()  # service item 객체를 담을 객체 초기화

        # service에 대한 정보 저장
        service_json['name'] = ser_item.metadata.name
        if ser_item.spec.selector is not None:
            if 'app' in ser_item.spec.selector:
                service_json['target_pod'] = ser_item.spec.selector['app']
            else:
                service_json['target_pod'] = ''
        else:
            service_json['target_pod'] = ''

        service_json['target_port'] = ser_item.spec.ports[0].target_port
        service_json['type'] = ser_item.spec.type

        # parsing 된 json 형식의 dict data를 service 배열에 저장
        services_arr.append(service_json)

    namespace_json['services'] = services_arr  # service 배열의 결과값 저장.
    # #########  namespace 별 service 값 parsing END ##########

    # #########  namespace 별 pod 값 parsing START ##########
    pods_list = v1.list_namespaced_pod(namespace_name, watch=False)  # namespace의 pod list 불러오기
    pods_arr = []  # service 객체들을 담을 배열 초기화

    # pods data parsing logic
    for pod_item in pods_list.items:

        pod_json = OrderedDict()  # service item 객체를 담을 객체 초기화

        # pod에 대한 정보 저장
        pod_json['name'] = pod_item.metadata.name
        pod_json['status'] = pod_item.status.phase
        pod_json['source-pod'] = pod_item.metadata.labels['app']

        # parsing 된 json 형식의 dict data를 pods 배열에 저장
        pods_arr.append(pod_json)

    namespace_json['pods'] = pods_arr  # pods 배열의 결과값 저장.
    # #########  namespace 별 pod 값 parsing END ##########

    return Response(namespace_json)


@api_view(["GET"])
def kube_all_resources_api(request):
    """ ## 모든 namespace에 대한 resource 정보를 리턴해주는 API ##
        params :
        return : {
            'namespace1': {'ingresses': [], 'services': [], 'pods': []},
            'namespace2': {'ingresses': [], 'services': [], 'pods': []},
             ...
        }
    """
    # config.load_kube_config()       # 로컬환경에서 테스트시 사용.
    config.load_incluster_config()  # 서버에 올릴 때 사용.

    v1 = client.CoreV1Api()     # kudenetes에서 namespace 관련 정보들을 얻을 수 있게 제공해주는 API
    extension_v1 = client.ExtensionsV1beta1Api()    # ingress에 대한 정보를 가지고 오기 위한 API

    ret = v1.list_namespace(watch=False)    # namespace list 가져오기.

    res_json = {}   # return data

    # namespace list parsing logic
    for item in ret.items:

        namespace_json = OrderedDict()  # namespace json 객체 초기화
        namespace_name = item.metadata.name

        # #########  namespace 별 ingress 값 parsing START ##########
        ingresses_list = extension_v1.list_namespaced_ingress(namespace_name, watch=False)      # namespace의 ingress list 불러오기
        ingresses_arr = []  # ingress 객체들을 담을 배열 초기화

        # ingresses data parsing logic
        for ing_item in ingresses_list.items:
            ingress_json = OrderedDict()  # ingress item 객체를 담을 객체 초기화

            # ingress에 대한 정보 저장
            ingress_json['name'] = ing_item.metadata.name
            ingress_json['domain_name'] = ing_item.spec.rules[0].host
            ingress_json['target_service'] = ing_item.spec.rules[0].http.paths[0].backend.service_name

            # parsing 된 data를 json 형식으로 변환 후 ingress 배열에 저장
            ingresses_arr.append(ingress_json)

        namespace_json['ingresses'] = ingresses_arr  # ingress 배열의 결과값 저장.
        # #########  namespace 별 ingress 값 parsing END ##########

        # #########  namespace 별 service 값 parsing START ##########
        services_list = v1.list_namespaced_service(namespace_name, watch=False)   # namespace의 service list 불러오기
        services_arr = []  # service 객체들을 담을 배열 초기화

        # services data parsing logic
        for ser_item in services_list.items:

            service_json = OrderedDict()  # service item 객체를 담을 객체 초기화

            # service에 대한 정보 저장
            service_json['name'] = ser_item.metadata.name
            if ser_item.spec.selector is not None:
                if 'app' in ser_item.spec.selector:
                    service_json['target_pod'] = ser_item.spec.selector['app']
                else:
                    service_json['target_pod'] = ''
            else:
                service_json['target_pod'] = ''

            service_json['target_port'] = ser_item.spec.ports[0].target_port
            service_json['type'] = ser_item.spec.type

            # parsing 된 data를 json 형식으로 변환 후 service 배열에 저장
            services_arr.append(service_json)

        namespace_json['services'] = services_arr     # service 배열의 결과값 저장.
        # #########  namespace 별 service 값 parsing END ##########

        # #########  namespace 별 pod 값 parsing START ##########
        pods_list = v1.list_namespaced_pod(namespace_name, watch=False)      # namespace의 pod list 불러오기
        pods_arr = []  # service 객체들을 담을 배열 초기화

        # pods data parsing logic
        for pod_item in pods_list.items:
            pod_json = OrderedDict()  # service item 객체를 담을 객체 초기화

            # pod에 대한 정보 저장
            pod_json['name'] = pod_item.metadata.name
            pod_json['status'] = pod_item.status.phase
            pod_json['source-pod'] = pod_item.metadata.labels['app']

            # parsing 된 data를 json 형식으로 변환 후 pods 배열에 저장
            pods_arr.append(pod_json)

        namespace_json['pods'] = pods_arr  # pods 배열의 결과값 저장.
        # #########  namespace 별 pod 값 parsing END ##########

        res_json[namespace_name] = namespace_json  # parsing 된 namespace json data 저장

    return Response(res_json)