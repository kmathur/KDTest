import tensorflow as tf
import os
from tensorflow.python.framework.versions import CXX11_ABI_FLAG

CXX11_ABI_FLAG

#bdfs
bdfs_file_system_library = os.path.join("/opt/bluedata","libbdfs_file_system_shared_r1_9.so")
tf.load_file_system_library(bdfs_file_system_library)

with tf.gfile.Open("dtap://TenantStorage/tmp/tensorflow/dtap.txt", 'w') as f:
    f.write("This is the dtap test file")

with tf.gfile.Open("dtap://TenantStorage/tmp/tensorflow/dtap.txt", 'r') as f:
    content = f.read()

