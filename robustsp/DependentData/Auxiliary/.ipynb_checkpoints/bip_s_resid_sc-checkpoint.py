import numpy as np
import robustsp as rsp

def bip_s_resid_sc(x, beta_hat, p, q):
    
    phi_hat = np.array(beta_hat[:p]) # [] if p=0, MA case
    
    theta_hat = np.array(beta_hat[p:]) # [] if p=length(beta_hat), AR case
    
    x = np.array(x)
    N = len(x)
    r = max(p,q)
    
    a_bip = np.zeros(N)
    
    x_sc = rsp.m_scale(x)
    
    kap2 = 0.8724286
    
    poles = lambda x: np.sum(np.abs(np.roots(-1*np.array([-1,*x])))>1)
    
    if poles(phi_hat) or poles(theta_hat):
        sigma_hat = x_sc
    
    else:
        lamb = rsp.ma_infinity(phi_hat, -1*theta_hat, 100) # MA infinity approximation to compute scale used in eta function
        sigma_hat = np.sqrt(x_sc**2/(1+kap2*np.sum(lamb**2))) # scale used in eta
        
    if r == 0:
        a_sc_bip = x_sc
        a_bip = np.array(x)
    else:
        if poles(phi_hat) or poles(theta_hat):
            a_bip_sc = 10**10
        elif p>=1 and q>=1:
            # ARMA model
            for ii in range(r,N):
                # BIP-ARMA residuals
                xArr = x[ii-1::-1] if ii-p-1 < 0 else x[ii-1:ii-p-1:-1]
                aArr = a_bip[ii-1::-1] if ii-q-1 < 0 else a_bip[ii-1:ii-q-1:-1]
                apArr = a_bip[ii-1::-1] if ii-p-1 < 0 else a_bip[ii-1:ii-p-1:-1]

                a_bip[ii] = x[ii]\
                -phi_hat@(xArr-apArr+sigma_hat*rsp.eta(apArr/sigma_hat))+sigma_hat*(theta_hat[None,:])@(rsp.eta(aArr/sigma_hat)[:,None])
                
        elif p==0 and q>=1:
            # MA residuals
            for ii in range(r,N):
                # BIP-MA residuals
                aArr = a_bip[ii-1::-1] if ii-q-1 < 0 else a_bip[ii-1:ii-q-1:-1]
                
                a_bip[ii] = x[ii]+theta_hat[None,:]@(sigma_hat*rsp.eta(aArr/sigma_hat)[:,None])

        elif p>=1 and q==0:
            # AR Model
            for ii in range(r,N):
                xArr = x[ii-1::-1] if ii-p-1 < 0 else x[ii-1:ii-p-1:-1]
                apArr = a_bip[ii-1::-1] if ii-p-1 < 0 else a_bip[ii-1:ii-p-1:-1]

                a_bip[ii] = x[ii]-phi_hat@(xArr-apArr\
                +sigma_hat*rsp.eta(apArr/sigma_hat))
                

        a_bip_sc = rsp.m_scale(a_bip[p:])
        x_filt = np.array(x)
        
        for ii in range(p,N):
            x_filt[ii] = x[ii] - a_bip[ii] + sigma_hat * rsp.eta(a_bip[ii]/sigma_hat)
    
    return a_bip_sc, x_filt