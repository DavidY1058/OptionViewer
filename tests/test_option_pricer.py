from european_option import EuropeanOption

class TestEuropeanOption:
    
    def _isFloatNear(self, x,y,tol=0.0001):
        if abs(x-y) > tol: 
            print(f"x y (x-y): %f %f %f" % (x, y, x-y))
        return abs(x-y)<tol
    
    def _init_option_a(self):
        opt = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt.setLevel(200.0, 0.3, 0.03) #spot, ivol, riskFree
        return opt

    def _init_option_b(self):
        opt = EuropeanOption(True, 98.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt.setLevel(100.0, 0.3, 0.03) #spot, ivol, riskFree
        return opt

    def _init_option_c(self):
        opt = EuropeanOption(False, 102.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt.setLevel(100.0, 0.3, 0.03) #spot, ivol, riskFree
        return opt

    def _init_option_d(self):
        opt = EuropeanOption(False, 49.0, 30.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt.setLevel(50.0, 0.3, 0.03) #spot, ivol, riskFree
        return opt    
    
    def test_expired_call_1(self):
        opt = EuropeanOption(True, 49.0, 0.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt.setLevel(50.0, 0.3, 0.03) #spot, ivol, riskFree
        assert self._isFloatNear(opt.fairValue(), 1.0, 1e-16)
    
    def test_expired_call_2(self):
        opt = EuropeanOption(True, 51.0, 0.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt.setLevel(50.0, 0.3, 0.03) #spot, ivol, riskFree
        assert self._isFloatNear(opt.fairValue(), 0.0, 1e-16)

    def test_expired_put_1(self):
        opt = EuropeanOption(False, 49.0, 0.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt.setLevel(50.0, 0.3, 0.03) #spot, ivol, riskFree
        assert self._isFloatNear(opt.fairValue(), 0.0, 1e-16)

    def test_expired_put_2(self):
        opt = EuropeanOption(False, 51.0, 0.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt.setLevel(50.0, 0.3, 0.03) #spot, ivol, riskFree
        assert self._isFloatNear(opt.fairValue(), 1.0, 1e-16)


    
    def test_a_fairValue(self):
        opt = self._init_option_a()
        assert self._isFloatNear(opt.fairValue(), 10.3188, 0.02)
    
    def test_a_delta(self):
        opt = self._init_option_a()
        assert self._isFloatNear(opt.delta(), 0.4814, 0.001)
                
    def test_a_vega(self):
        opt = self._init_option_a()
        assert self._isFloatNear(opt.vega()/100.0, 0.3961, 0.001)

    def test_a_rho(self):
        opt = self._init_option_a()
        assert self._isFloatNear(opt.rho()/100.0, 0.2142, 0.01)        

    def test_a_theta(self):
        opt = self._init_option_a()
        assert self._isFloatNear(opt.theta()/365.0, -0.0658, 0.002)

    def test_a_gearing(self):
        opt = self._init_option_a()
        assert self._isFloatNear(opt.gearing(), 19.38, 0.02)

    def test_a_gamma(self):
        opt = self._init_option_a()
        assert self._isFloatNear(opt.gamma(), 0.01324)   
        
        
    def test_b_fairValue(self):
        opt = self._init_option_b()
        assert self._isFloatNear(opt.fairValue(), 7.0525, 0.02)
    
    def test_b_delta(self):
        opt = self._init_option_b()
        assert self._isFloatNear(opt.delta(), 0.5864, 0.001)
                
    def test_b_vega(self):
        opt = self._init_option_b()
        assert self._isFloatNear(opt.vega()/100.0, 0.1932, 0.001)

    def test_b_rho(self):
        opt = self._init_option_b()
        assert self._isFloatNear(opt.rho()/100.0, 0.13, 0.01)        

    def test_b_theta(self):
        opt = self._init_option_b()
        assert self._isFloatNear(opt.theta()/365.0, -0.0323, 0.001)

    def test_b_gearing(self):
        opt = self._init_option_b()
        assert self._isFloatNear(opt.gearing(), 14.18, 0.02)

    def test_b_gamma(self):
        opt = self._init_option_b()
        assert self._isFloatNear(opt.gamma(), 0.025836)       
        
        
    def test_c_fairValue(self):
        opt = self._init_option_c()
        assert self._isFloatNear(opt.fairValue(), 6.9081, 0.02)
    
    def test_c_delta(self):
        opt = self._init_option_c()
        assert self._isFloatNear(opt.delta(), -0.514, 0.001)
                
    def test_c_vega(self):
        opt = self._init_option_c()
        assert self._isFloatNear(opt.vega()/100.0, 0.1981, 0.001)

    def test_c_rho(self):
        opt = self._init_option_c()
        assert self._isFloatNear(opt.rho()/100.0, -0.15, 0.01)        

    def test_c_theta(self):
        opt = self._init_option_c()
        assert self._isFloatNear(opt.theta()/365.0, -0.033, 0.003)

    def test_c_gearing(self):
        opt = self._init_option_c()
        assert self._isFloatNear(opt.gearing(), 14.48, 0.02)

    def test_c_gamma(self):
        opt = self._init_option_c()
        assert self._isFloatNear(opt.gamma(), 0.02648)   
        
        
    def test_d_fairValue(self):
        opt = self._init_option_d()
        assert self._isFloatNear(opt.fairValue(), 1.227, 0.02)
    
    def test_d_delta(self):
        opt = self._init_option_d()
        assert self._isFloatNear(opt.delta(), -0.3866, 0.001)
                
    def test_d_vega(self):
        opt = self._init_option_d()
        assert self._isFloatNear(opt.vega()/100.0, 0.0548, 0.001)

    def test_d_rho(self):
        opt = self._init_option_d()
        assert self._isFloatNear(opt.rho()/100.0, -0.0169, 0.0002)        

    def test_d_theta(self):
        opt = self._init_option_d()
        assert self._isFloatNear(opt.theta()/365.0, -0.0277, 0.002)

    def test_d_gearing(self):
        opt = self._init_option_d()
        assert self._isFloatNear(opt.gearing(), 40.75, 0.05)

    def test_d_gamma(self):
        opt = self._init_option_d()
        assert self._isFloatNear(opt.gamma(), 0.08886)  
        
    def test_e_veta(self):
        #veta = d2V/ dt dv = dTheta/dv
        dvol = 0.001
        
        opt1 = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt1.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        
        #note for the option class, theta convention = -dV/dt        
        t1 = -opt1.theta()
        
        opt2 = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt2.setLevel(200.0, 0.300+dvol, 0.03) #spot, ivol, riskFree
        t2 = -opt2.theta()        
        
        approx = (t2-t1)/dvol
        
        optMid = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        optMid.setLevel(200.0, 0.300+dvol*0.5, 0.03) #spot, ivol, riskFree

        assert self._isFloatNear( approx/ optMid.veta(), 1.0, 1e-3)

    def test_e_charm(self):
        #Delta Decay/ Charm: - d2X/dt dS = -dDelta/dt = -dTheta/dS
        dt = 0.1
        
        opt1 = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt1.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        
        #note for the option class, theta convention = -dV/dt        
        d1 = opt1.delta()
        
        opt2 = EuropeanOption(True, 204.0, 91.0+dt, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt2.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        d2 = opt2.delta()        
        
        approx = -(d2-d1)/(dt/365.0)
        
        optMid = EuropeanOption(True, 204.0, 91.0+dt*0.5, 0.02) #isCall, strike, dayToExpiry, dvdYield
        optMid.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree

        assert self._isFloatNear( approx/ optMid.charm(), 1.0, 1e-3)
   
    def test_e_volga(self):
        #Delta Decay/ Charm: - d2X/dt dv = -dDelta/dt = -dTheta/dS
        dvol = 0.001
        
        opt1 = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt1.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        
        #note for the option class, theta convention = -dV/dt        
        v1 = opt1.vega()
        
        opt2 = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt2.setLevel(200.0, 0.300+dvol, 0.03) #spot, ivol, riskFree
        v2 = opt2.vega()        
        
        approx = (v2-v1)/dvol
        
        optMid = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        optMid.setLevel(200.0, 0.300+dvol*0.5, 0.03) #spot, ivol, riskFree

        assert self._isFloatNear( approx/ optMid.volga(), 1.0, 1e-3)          
        
        
    #For test_e, test_f assume X = option price, S=spot, v=implVol
    #test_e and f are for second order greek testing.  with e being the Call, f being the Put
    def test_e_vanna(self):
        #vanna = d2V/ dS dv = dDelta/dv
        dvol = 0.001
        
        opt1 = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt1.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        d1 = opt1.delta()
        
        opt2 = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt2.setLevel(200.0, 0.300+dvol, 0.03) #spot, ivol, riskFree
        d2 = opt2.delta()        
        
        approx = (d2-d1)/dvol
        
        optMid = EuropeanOption(True, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        optMid.setLevel(200.0, 0.300+dvol*0.5, 0.03) #spot, ivol, riskFree
        print(approx)
        print(optMid.vanna())
        assert self._isFloatNear( approx/ optMid.vanna(), 1.0, 1e-3)
   

    def test_f_vanna(self):
        #vanna = d2V/ dS dv = dDelta/dv
        dvol = 0.001
        
        opt1 = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt1.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        d1 = opt1.delta()
        
        opt2 = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt2.setLevel(200.0, 0.300+dvol, 0.03) #spot, ivol, riskFree
        d2 = opt2.delta()        
        
        approx = (d2-d1)/dvol
        
        optMid = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        optMid.setLevel(200.0, 0.300+dvol*0.5, 0.03) #spot, ivol, riskFree
        print(approx)
        print(optMid.vanna())
        assert self._isFloatNear( approx/ optMid.vanna(), 1.0, 1e-3)      
        


   
    def test_f_veta(self):
        #veta = d2V/ dt dv = dTheta/dv
        dvol = 0.001
        
        opt1 = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt1.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        
        #note for the option class, theta convention = -dV/dt
        t1 = -opt1.theta()
        
        opt2 = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt2.setLevel(200.0, 0.300+dvol, 0.03) #spot, ivol, riskFree
        t2 = -opt2.theta()        
        
        approx = (t2-t1)/dvol
        
        optMid = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        optMid.setLevel(200.0, 0.300+dvol*0.5, 0.03) #spot, ivol, riskFree

        assert self._isFloatNear( approx/ optMid.veta(), 1.0, 1e-3)

  
    
    def test_f_charm(self):
        #Delta Decay/ Charm: - d2X/dt dS = -dDelta/dt = -dTheta/dS
        dt = 0.1
        
        opt1 = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt1.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        
        #note for the option class, theta convention = -dV/dt        
        d1 = opt1.delta()
        
        opt2 = EuropeanOption(False, 204.0, 91.0+dt, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt2.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        d2 = opt2.delta()        
        
        approx = -(d2-d1)/(dt/365.0)
        
        optMid = EuropeanOption(False, 204.0, 91.0+dt*0.5, 0.02) #isCall, strike, dayToExpiry, dvdYield
        optMid.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree

        assert self._isFloatNear( approx/ optMid.charm(), 1.0, 1e-3)   



        
    def test_f_volga(self):
        #Delta Decay/ Charm: - d2X/dt dv = -dDelta/dt = -dTheta/dS
        dvol = 0.001
        
        opt1 = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt1.setLevel(200.0, 0.300, 0.03) #spot, ivol, riskFree
        
        #note for the option class, theta convention = -dV/dt        
        v1 = opt1.vega()
        
        opt2 = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        opt2.setLevel(200.0, 0.300+dvol, 0.03) #spot, ivol, riskFree
        v2 = opt2.vega()        
        
        approx = (v2-v1)/dvol
        
        optMid = EuropeanOption(False, 204.0, 91.0, 0.02) #isCall, strike, dayToExpiry, dvdYield
        optMid.setLevel(200.0, 0.300+dvol*0.5, 0.03) #spot, ivol, riskFree

        assert self._isFloatNear( approx/ optMid.volga(), 1.0, 1e-3)        
                