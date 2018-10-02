#%cd "C:/Users/shbhu/Documents/Git/Py_mass_radius_working/PyCode"
import numpy as np
from scipy.stats import beta,norm
from scipy.integrate import quad
from scipy.optimize import brentq as root
from astropy.table import Table
from scipy.optimize import minimize, fmin_slsqp
from multiprocessing import Pool,cpu_count
import os
import sys
import datetime
from shutil import copyfile

sys.path.append(os.path.dirname(__file__))
from MLE_fit import MLE_fit


t = Table.read(os.path.join(os.path.dirname(__file__),'MR_Kepler_170605_noanalytTTV_noupplim.csv'))
t = t.filled()

M_sigma = (abs(t['pl_masseerr1']) + abs(t['pl_masseerr2']))/2
R_sigma = (abs(t['pl_radeerr1']) + abs(t['pl_radeerr2']))/2

M_obs = np.array(t['pl_masse'])
R_obs = np.array(t['pl_rade'])

# bounds for Mass and Radius
Radius_min = -0.3
Radius_max = np.log10(max(R_obs) + np.std(R_obs)/np.sqrt(len(R_obs)))
Mass_min = np.log10(max(min(M_obs) - np.std(M_obs)/np.sqrt(len(M_obs)), 0.1))
Mass_max = np.log10(max(M_obs) + np.std(M_obs)/np.sqrt(len(M_obs)))
num_boot = 100
#select_deg = 5

data = np.vstack((M_obs,R_obs)).T
sigma = np.vstack((M_sigma,R_sigma)).T

bounds = np.array([Mass_max,Mass_min,Radius_max,Radius_min])
Log = True



def bootsample_mle(inputs):
    '''
    To bootstrap the data and run MLE
    Input:
        dummy : Variable required for mapping for parallel processing
    '''

    MR_boot = MLE_fit(data = inputs[0], sigma = inputs[1], bounds = inputs[2], Log = inputs[3], deg = inputs[4], abs_tol = inputs[5], location = inputs[6])
    #MR_boot = MLE_fit(data = data_boot, bounds = bounds, sigma = data_sigma, Log = Log, deg = deg_choose)

    return MR_boot


    

