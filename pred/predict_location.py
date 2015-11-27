import kcnnr
import helper.dt_utils as du
import helper.data_loader as tum_dataset_loader
import numpy as np
import cPickle as pickle

def predict(test_set_x,params):
    model=kcnnr.build_model(params)
    model.build()
    wd=params["wd"]
    model_name=wd+"/"+"models"+"/"+params['model_name']
    import h5py
    #model2=pickle.load(open( model_name.replace("hdf5","pkl"), "rb" ) )
    model.load_weights(model_name)
    #dataset parameters
    im_type=params["im_type"]
    nc =params["nc"]  # number of channcels
    size =params["size"]  # size = [480,640] orijinal size,[height,width]

    # learning parameters
    batch_size =params["batch_size"]
    n_test_batches = len(test_set_x)
    ash=n_test_batches%batch_size
    if(ash>0):
        test_set_x=np.vstack((test_set_x,np.tile(test_set_x[-1],(batch_size-ash,1))))
        n_test_batches = len(test_set_x)

    n_test_batches /= batch_size
    y_pred=[]
    print "Prediction on test images"
    for i in xrange(n_test_batches):
        Fx = test_set_x[i * batch_size: (i + 1) * batch_size]
        data_Fx = du.load_batch_images(size, nc, "F", Fx,im_type)
        data_Sx = du.load_batch_images(size, nc, "S", Fx,im_type)
        if(len(y_pred)==0):
            y_pred= model.predict([data_Fx, data_Sx])
        else:
            y_pred=np.concatenate((y_pred,model.predict([data_Fx, data_Sx])))
    if(ash>0):
        y_pred= y_pred[0:-(batch_size-ash)]
    return y_pred

