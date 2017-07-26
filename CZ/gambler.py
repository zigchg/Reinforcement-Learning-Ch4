import numpy as np
import matplotlib.pyplot as plt

# we have an undiscounted task: 
gamma = 1

# the number of states (0 and 100 are terminal states) 
n_non_term_states=99
n_states=n_non_term_states+2

# initialize state value function (including terminal states): 
V = [0 for i in range(0,n_states)]
V[0] = 0.0
V[len(V)-1]=1.0 

# the probability our coin lands heads: 
p_heads = 0.40

thetaThreshold = 1e-8

def gam_rhs_state_bellman(s,a,V,gamma,p_head):
    s_head = s+a # we win an additional amount "a"
    s_tail = s-a # we loose our bet "a"

    v_tmp = p_head*V[s_head] + (1-p_head)*V[s_tail]
    return v_tmp

# plot these iterations: 
plotIters = [ 1, 2, 3, 32 ]

delta = float("inf")
iterCnts = 0

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)

while( delta > thetaThreshold ):
  iterCnts=iterCnts+1
  
  delta = 0; 
  # loop over all NON TERMINAL states: 
  for si in range(1, n_states-1):
    v = V[si]
    s = si  # the state \in [1,\cdots,99]
    # get the possible actions in this state (not lower bound of ONE ... zero seems like a unreasonable action)
    acts = range(1,min(s,(n_states-1)-s)+1)
    Q = [0 for i in range(0,len(acts))]
    
    for ai in range(0,len(acts)):
      Q[ai] = gam_rhs_state_bellman(s,acts[ai],V,gamma,p_heads); 

    V[si] = max(Q);
    delta = max(delta,abs(v-V[si]));
  
  if( iterCnts in plotIters ):
    ax1.plot( range(0,n_states), V, label='sweep'+str(iterCnts))

ax1.plot( range(0,n_states), V, label='final' )

fig1.show()

# compute the greedy policy at each timestep: 
# 
eps_pol = 1e-8
pol_pi  = [0 for i in range(0,n_states)]
# loop over all non-terminal states: 
for si in range(1,n_states-1):   
  s = si  # the state \in [1,\cdots,99]
  # get the possible actions in this state (no zero action)
  acts = range(1,min(s,(n_states-1)-s)+1)
  
  Q = [0 for i in range(0,len(acts))]
  bestVal = -float("inf")
  bestAct = 0
  for ai in range(0,len(acts)):
    Q[ai] = gam_rhs_state_bellman(s,acts[ai],V,gamma,p_heads)
    # assume that we have to beat an earlier policy by at least eps_pol 
    # this seems to encourage plays with the smallest bets
    if( bestVal<(Q[ai]-eps_pol) ):  
      bestVal=Q[ai]
      bestAct=ai
  
  pol_pi[si] = bestAct

fig2 = plt.figure()
ax2 = fig2.add_subplot(222)
ax2.plot(range(0,n_states), pol_pi)

fig2.show()
#if( 1 ) %i( [iterCnts] is plotIters ):
#  figure(fhs)
#  stairs( 1:(n_states-2), pol_pi )
#  plt. xlabel('capital')
#  plt.ylabel('last policy')#; axis tight; drawnow; 
  #fn='gam_final_policy.eps'; saveas( gcf, fn, 'epsc' ); 
