##DTAP suppport for tensorflow
set -o pipefail
SELF=$(readlink -nf $0)
export CONFIG_BASE_DIR=$(dirname ${SELF})

sudo yum -y install epel-release
sudo yum -y install python-pip
sudo yum -y install java-1.8.0-openjdk
wget https://archive.apache.org/dist/hadoop/core/hadoop-2.8.5/hadoop-2.8.5.tar.gz
mkdir -p /opt/bluedata/
cp hadoop-2.8.5.tar.gz /opt/bluedata/
cd /opt/bluedata/
tar -xvf hadoop-2.8.5.tar.gz
cd /opt/bluedata/hadoop-2.8.5
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.212.b04-0.el7_6.x86_64/
source libexec/hadoop-config.sh
cd etc/hadoop/
echo export HADOOP_CLASSPATH=$HADOOP_CLASSPATH:/opt/bluedata/bluedata-dtap.jar >> hadoop-env.sh
export JAVA_HOME=/etc/alternatives/jre
export HADOOP_HDFS_HOME=/opt/bluedata/hadoop-2.8.5
export HADOOP_HOME=/opt/bluedata/hadoop-2.8.5
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${JAVA_HOME}/lib/amd64/server:${HADOOP_HOME}/lib/native/
export PATH=$PATH:${HADOOP_HOME}/bin
export CLASSPATH=${HADOOP_HOME}/bin/hadoop classpath
echo export LD_LIBRARY_PATH=${LD_LIBRARY_PATH} >> ~/.bashrc
export HADOOP_HOME=/opt/bluedata/hadoop-2.8.5
rm -f $HADOOP_HOME/etc/hadoop/core-site.xml
cp -f ${CONFIG_BASE_DIR}/core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
echo export JAVA_HOME=/etc/alternatives/jre >> ~/.bashrc
echo export CLASSPATH=$(${HADOOP_HOME}/bin/hadoop classpath --glob) >> ~/.bashrc
echo export PATH=$PATH:${HADOOP_HOME}/bin >> ~/.bashrc
echo export HADOOP_HDFS_HOME=/opt/bluedata/hadoop-2.8.5 >> ~/.bashrc
