import math
from scipy.stats import norm

class EuropeanOption:
    #https://en.wikipedia.org/wiki/Greeks_(finance)

    def __init__(self, isCall, strike, dayToExpiry, dvdYield, dayInYr=365):
        self.hasLevel = False
        self.isCall = isCall
        self.strike = strike
        self.tToExpiry = dayToExpiry/dayInYr
        self.dvdYield = dvdYield
        self.dayInYr = dayInYr
            
    def _dj(self, j, s, k, v, t, r, q):        
        return (math.log(s/k) + (r - q + ((-1)**(j-1))*0.5*v*v)*t)/(v*(t**0.5))

    def setLevel(self, spot, ivol, riskFreeRate):
        self.hasLevel = True
        self.spot = spot
        self.ivol = ivol
        self.riskFreeRate = riskFreeRate
        if self.tToExpiry > 0.0: 
            self.d1 = self._dj(1, self.spot, self.strike, self.ivol, self.tToExpiry, self.riskFreeRate, self.dvdYield)
            self.d2 = self._dj(2, self.spot, self.strike, self.ivol, self.tToExpiry, self.riskFreeRate, self.dvdYield)
        else:
            self.d1, self.d2 = float('nan'), float('nan')
     
    def fairValue(self):        
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')
        if self.tToExpiry <= 0.0: 
            if self.isCall:
                return max(0.0, self.spot-self.strike)
            else:
                return max(0.0, self.strike-self.spot)
        
        s_exp_minus_qt=self.spot*math.exp(-self.dvdYield*self.tToExpiry)
        k_exp_minus_rt=self.strike*math.exp(-self.riskFreeRate*self.tToExpiry)
        if self.isCall:
            return s_exp_minus_qt*norm.cdf(self.d1)-k_exp_minus_rt*norm.cdf(self.d2)
        else:
            return k_exp_minus_rt*norm.cdf(-self.d2)-s_exp_minus_qt*norm.cdf(-self.d1)
    
    #first order greeks
    def delta(self):
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')    
        if self.tToExpiry <= 0.0: return float('nan')
        exp_minus_qt=math.exp(-self.dvdYield*self.tToExpiry)
        if self.isCall:
            return exp_minus_qt*norm.cdf(self.d1)
        else:
            return -exp_minus_qt*norm.cdf(-self.d1)

    def vega(self):    
        #for 100% increase in implied vol
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')
        if self.tToExpiry <= 0.0: return float('nan')
        s_exp_minus_qt=self.spot*math.exp(-self.dvdYield*self.tToExpiry)        
        return s_exp_minus_qt*norm.pdf(self.d1)*math.sqrt(self.tToExpiry)

    def rho(self):    
        #for 100% increase in risk free rate
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')        
        if self.tToExpiry <= 0.0: return float('nan')
        kt_exp_minus_rt=self.strike*self.tToExpiry*math.exp(-self.riskFreeRate*self.tToExpiry)
        if self.isCall:
            return kt_exp_minus_rt*norm.cdf(self.d2)
        else:
            return -kt_exp_minus_rt*norm.cdf(-self.d2)
                      
    def theta(self):
        #Note the convention here is -dX/dt (ie positive theta for a normal call or put)
        #time decay per annum
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')
        if self.tToExpiry <= 0.0: return float('nan')
        s_exp_minus_qt=self.spot*math.exp(-self.dvdYield*self.tToExpiry)
        rk_exp_minus_rt=self.riskFreeRate*self.strike*math.exp(-self.riskFreeRate*self.tToExpiry)
        half_v_div_sqrt_t = 0.5*self.ivol/math.sqrt(self.tToExpiry)
                
        sign = 1 if self.isCall else -1        
        term1=-s_exp_minus_qt*half_v_div_sqrt_t*norm.pdf(sign*self.d1)
        term2=-sign*rk_exp_minus_rt*norm.cdf(sign*self.d2)
        term3=sign*s_exp_minus_qt*self.dvdYield*norm.cdf(sign*self.d1)
        return term1+term2+term3

    def gearing(self):
        #gearing==delta
        if self.tToExpiry <= 0.0: return float('nan')
        return self.spot/self.fairValue()
    
    #second order greeks    
    
    #d2V/d2S
    def gamma(self):
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')
        if self.tToExpiry <= 0.0: return float('nan')
        s_v_sqrt_t = self.spot*self.ivol*math.sqrt(self.tToExpiry)
        exp_minus_qt=math.exp(-self.dvdYield*self.tToExpiry)    
        return exp_minus_qt/s_v_sqrt_t*norm.pdf(self.d1)

    #d2V/dSdv
    def vanna(self):
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')
        if self.tToExpiry <= 0.0: return float('nan')
        exp_minus_qt=math.exp(-self.dvdYield*self.tToExpiry)    
        return -exp_minus_qt*norm.pdf(self.d1)*self.d2/self.ivol

    #d2V/dv2
    def volga(self):
        #volga == vomma
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')
        if self.tToExpiry <= 0.0: return float('nan')
        return self.vega()*self.d1*self.d2/self.ivol
      
    #d2V/dvdt
    def veta(self):
        #vegaDecay == veta
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')
        if self.tToExpiry <= 0.0: return float('nan')
        s,t,r,q,d1,d2=self.spot, self.tToExpiry, self.riskFreeRate, self.dvdYield, self.d1, self.d2
        term1 = -s*math.exp(-t*q)*norm.pdf(d1)*math.sqrt(t)
        term2 = q + (r-q)*d1/self.ivol/math.sqrt(t)-0.5*(1.0+d1*d2)/t
        return term1*term2
    
    #-d2V/dtdS
    def charm(self):
        #deltaDecay == charm
        if not self.hasLevel: raise RuntimeError('Option current levels has not been set')
        if self.tToExpiry <= 0.0: return float('nan')
        t,r,q,d1,d2=self.tToExpiry, self.riskFreeRate, self.dvdYield, self.d1, self.d2
        v_sqrt_t=self.ivol*math.sqrt(t)        
        term2 = math.exp(-q*t)*norm.pdf(d1)* 0.5*(2.0*(r-q)*t-d2*v_sqrt_t)/v_sqrt_t/t
        if self.isCall:
            return q*math.exp(-q*t)*norm.cdf(d1)-term2
        else:
            return -q*math.exp(-q*t)*norm.cdf(-d1)-term2
            
            
   