import math

gamma = 0.9

max_n_cars = 20
max_cars_can_store = 10 # $4 addition if exceed
max_num_cars_can_transfer = 5

lambda_A_return = 3
lambda_A_rental = 3
lambda_B_return = 2
lambda_B_rental = 4

def poisspdf(n, lambd):
    p = (lambd**n)*math.exp(-lambd)/math.factorial(n)
    return p

def cmpt_P_and_R(lambda_rental,lambda_return):
    # nCM: n of cars in the morning
    nCM = [i for i in range(0,1+max_n_cars+max_num_cars_can_transfer)]
    
    R = [0 for i in range(0,len(nCM))]
    for n in nCM:
        tmp = float(0)
        for n_rental in range(0,1+10*lambda_rental):
            tmp = tmp + 10*min(n,n_rental)*poisspdf(n_rental, lambda_rental)
#            for n_return in range(0,1+10*lambda_return):
#                tmp = tmp + 10*min(n,n_rental)*poisspdf(n_rental, lambda_rental)*poisspdf(n_return,lambda_return)
        R[n] = tmp
        
    P = [[0 for i in range(0,max_n_cars+1)] for j in range(0,len(nCM))]
    for n_rental in range(0,1+10*lambda_rental):
        rental_P = poisspdf(n_rental, lambda_rental)
        for n_return in range(0,1+10*lambda_return):
            return_P = poisspdf(n_return,lambda_return)
            for n in nCM:
                requests = min(n,n_rental)
                n_prime = max(0, min(max_n_cars,n+n_return-requests))
                P[n][n_prime] = P[n][n_prime] + rental_P*return_P
    
    return R, P

def ind2sub(d,s):
    x = s%(d+1)
    y = (s-x)/(d+1)
    return int(x), int(y)

def rhs_state_value_bellman(na,nb,ntrans,useEmp,V,Ra,Pa,Rb,Pb):
    # restrict this action: 
    ntrans_total = ntrans+useEmp
    ntrans_total = max(-nb,min(ntrans_total,na))
    ntrans_total = max(-max_num_cars_can_transfer,min(+max_num_cars_can_transfer,ntrans_total))
    
    # the number of cars at each site due to transport: 
    na_morn = na-ntrans_total
    nb_morn = nb+ntrans_total
    
    # calculate all costs:
    # --fixed transport cost: 
    v_tmp   = -2*abs(ntrans);
    # --overnight storage cost:
    if( na_morn > max_cars_can_store ):
        v_tmp = v_tmp - 4
    if( nb_morn > max_cars_can_store ):
        v_tmp = v_tmp - 4
    
    for nna in range(0,max_n_cars+1):
        for nnb in range(0,max_n_cars+1):
            pa = Pa[na_morn][nna]
            pb = Pb[nb_morn][nnb]
            try:
                v_tmp = v_tmp + pa*pb*(Ra[na_morn]+Rb[nb_morn]+gamma*V[nna][nnb])
            except:
                print("Ra: " + str(Ra) + "\n")
                print("Rb: " + str(Rb) + "\n")
                print("V: " + str(V) + "\n")
                import sys
                sys.exit()
    return v_tmp

def policy_evaluation(V,pol_pi,emp_pol_pi,Ra,Pa,Rb,Pb):
    n_states = (max_n_cars+1)**2
    MAX_N_ITERS = 100
#    iterCnt = 0
    CONV_TOL = 1e-6
    delta = float('inf')
    
    # MAIN policy evaluation
    while((delta>CONV_TOL)):#and(iterCnt<=MAX_N_ITERS)):
        delta = 0
        for si in range(0,n_states):
            na, nb = ind2sub(max_n_cars,si)
            # zero based
            # get the old action value
            v = V[na][nb]
            # get transfer numbers
            ntrans = pol_pi[na][nb]
            useEmp = emp_pol_pi[na][nb]
            
            V[na][nb] = rhs_state_value_bellman(na,nb,ntrans,useEmp,V,Ra,Pa,Rb,Pb)
            
            delta = max(delta, abs(v-V[na][nb]))
#        iterCnt = iterCnt + 1
    return V

def policy_improvement(pol_pi,emp_pol_pi,V,Ra,Pa,Rb,Pb):
    n_states = (max_n_cars+1)**2
    policyStable = True
    
    for si in range(0,n_states):
        na, nb = ind2sub(max_n_cars,si)
        # zero based
        
        # policy for this state
        b = pol_pi[na][nb]
        b_emp = emp_pol_pi[na][nb]
        
        useEmp = 0
        posA = min(na,max_num_cars_can_transfer)
        posB = min(nb,max_num_cars_can_transfer)
        
        posActionsInState0 = range(-posB,posA+1)
        npa = len(posActionsInState0)
        Q0 = []
        
        for ti in range(0,npa):
            ntrans = posActionsInState0[ti]
            bm = rhs_state_value_bellman(na,nb,ntrans,useEmp,V,Ra,Pa,Rb,Pb)
            Q0.append(bm)
            
        useEmp = 1
        posA = min(max(na-1,0),max_num_cars_can_transfer)
        posB = min(nb,max_num_cars_can_transfer)
        
        posActionsInState1 = range(-posB,posA+1)
        npa = len(posActionsInState1)
        Q1 = []
        
        for ti in range(0,npa):
            ntrans = posActionsInState1[ti]
            bm = rhs_state_value_bellman(na,nb,ntrans,useEmp,V,Ra,Pa,Rb,Pb)
            Q1.append(bm)
            
        max0 = max(Q0)
        imax0 = Q0.index(max0)
        
        max1 = max(Q1)
        imax1 = Q1.index(max1)
        
        dum = max(max0,max1)
        useEmpMax = [max0,max1].index(dum)
        
        if(useEmpMax==0):
            maxPosAct = posActionsInState0[imax0]
        else:
            maxPosAct = posActionsInState1[imax1]
        
        if(maxPosAct!=b or useEmpMax!=b_emp):
            policyStable = False
            pol_pi[na][nb] = maxPosAct
            emp_pol_pi[na][nb] = useEmpMax
    return pol_pi,emp_pol_pi,policyStable
            
            
# Main method
# if __name__=="__main__":
Ra = []
Pa = []
Ra, Pa = cmpt_P_and_R(lambda_A_rental,lambda_A_return)
Rb, Pb = cmpt_P_and_R(lambda_B_rental,lambda_B_return)

V = [[0 for i in range(0,max_n_cars+1)] for j in range(0,max_n_cars+1)]

# initial policy
pol_pi = [[0 for i in range(0,max_n_cars+1)] for j in range(0,max_n_cars+1)]
emp_pol_pi = [[0 for i in range(0,max_n_cars+1)] for j in range(0,max_n_cars+1)]

policyStable = False
# iterNum = 0
while(not policyStable):
    # evaluate the state-value function under this policy:
    V = policy_evaluation(V,pol_pi,emp_pol_pi,Ra,Pa,Rb,Pb)
    # compute an improved policy using the most recent as a base:
    pol_pi, emp_pol_pi, policyStable = policy_improvement(pol_pi,emp_pol_pi,V,Ra,Pa,Rb,Pb)

#    iterNum = iterNum + 1
#    if(iterNum==2):
#        break