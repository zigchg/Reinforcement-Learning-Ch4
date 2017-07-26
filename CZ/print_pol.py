# coding: utf-8
for i in range(0,21):
    for j in range(0,20):
        print('{0:3d}'.format(pol_pi[20-i][j]),end='')
    print('{0:3d}'.format(pol_pi[20-i][20]),end='\n')
    
for i in range(0,21):
    for j in range(0,20):
        print('{0:3d}'.format(emp_pol_pi[20-i][j]),end='')
    print('{0:3d}'.format(emp_pol_pi[20-i][20]),end='\n')
    
