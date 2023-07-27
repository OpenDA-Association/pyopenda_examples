# Example script performing a calibration using the scipy minumize function
# Author Nils van Velzen (VORtech)
#
# Note first start the server : oda_py4j.sh

import openda.utils.py4j_utils as oda_p4j
import os
from scipy.optimize import minimize

model_params = None   # Model paremeter vector. Only used for fast cloning
cost_funtion = None   # OpenDA cost function

def setup(input_dir=os.getcwd()):
    """
    Setup the OpenDA model factory, stoch observer and object function
    :param input_dir: root directory of configuration files. Location of scipt is used when not provided

    :return:
    """
    global cost_funtion
    global model_params


    #Initialize the model factory
    model_input_dir = os.path.join(input_dir, 'swanModel', 'config')
    model_config_xml = "swanStochModelConfig.xml"


    model_factory = oda_p4j.gateway.jvm.org.openda.model_swan.SwanCalibStochModelFactory()
    oda_p4j.initialize_openda_configurable(model_factory, model_input_dir, model_config_xml)

    #Initialize stoch observer
    observer_input_dir = model_input_dir = os.path.join(input_dir, 'stochObserver')
    observer_config_xml = "swanStochObsConfig.xml"

    observer = oda_p4j.gateway.jvm.org.openda.observers.IoObjectStochObserver()
    oda_p4j.initialize_openda_configurable(observer, observer_input_dir, observer_config_xml)

    #Initialize cost function org.openda.algorithms
    cost_funtion = oda_p4j.gateway.jvm.org.openda.algorithms.SimulationKwadraticCostFunction(model_factory, observer)


    #Get initial parameter
    outputLevel = oda_p4j.gateway.jvm.org.openda.interfaces.IStochModelFactory.OutputLevel.Debug
    model_ini = model_factory.getInstance(outputLevel)
    p = model_ini.getParameters()
    model_params= p



def object_function(p):
    """
    Compute the object function for parameters p
    :param p: parameters
    :return: value object function
    """

    # Create an OpenDA TreeVector with parameter value
    p_new = model_params.clone()
    j_p = oda_p4j.py_list_to_j_array(p)
    p_new.setValues(j_p)

    #Compute object function
    val = cost_funtion.evaluate(p_new, "-")

    # Debug: Some relevant output
    print ("Val="+str(val)+" p="+str(p))

    return val



def main():
    print("Hallo 1")
    global model_params
    setup()
    print("Hallo 2")

    j_p0 = model_params.clone().getValues()
    py_p0 = oda_p4j.j_array_to_py_list(j_p0)

    #results = minimize(object_function, py_p0, method='nelder-mead', options={'xtol': 1e-5, 'disp': True})
    #results = minimize(object_function, py_p0, method='powell', options={'xtol': 1e-5, 'disp': True, 'direc': [0.1, 1.0]})
    results = minimize(object_function, py_p0, method='powell', options={'xtol': 1e-5, 'disp': True})


    print("Optimal value ="+str(results.x))
    print("Done")



if __name__ == "__main__":
    main()
