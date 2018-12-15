import matplotlib.pyplot as plt
import os
from astropy.table import Table
import numpy as np

from mrexo import predict_m_given_r, predict_r_given_m


try :
    pwd = os.path.dirname(__file__)
except NameError:
    pwd = ''



result_dir = "C:/Users/shbhu/Documents/Git/mrexo/sample_kepler2/Kepler_55_open_corrected"

i = 4

#result_dir = "C:/Users/shbhu/Documents/Git/mrexo/sample_scripts/M_dwarfs_deg_reduced_tol{}".format(17)
#result_dir =  "C:/Users/shbhu/Documents/Git/mrexo/sample_scripts/Smaller_boundaries/M_dwarfs_deg{}".format(i)

#result_dir = os.path.join(pwd,'Results_deg_11')
#result_dir = "C:/Users/shbhu/Documents/GitHub/mrexo/sample_kepler2/Kepler_55_cluster"

#weights_mle = np.loadtxt(os.path.join(result_dir,'output','weights.txt'))
#print(predict_m_given_r(Radius=np.log10(5), Radius_sigma=None, posterior_sample=False, islog=True, dataset='kepler', showplot=False))

for i in range(17,18):

    result_dir =  "C:/Users/shbhu/Documents/Git/mrexo/sample_scripts/M_dwarfs_deg_cancel_boundary_poly17"
    result_dir = "C:/Users/shbhu/Documents/Git/mrexo/sample_scripts/M_dwarfs_deg17_trimmed"
    a = predict_m_given_r(Radius=1.64, Radius_sigma=None, posterior_sample=False, islog=False, result_dir=result_dir, showplot=True)
    print(a)
    break
#c = predict_r_given_m(Mass=np.log10(1), Mass_sigma=None, posterior_sample=False, islog=False, result_dir=result_dir, showplot=True)

#b = predict_m_given_r(Radius=1, Radius_sigma=0.1, posterior_sample=False, islog=True, dataset='mdwarf', showplot=True)

'''
C:/Users/shbhu/Documents/Git/mrexo/sample_scripts/M_dwarfs_deg17
17
[1.9423930353731744, 0.4405540095682138, 8.992463492366237]

'''

#print(predict_r_given_m(Mass=np.linspace(1.,1.2,3), Mass_sigma=np.repeat(0.1,3), posterior_sample=True, islog=True, dataset='kepler', showplot=False))
#b = predict_m_given_r(Radius=np.linspace(1.,1.2,10), Radius_sigma=np.repeat(None,10), posterior_sample=True, islog=False, dataset='mdwarf', showplot=True)
