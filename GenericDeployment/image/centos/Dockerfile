FROM bluedata/centos7:latest

# Install dTap
RUN yum install -y centos-release-scl
ADD tf_support /tmp/tf_support
ADD tf_support/libbdfs_file_system_shared_r1_14_ABI.so /opt/bluedata/
ADD tf_support/libbdfs_file_system_shared_r1_9.so /opt/bluedata/

RUN /tmp/tf_support/install_dtap.sh

RUN yum groupinstall -y 'Development Tools'

RUN wget https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-10.0.130-1.x86_64.rpm && \
    rpm -i cuda-repo-rhel7-10.0.130-1.x86_64.rpm && \
    yum  install -y cuda-toolkit-10-0

# Install Anaconda version 2019.03. Released April 5, 2019
# Anaconda installs many python ML packages
RUN wget https://repo.continuum.io/archive/Anaconda3-2019.03-Linux-x86_64.sh -P /opt && \
    chmod +x /opt/Anaconda3-2019.03-Linux-x86_64.sh && \
    /opt/Anaconda3-2019.03-Linux-x86_64.sh -b -p /opt/anaconda3  && \
    rm /opt/Anaconda3-2019.03-Linux-x86_64.sh

# Create symbolic links
RUN ln -s /opt/anaconda3/bin/pip /bin/pip3
RUN ln -s /opt/anaconda3/bin/python3 /bin/python3
RUN ln -s /opt/anaconda3/bin/conda /bin/conda

# Update conda environment
#RUN conda update --all


#Install python version 3.7 This is the common python version in Training and Deployment Environment
RUN conda install python==3.7.3 -y

# Install Tensorflow 2.1.0 with cuda 10.1. cuDNN 7.6 shall be installed. Tensorflow-metadata and gast are required packages for later installations.
RUN conda install -c anaconda tensorflow-gpu==2.1.0 cudatoolkit==10.1.243  gast==0.2.2 -y

# Install Keras, Theano, and PyTorch
#RUN conda install -c conda-forge apache-beam==2.14.0 -y
RUN conda install -c conda-forge keras==2.3.0
RUN conda install -c conda-forge theano==1.0.4
RUN conda install -c pytorch pytorch==1.4.0 -y
RUN conda install -c pytorch torchvision -y
RUN pip3 install xgboost==1.3.3

# Install some of the packages that do not come bundled with Anaconda
RUN conda install numpy==1.18.1 -y # downgrade numpy to prevent tensorflow FutureWarnings
RUN conda install plotly==4.7.1 -y
RUN conda install scipy==1.4.1 -y 
RUN conda install -c anaconda flask==1.0.2 -y
RUN conda install -c anaconda dill==0.3.1.1 -y

RUN conda install -c conda-forge statsmodels==0.11.1 scikit-learn==0.22.1 pandas==1.0.1 -y

# Install tensorflow libraries not a part of conda using pip. The versions are frozen to 0.21.0 as they are the latest versions that support TF 2.1.0. scipy is downgraded to version 1.2.2 after this step. Uncomment these after right package installer version is available
#RUN pip3 install tensorflow-data-validation==0.21.0
#RUN pip3 install tensorflow-transform==0.21.0
#RUN pip3 install tensorflow-model-analysis==0.21.1
#RUN pip3 install tensorflow-metadata==0.21.0

### Changes for including flask in the Inference Engine
RUN conda install -c conda-forge gunicorn==19.9.0 
RUN conda install -c conda-forge mysql-connector-python
RUN conda install -c conda-forge tinydb
RUN ln -s /opt/anaconda3/bin/gunicorn /bin/gunicorn
RUN conda install -c conda-forge python-dotenv -y
RUN conda install -c anaconda boto3=1.17.46 -y
# create a directory for storing all the files
RUN mkdir /usr/lib/mysql_files
ADD mysql-init /usr/lib/mysql_files/mysql-init

# install mysql server
RUN wget http://repo.mysql.com/mysql80-community-release-el7.rpm --directory-prefix=/usr/lib/
RUN sudo -E rpm -ivh /usr/lib/mysql80-community-release-el7.rpm
RUN yum -y install mysql-community-server && cp /var/log/mysqld.log /usr/lib/mysql_files/mysqld.log

RUN yum -y install haproxy

#install 2to3 and move the appconfig scripts inside the image
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip install 2to3
#COPY flask_configure.tgz /opt/configscript/flask_configure.tgz

# Copy Appconfig scripts from github repo and branch

# Github token
ARG TOKEN 

# Work directory eg: K8s-Mlops/JupyterHubNotebook
ARG WORKDIR

# github repo eg: github.hpe.com/saurabh-jogalekar/bluedata-catalog.git
ARG GITREPO

# branch
ARG BRANCH="master"

# we clone repo to /tmp/appconfig. Then, compress the workdir/appconfig directory. Copy the appconfig to appropriate location and delete the cloned repo.
RUN git clone https://${TOKEN}@${GITREPO} -b ${BRANCH} /tmp/appconfig && \
mkdir -p /opt/configscript && \
cd /tmp/appconfig/${WORKDIR} && \
tar -czf /opt/configscript/flask_configure.tgz flask_configure/ && \
rm -rf /tmp/appconfig && \
chmod 755 /opt/configscript/flask_configure.tgz
