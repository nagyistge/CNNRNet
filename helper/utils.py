import numpy
import theano
import theano.tensor as T
import os
import glob
from PIL import Image
import datetime
import numpy as np

def init_W_b(W, b, rng, n_in, n_out):
    # for a discussion of the initialization, see
    # https://plus.google.com/+EricBattenberg/posts/f3tPKjo7LFa
    if W is None:
        W_values = numpy.asarray(
            rng.uniform(
                low=-numpy.sqrt(6./(n_in + n_out)),
                high=numpy.sqrt(6./(n_in + n_out)),
                size=(n_in, n_out)
                ),
            dtype=theano.config.floatX
        )
        W = theano.shared(value=W_values, name='W', borrow=True)

    # init biases to positive values, so we should be initially in the linear regime of the linear rectified function
    if b is None:
        b_values = numpy.ones((n_out,), dtype=theano.config.floatX) * numpy.cast[theano.config.floatX](0.01)
        b = theano.shared(value=b_values, name='b', borrow=True)
    return W, b


def init_CNNW_b(W, b, rng, n_in, n_out,fshape):
    # for a discussion of the initialization, see
    # https://plus.google.com/+EricBattenberg/posts/f3tPKjo7LFa
    if W is None:
        W_values = numpy.asarray(
            rng.uniform(
                low=-numpy.sqrt(6./(n_in + n_out)),
                high=numpy.sqrt(6./(n_in + n_out)),
                size=(n_in, n_out)
                ),
            dtype=theano.config.floatX
        )
        W = theano.shared(value=W_values, name='W', borrow=True)

    # init biases to positive values, so we should be initially in the linear regime of the linear rectified function
    if b is None:
        b_values = numpy.ones((fshape,), dtype=theano.config.floatX) * numpy.cast[theano.config.floatX](0.01)
        b = theano.shared(value=b_values, name='b', borrow=True)
    return W, b

rng = numpy.random.RandomState(1234)
srng = T.shared_randomstreams.RandomStreams(rng.randint(999999))

def drop(input, p=0.5, rng=rng):
    """
    :type input: numpy.array
    :param input: layer or weight matrix on which dropout resp. dropconnect is applied

    :type p: float or double between 0. and 1.
    :param p: p probability of NOT dropping out a unit or connection, therefore (1.-p) is the drop rate.

    """
    mask = srng.binomial(n=1, p=p, size=input.shape, dtype=theano.config.floatX)
    return input * mask

def rescale_weights(params, incoming_max):
    incoming_max = numpy.cast[theano.config.floatX](incoming_max)
    for p in params:
        w = p.get_value()
        w_sum = (w**2).sum(axis=0)
        w[:, w_sum>incoming_max] = w[:, w_sum>incoming_max] * numpy.sqrt(incoming_max) / w_sum[w_sum>incoming_max]
        p.set_value(w)

def up_sample(overlaps,data_y,step_size):
    data_yy=[]
    for index in range(len(overlaps)):
        value= sum(numpy.asarray(data_y)[overlaps[index]]) / (step_size * len(overlaps[index]))
        data_yy.append(value)
    return numpy.asarray(data_yy)

def convert_to_grayscale(params):
    for dir in params["dataset"]:
        im_type='rgb'
        im_type_to='gray'
        new_dir=dir+im_type_to+"/"
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            full_path=dir+'/'+im_type+'/*.png'
            lst=glob.glob(full_path)
            for f in lst:
                img = Image.open(f).convert('L')
                img.save(new_dir+os.path.basename(f))
            print("data set converted %s"%(dir))
        else:
            print("data set has already converted %s"%(dir))


def start_log(datasets,params):
    log_file=params["log_file"]
    create_file(log_file)

    X_train, y_train,overlaps_train = datasets[0]
    X_val, y_val,overlaps_val = datasets[1]
    X_test, y_test,overlaps_test = datasets[2]
    y_train_mean=np.mean(y_train)
    y_train_abs_mean=np.mean(np.abs(y_train))
    y_val_mean=np.mean(y_val)
    y_val_abs_mean=np.mean(np.abs(y_val))
    y_test_mean=np.mean(y_test)
    y_test_abs_mean=np.mean(np.abs(y_test))
    ds= get_time()


    log_write("Batch size: %s"%(params['batch_size']),params)
    log_write("Images are cropped to: %s"%(params['size']),params)
    log_write("Dataset splits: %s"%(params["step_size"]),params)
    log_write("Image type: %s"%(params["im_type"]),params)
    log_write("List of dataset used:",params)
    for dir in params["dataset"]:
        log_write(dir,params)

    log_write("Starting Time:%s"%(ds),params)
    log_write("size of training data:%f"%(len(X_train)),params)
    log_write("size of val data:%f"%(len(X_val)),params)
    log_write("size of test data:%f"%(len(X_test)),params)
    log_write("Mean of training data:%f, abs mean: %f"%(y_train_mean,y_train_abs_mean),params)
    log_write("Mean of val data:%f, abs mean: %f"%(y_val_mean,y_val_abs_mean),params)
    log_write("Mean of test data:%f, abs mean: %f"%(y_test_mean,y_test_abs_mean),params)


def get_time():
    return str(datetime.datetime.now().time()).replace(":","_").replace(".","_")

def create_file(log_file):
    log_dir= os.path.dirname(log_file)
    if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    if(os.path.isfile(log_file)):
        with open(log_file, "w"):
            pass
    else:
        os.mknod(log_file)

def log_to_file(str,params):
    with open(params["log_file"], "a") as log:
        log.write(str)


def log_write(str,params):
    print(str)
    ds= get_time()
    str=ds+" | "+str+"\n"
    log_to_file(str,params)