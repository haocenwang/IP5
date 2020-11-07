# IP5

Installing the environment:
1. installing anaconda distribution wiht Anaconda PATH: https://www.anaconda.com/products/individual 
2. in Anaconda Propmt: 
    2.1: conda create --name installingrasa python==3.7.6
    2.2: conda install ujson
    2.3: conda install tensorflow==2.0.0
    2.4: pip install rasa
    2.5: rasa init
    2.6: if there is faliure of running rasa init: change the version that rasa requires for example numpy==1.18 or hdf5==1.10.4 etc.