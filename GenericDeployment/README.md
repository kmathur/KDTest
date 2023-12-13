Files for Kubedirector Deployment Engine app 

Contains the following:
1. Appconfig scripts to be packaged. 

2. Image directory container dockerfile, to build image.
 
3. cr-app-deployment-engine.json for launching kubedirectorapp. Referencing catalog.json from kubedirector 5.0 
https://github.com/bluek8s/kubedirector/blob/v0.5.0/deploy/example_catalog/cr-app-deployment-engine.json
 
4. cr-cluster-endpoint-wrapper.yaml to launch k8s virtual cluster. Referencing cluster.yaml fro kubedirector 5.0
https://github.com/bluek8s/kubedirector/blob/v0.5.0/deploy/example_clusters/cr-cluster-endpoint-wrapper.yaml


This is a Generic API Wrapper (as dependent distro to trainng and deployment images). It is loadbalanced and comes up with token authentication.
1. FIX INDENTATION
2. Think about Async as optional
3. Put training metadata and serving url in configmeta.
4. Gunicorn server error file
5. API spec finetune and give url for posting as part of deployment
6. Add queue for round robin request on compute
7. Gunicorn multiple workers and threads (based on vCPUs)
8. Expand and shrink with Haproxy (haproxy -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -sf $(cat /var/run/haproxy.pid) 
9. Cleanup of files and DB after use
10. if server crashes then errors
11. catalog api version
12. Latest 2to3 package installation 

Supports kubedirector 5.0 and above.