def MLE_fit_bootstrap(data, sigma, Mass_max = None, Mass_min = None, Radius_max = None, Radius_min = None, degree = 60, select_deg = 55,
            Log = False, k_fold = 10, num_boot = 100, store_output = False, cores = cpu_count(),location = os.path.dirname(__file__), abs_tol = 1e-10):
    '''
    Predict the Mass and Radius relationship
    INPUT:
                
        data: the first column contains the mass measurements and 
             the second column contains the radius measurements.
        sigma: measurement errors for the data, if no measuremnet error, 
                    it is NULL
        Mass_max: the upper bound for mass. Default = None
        Mass_min: the lower bound for mass. Default = None
        Radius_max: the upper bound for radius. Default = None
        Radius_min: the upper bound for radius. Default = None
        degree: the maximum degree used for cross-validation/AIC/BIC. Default = 60
        select_deg: if input "cv": cross validation
                            if input "aic": aic method
                            if input "bic": bic method
                            if input a number: default using that number and 
                            skip the select process 
        Log: is the data transformed into a log scale if Log = True. Default = False
        k_fold: number of fold used for cross validation. Default = 10
        num_boot: number of bootstrap replication. Default = 100
        store_output: store the output into csv files if True. Default = False
        cores: this program uses parallel computing for bootstrap. Default = 1
        abs_tol : Defined for integration in MLE_fit()
      
    '''
    starttime = datetime.datetime.now()
    print('Started for {} degrees at {}, using {} cores'.format(select_deg, starttime, cores))
    
    if not os.path.exists(location):
        os.mkdir(location)   
        
    with open(os.path.join(location,'log_file.txt'),'a') as f:
       f.write('Started run at {}\n'.format(starttime))
    f.close()
    
    copyfile(os.path.join(os.path.dirname(location),os.path.basename(__file__)), os.path.join(location,os.path.basename(__file__)))
    copyfile(os.path.join(os.path.dirname(location),'MLE_fit.py'), os.path.join(location,'MLE_fit.py'))
    
    n = np.shape(data)[0]
    M = data[:,0]
    R = data[:,1]
      
    sigma_M = sigma[:,0]
    sigma_R = sigma[:,1]
    
    if len(M) != len(R):
        print('Length of Mass and Radius vectors must be the same')
    if len(M) != len(sigma_M) and (sigma_M is not None):
        print('Length of Mass and Mass sigma vectors must be the same')
    if len(R) != len(sigma_R) and (sigma_R is not None):
        print('Length of Radius and Radius sigma vectors must be the same')
        
    if Mass_min is None:
        Mass_min = np.min(M) - np.max(sigma_M)/np.sqrt(n)
    if Mass_max is None:
        Mass_max = np.max(M) + np.max(sigma_M)/np.sqrt(n)    
    if Radius_min is None:
        Radius_min = np.min(R) - np.max(sigma_R)/np.sqrt(n)
    if Radius_max is None:
        Radius_max = np.max(R) + np.max(sigma_R)/np.sqrt(n) 
        
    bounds = np.array([Mass_max,Mass_min,Radius_max,Radius_min])

    ###########################################################
    ## Step 1: Select number of degree based on cross validation, aic or bic methods.
    
    degree_candidate = np.arange(5, degree, 5)
    deg_length = len(degree_candidate)
        
    if select_deg == 'aic' : 
        aic = np.array([MLE_fit(data = data, bounds = bounds, sigma = sigma, Log = Log, deg = d, abs_tol = abs_tol)['aic'] for d in range(2,degree)])
        deg_choose = np.nanmin(aic)

    elif select_deg == 'bic':
        bic = np.array([MLE_fit(data = data, bounds = bounds, sigma = sigma, Log = Log, deg = d, abs_tol = abs_tol)['bic'] for d in range(2,degree)])
        deg_choose = np.nanmin(bic)   
                 
    elif isinstance(select_deg, (int,float)):
        deg_choose = select_deg
    
    else : 
        print('Error: Incorrect input for select_deg')
            
    ###########################################################
    ## Step 2: Estimate the model
            
    print('Running full dataset MLE before bootstrap')        
    fullMLEresult = MLE_fit(data = data, bounds = bounds, sigma = sigma, Log = Log, deg = deg_choose, abs_tol = abs_tol, location = location)
    
    with open(os.path.join(location,'log_file.txt'),'a') as f:
       f.write('Finished full dataset MLE run at {}\n'.format(datetime.datetime.now()))
    f.close()
    
    weights = fullMLEresult['weights']
    aic = fullMLEresult['aic']
    bic = fullMLEresult['bic'] 
    M_points =  fullMLEresult['M_points'] 
    R_points = fullMLEresult['R_points'] 
    M_cond_R = fullMLEresult['M_cond_R'] 
    M_cond_R_var = fullMLEresult['M_cond_R_var'] 
    M_cond_R_lower = fullMLEresult['M_cond_R_quantile'][:,0] 
    M_cond_R_upper = fullMLEresult['M_cond_R_quantile'][:,1] 
    R_cond_M = fullMLEresult['R_cond_M']      
    R_cond_M_var = fullMLEresult['R_cond_M_var'] 
    R_cond_M_lower = fullMLEresult['R_cond_M_quantile'][:,0]  
    R_cond_M_upper = fullMLEresult['R_cond_M_quantile'][:,1]  
    Radius_marg = fullMLEresult['Radius_marg']  
    Mass_marg = fullMLEresult['Mass_marg']  
    
    np.savetxt(os.path.join(location,'weights.txt'),weights)
    np.savetxt(os.path.join(location,'aic.txt'),[aic])    
    np.savetxt(os.path.join(location,'bic.txt'),[bic]) 
    np.savetxt(os.path.join(location,'M_points.txt'),M_points)
    np.savetxt(os.path.join(location,'R_points.txt'),R_points)    
    np.savetxt(os.path.join(location,'M_cond_R.txt'),M_cond_R)
    np.savetxt(os.path.join(location,'M_cond_R_var.txt'),M_cond_R_var)
    np.savetxt(os.path.join(location,'M_cond_R_lower.txt'),M_cond_R_lower)
    np.savetxt(os.path.join(location,'M_cond_R_upper.txt'),M_cond_R_upper)
    np.savetxt(os.path.join(location,'R_cond_M.txt'),R_cond_M)
    np.savetxt(os.path.join(location,'R_cond_M_var.txt'),R_cond_M_var) 
    np.savetxt(os.path.join(location,'R_cond_M_lower.txt'),R_cond_M_lower)
    np.savetxt(os.path.join(location,'R_cond_M_upper.txt'),R_cond_M_upper)
    np.savetxt(os.path.join(location,'Radius_marg.txt'),Radius_marg)  
    np.savetxt(os.path.join(location,'Mass_marg.txt'),Mass_marg) 
    


    n_boot_iter = (np.random.choice(n, n, replace = True) for i in range(num_boot))
    inputs = ((data[n_boot], sigma[n_boot], bounds, Log, deg_choose, abs_tol, location) for n_boot in n_boot_iter)
    
    print('Running {} bootstraps for the MLE code with degree = {}, using {} threads.'.format(str(num_boot),str(deg_choose),str(cores)))
    pool = Pool(processes = cores)
    results = map(bootsample_mle,inputs)
    
    weights_boot = np.array([x['weights'] for x in results])
    aic_boot = np.array([x['aic'] for x in results])
    bic_boot = np.array([x['bic'] for x in results]) 
    M_points_boot =  np.array([x['M_points'] for x in results]) 
    R_points_boot = np.array([x['R_points'] for x in results]) 
    M_cond_R_boot = np.array([x['M_cond_R'] for x in results]) 
    M_cond_R_var_boot = np.array([x['M_cond_R_var'] for x in results]) 
    M_cond_R_lower_boot = np.array([x['M_cond_R_quantile'][:,0] for x in results]) 
    M_cond_R_upper_boot = np.array([x['M_cond_R_quantile'][:,1] for x in results]) 
    R_cond_M_boot = np.array([x['R_cond_M'] for x in results])      
    R_cond_M_var_boot = np.array([x['R_cond_M_var'] for x in results]) 
    R_cond_M_lower_boot = np.array([x['R_cond_M_quantile'][:,0] for x in results])  
    R_cond_M_upper_boot = np.array([x['R_cond_M_quantile'][:,1] for x in results])  
    Radius_marg_boot = np.array([x['Radius_marg'] for x in results])  
    Mass_marg_boot = np.array([x['Mass_marg'] for x in results])       
    
    np.savetxt(os.path.join(location,'weights_boot.txt'),weights_boot)
    np.savetxt(os.path.join(location,'aic_boot.txt'),aic_boot)    
    np.savetxt(os.path.join(location,'bic_boot.txt'),bic_boot) 
    np.savetxt(os.path.join(location,'M_points_boot.txt'),M_points_boot[0])
    np.savetxt(os.path.join(location,'R_points_boot.txt'),R_points_boot[0])    
    np.savetxt(os.path.join(location,'M_cond_R_boot.txt'),M_cond_R_boot)
    np.savetxt(os.path.join(location,'M_cond_R_var_boot.txt'),M_cond_R_var_boot)
    np.savetxt(os.path.join(location,'M_cond_R_lower_boot.txt'),M_cond_R_lower_boot)
    np.savetxt(os.path.join(location,'M_cond_R_upper_boot.txt'),M_cond_R_upper_boot)
    np.savetxt(os.path.join(location,'R_cond_M_boot.txt'),R_cond_M_boot)
    np.savetxt(os.path.join(location,'R_cond_M_var_boot.txt'),R_cond_M_var_boot) 
    np.savetxt(os.path.join(location,'R_cond_M_lower_boot.txt'),R_cond_M_lower_boot)
    np.savetxt(os.path.join(location,'R_cond_M_upper_boot.txt'),R_cond_M_upper_boot)
    np.savetxt(os.path.join(location,'Radius_marg_boot.txt'),Radius_marg_boot)  
    np.savetxt(os.path.join(location,'Mass_marg_boot.txt'),Mass_marg_boot)
    
    endtime = datetime.datetime.now()
    print(endtime - starttime)
    
    with open(os.path.join(location,'log_file.txt'),'a') as f:
       f.write('Ended run at {}\n'.format(endtime))
    f.close()
                                        
    return results
            
            
if __name__ == '__main__':           
    a = MLE_fit_bootstrap(data = data, sigma = sigma, Mass_max = Mass_max, 
                        Mass_min = Mass_min, Radius_max = Radius_max, Radius_min = Radius_min, select_deg = 5, Log = True, num_boot = 8,
                        location = os.path.join(os.path.dirname(__file__),'Bootstrap_open_serial_short'))

            
            
        
        
        
        
    
    
    