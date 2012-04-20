'''
Created on 18.04.2012

@author: Mathias
'''
import numpy as np
import time
from Devices.TranslationalStage_3Axes import TranslationalStage_3Axes
from Devices.Thorlabs_PM100D import Thorlabs_PM100D

def find_vertical_max_jog(power_meter, stage, intensity_treshold=1e-5):
    negative_slope = False
    a = np.array([])
    std = np.array([])
    # this is just searching into the upwards direction
    tmp = np.array([])
    for i in range(0,10):
        tmp = np.append(tmp, power_meter.getPower())
    a = np.append(a, np.average(tmp))
    std= np.append(std,np.std(tmp))
    
    t = time.time()    
    while not negative_slope and (time.time()-t) < 20:
        tmp = np.array([])
        stage.AG_UC2_2.jog(1, 1)
        for i in range(0,10):
            tmp = np.append(tmp, power_meter.getPower())
        std = np.append(std,np.std(tmp))
        a = np.append(a, np.average(tmp))
        if a[-1]+std[-1] < a[-2] and a[-1] > intensity_treshold:
            negative_slope = True
    stage.AG_UC2_2.stop_jog(1)
    
def find_horizontal_max_jog(power_meter, stage, intensity_treshold=1e-5):
    negative_slope = False
    a = np.array([])
    std = np.array([])
    # this is just searching into the upwards direction
    tmp = np.array([])
    for i in range(0,10):
        tmp = np.append(tmp, power_meter.getPower())
    a = np.append(a, np.average(tmp))
    std= np.append(std,np.std(tmp))
    t = time.time()    
    while not negative_slope and (time.time()-t) < 20:
        tmp = np.array([])
        stage.AG_UC2_1.jog(1, 1)
        for i in range(0,10):
            tmp = np.append(tmp, power_meter.getPower())
        std = np.append(std,np.std(tmp))
        a = np.append(a, np.average(tmp))
        if a[-1]+std[-1] < a[-2] and a[-2] > intensity_treshold:
            negative_slope = True
    stage.AG_UC2_1.stop_jog(1)
    
def move_along_maximum(power_meter, stage, intensity_treshold=1e-5):
    '''
    Please position the fiber tip to Intensity maximum manually first.
    move with the manual stage a little away from the limits so the scan has a wider range
    to move to
    '''
    stage.AG_UC2_2.move_to_limit(1,-2)
    a = np.array([])
    std = np.array([])
    height = np.array([])

    for i in xrange(0,100):
        h, mean, stdev = find_vertical_max(power_meter, stage, 1e-5)
        a = np.append(a, mean)
        std= np.append(std,stdev)
        height = np.append(height, h)
        stage.backwards(1)
    return height, a, std


def find_vertical_max(power_meter, stage, intensity_treshold = 1e-6):
    positive_slope = True
    a = np.array([])
    std = np.array([])
    counter = 0    
    
    mean, stdev, var = take_averaged_measurement(power_meter)
    a = np.append(a, mean)
    std= np.append(std,stdev)
    
    t = time.time()    
    while positive_slope and (time.time()-t) < 15:
        stage.up(1)
        counter += 1
        mean, stdev, var = take_averaged_measurement(power_meter)
        a = np.append(a, mean)
        std = np.append(std,stdev)
        if a[-1]+std[-1] < a[-2] and a[-2] > intensity_treshold:
            stage.down(1)
            counter -= 1
            positive_slope = False

    if counter == 0:
        positive_slope=True
        t = time.time()    
        while positive_slope and (time.time()-t) < 15:
            stage.down(1)
            counter -= 1
            mean, stdev, var = take_averaged_measurement(power_meter)
            a = np.append(a, mean)
            std = np.append(std,stdev)
            if a[-1]+std[-1] < a[-2] and a[-2] > intensity_treshold:
                stage.up(1)
                counter += 1
                positive_slope = False
            
    return counter, a[-1], std[-1] # return height change, power, standard deviation

def find_horizontal_max(power_meter, stage, intensity_treshold = 1e-6):
    positive_slope = True
    a = np.array([])
    std = np.array([])
    counter = 0    
    
    mean, stdev, var = take_averaged_measurement(power_meter)
    a = np.append(a, mean)
    std= np.append(std,stdev)
    
    t = time.time()    
    while positive_slope and (time.time()-t) < 30:
        stage.left(1)
        counter += 1
        mean, stdev, var = take_averaged_measurement(power_meter)
        a = np.append(a, mean)
        std = np.append(std,stdev)
        if a[-1]+std[-1] < a[-2] and a[-2] > intensity_treshold:
            stage.right(1)
            counter -= 1
            positive_slope = False

    if counter == 0:
        positive_slope=True
        t = time.time()    
        while positive_slope and (time.time()-t) < 30:
            stage.right(1)
            counter -= 1
            mean, stdev, var = take_averaged_measurement(power_meter)
            a = np.append(a, mean)
            std = np.append(std,stdev)
            if a[-1]+std[-1] < a[-2] and a[-2] > intensity_treshold:
                stage.left(1)
                counter += 1
                positive_slope = False
            
    return counter, a[-1], std[-1] # return height change, power, standard deviation

def take_averaged_measurement(power_meter):
    tmp = np.array([])
    for i in xrange(0,10):
        tmp = np.append(tmp, power_meter.getPower())
    return np.mean(tmp), np.std(tmp), np.var(tmp)    
           

    
    