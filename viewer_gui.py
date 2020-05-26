from european_option import EuropeanOption
from tkinter import Tk, Label, Button, Entry, W, E, Frame, RIGHT, LEFT, Toplevel

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class OptionViewerGUI:  
    
    TradeInputField = [ 
            ("Notional",   "Notl       ", "f"), 
            ("CallOrPut",  "C/P        ", "putCall"),
            ("Strike",     "Strike     ", "f"), 
            ("DayToExpiry","DayToExpiry", "f"),             
            ("ImplVol",    "iVol(%)    ", "f"), 
            ("RiskFree",   "RiskFree(%)", "f"), 
            ("DvdYield",   "DvdYield(%)", "f"), 
            ]
    
    ScenInputField = ["Spot", "DayToExpiry", "RiskFree"] 
    #Need to enter ivol for each strike as well but will dynamically generate
    
    NTradeInput = 6
    NScenario = 5
    
    
    #GUI design:  
    #===========
    #Main Page: enter the trade detail a max of NTradeInput trades, 
    #then return a list of dict (tradeRecord) with len(tradeRecord)=NTradeInput
    #From this calculate per trade analytics, analytics as a portfolio 
    #and payoff profile chart
    #Scenario Page: after entered the trade details in Main Page, 
    #this page allows entering the inputs of up to NScenario of scenarios
    #After then, generate the portfolio statistics for each scenario.
    
    
    
    def __init__(self, master):
        self.tradeRecord = []
                
        self.master = master
        master.title("Option Viewer")
   
        #Set the framework for the components 
        #====================================
        topFrame = Frame(master)
        topFrame.pack()
        
        botFrame = Frame(master)
        botFrame.pack()
                
        swFrame = Frame(botFrame)
        swFrame.pack(side=LEFT)
        seFrame = Frame(botFrame)
        seFrame.pack(side=RIGHT)

        self.topFrame=topFrame
        self.swFrame=swFrame
        self.seFrame=seFrame
     
        #Input for individual trades (Top Frame)        
        #=====================================
        #Wrap the data validator
        vcmdFloat = topFrame.register(self.validateFloat) 
        vcmdPutCall = topFrame.register(self.validatePutCall) 

        #Title and spot price entry
        topFrameTitleLabel=Label(topFrame, text="Option Trades")
        topFrameTitleLabel.grid(row=0, column=0, columnspan=2, sticky=W)

        spotLabel=Label(topFrame, text="Spot")
        spotLabel.grid(row=0, column=len(self.TradeInputField)-1, sticky=E)
        self.spotEntry = Entry(topFrame, validate="key", validatecommand=(vcmdFloat, '%P'))
        self.spotEntry.grid(row=0, column=len(self.TradeInputField), sticky=E)

        #Input area for individual trades        
        
        #Labels for field names and row number
        tradeInputLabel=[]
        for _, dispName, _ in self.TradeInputField:
            tradeInputLabel.append(Label(topFrame, text=dispName))
        for i in range(len(self.TradeInputField)):            
            tradeInputLabel[i].grid(row=1, column=i+1, sticky=W)
            
        for j in range(self.NTradeInput):
            rowNumLabel = Label(topFrame, text=str(j+1))
            rowNumLabel.grid(row=j+2, column=0, sticky=W)           

        
        #Individual entry box        
        self.tradeEntry = [ [] for i in range(self.NTradeInput) ]        
        for j in range(self.NTradeInput):
            for _, _, ftype  in self.TradeInputField:
                if ftype == "f":
                    self.tradeEntry[j].append(Entry(topFrame, validate="key", validatecommand=(vcmdFloat, '%P')))
                elif ftype == "putCall":
                    self.tradeEntry[j].append(Entry(topFrame, validate="key", validatecommand=(vcmdPutCall, '%P')))

        for i in range(len(self.TradeInputField)):            
            for j in range(self.NTradeInput):
                self.tradeEntry[j][i].grid(row=j+2, column=i+1, sticky=W+E)


        #Control buttons
        nTradeInputField = len(self.TradeInputField)                
        self.calcButton = Button(topFrame, text="Calculate", command=self.mainCalculation)
        self.calcButton.grid(row=self.NTradeInput+2, column=nTradeInputField-1, sticky=W+E)
                
        self.scenButton = Button(topFrame, text="Scenario", command=self.scenarioWin)
        self.scenButton.grid(row=self.NTradeInput+2, column=nTradeInputField, sticky=W+E)
        

        #Setup payoff chart area (SW Frame)        
        #=====================================        
        fig = Figure(figsize=(14,5))
        fig.add_subplot(121)        
        fig.add_subplot(122)        
        
        self.canvas = FigureCanvasTkAgg(fig, master=swFrame)
        self.canvas.get_tk_widget().pack()
        

    
    
    
    def scenarioWin(self):        
        newWindow = Toplevel(self.master)
        newWinOffset=f"+{self.master.winfo_rootx()}+{self.master.winfo_rooty()+self.master.winfo_height()}"
        newWindow.geometry(newWinOffset)                    
        newWindow.title("Scenario")
   
        #Set the framework for the components     
        scenFrame = Frame(newWindow)
        scenFrame.pack()
        self.scenFrame =scenFrame
        
        uniqStrike = list({tr["Strike"] for tr in self.tradeRecord if tr})
        self.uniqStrike = uniqStrike
        
        titleLabel = Label(scenFrame, text = "Changes in")
        titleLabel.grid(row=0, column=1, columnspan=3)
        
        calcButton = Button(scenFrame, text = "Calculate", command=self.scenarioCalculation)
        calcButton.grid(row=self.NScenario+3, column=len(uniqStrike)+3)
        
        
        ########################################
        ##!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
        #Bug: A fixed DayToExpiry makes no sense (e.g. calendar spread)#
        self.scenInputHeading = self.ScenInputField.copy()
        for i in range(len(uniqStrike)):
            self.scenInputHeading.append(f"k={uniqStrike[i]:.2f}")


        ivLable = Label(scenFrame, text = "ImplVol For strike=")
        ivLable.grid(row=0, column=4, columnspan=len(uniqStrike))

        for i,s in enumerate(self.scenInputHeading):
            l = Label(scenFrame, text = s)
            l.grid(row=1, column=i+1)
            
        for i in range(self.NScenario):
            l = Label(scenFrame, text = str(i+1))
            l.grid(row=i+2, column=0)
    
        self.scenarioEntry = [ [] for i in range(self.NScenario) ]                
        vcmdFloat = scenFrame.register(self.validateFloat) 
                
            
        for j in range(self.NScenario):            
            for i in range(3+len(uniqStrike)):
                self.scenarioEntry[j].append(Entry(scenFrame, validate="key", validatecommand=(vcmdFloat, '%P')))
                self.scenarioEntry[j][i].grid(row=j+2, column=i+1, sticky=W+E)
     

        

        
    def perScenCalc(self, scen):
        calc = {}
        calc["FairValue"], calc["Delta"], calc["Gamma"], calc["Vega"], calc["Rho"] = 0.0, 0.0, 0.0, 0.0, 0.0
        for tr in self.tradeRecord:
            if tr:
                vol = scen[f"k={tr['Strike']:.2f}"]/100.0
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"]-abs(scen["DayToExpiry"]), tr["DvdYield"]/100.0)
                opt.setLevel(self.spot+scen["Spot"], vol, (tr["RiskFree"]+scen["RiskFree"])/100.0)
                calc["FairValue"] +=  opt.fairValue()* tr["Notional"]
                calc["Delta"] +=  opt.delta()* tr["Notional"]
                calc["Gamma"] +=  opt.gamma()* tr["Notional"]
                calc["Vega"] +=  opt.vega()* tr["Notional"]
                calc["Rho"] +=  opt.rho()* tr["Notional"]
        return calc

    def parseScenario(self, scenarioEntry, scenarioField):
        nScen = len(scenarioEntry)
        scenRecord = [ {} for i in range(nScen) ]        
        hasAllInput = [None] * nScen
        
        for i,r in enumerate(scenarioEntry):            
            nValidField = 0
            for elem in r:
                val = elem.get()
                if val: nValidField+=1                
            if nValidField == len(scenarioField):
                hasAllInput[i] = True
                for j, fld in enumerate(scenarioField):
                    val = r[j].get().strip()
                    scenRecord[i][fld]=float(val)                    
            elif nValidField >0:
                hasAllInput[i] = False
        return (scenRecord, hasAllInput)


    def scenarioCalculation(self):
                
        self.scenRecord, hasAllInput = self.parseScenario(self.scenarioEntry, self.scenInputHeading)
        for i, status in enumerate(hasAllInput):
            if status:
                statusStr = "ok" if status == True else "Input Error"
                rowNumLabel = Label(self.scenFrame, text=statusStr )
                rowNumLabel.grid(row=i+2, column=len(self.scenInputHeading)+1, padx=10, sticky=W)  

        fieldName = ['FairValue', 'Delta', 'Gamma', 'Vega', 'Rho']
        for i, f in enumerate(fieldName):
            fieldLabel = Label(self.scenFrame, text=f)
            fieldLabel.grid(row=1, column=len(self.scenInputHeading)+2+i, sticky=W)
        
        for i, sc in enumerate(self.scenRecord):
            if sc:
                calc = self.perScenCalc(sc)
                for j, f in enumerate(fieldName):
                    calcLabel = Label(self.scenFrame, text = f"{calc[f]:2.3f}")
                    calcLabel.grid(row=i+2, column=len(self.scenInputHeading)+2+j, sticky=W)                    

     
    def mainCalculation(self):
        #Get the spot level 
        try:
            self.spot = float(self.spotEntry.get().strip())
        except ValueError:
            popup = Tk()
            popup.geometry("+300+300")
            popup.wm_title("Warning: ")
            label = Label(popup, text="Spot level has not been set")
            label.pack(side="top", fill="x", padx=10, pady=10)
            popupButton = Button(popup, text="Okay", command = popup.destroy)
            popupButton.pack()
            return 
        
        
        #Get the individual trade entries.  Note that some of them can be empty
        self.tradeRecord, hasAllInput=self.parseTradeRecord(self.tradeEntry, self.TradeInputField)
        
        for i, status in enumerate(hasAllInput):
            if status is not None:
                statusStr = "ok" if status == True else "Incomplete input"
                rowNumLabel = Label(self.topFrame, text=statusStr )
                rowNumLabel.grid(row=i+2, column=len(self.TradeInputField)+1, padx=10, sticky=W)  
        

        #Output 1: per trade analytics            
        tradeCalc=self.perTradeCalc()
        fieldName = ['FairValue', 'Delta', 'Gamma', 'Vega', 'Rho']
        for i,f in enumerate(fieldName):
            fieldLabel = Label(self.topFrame, text=f)
            fieldLabel.grid(row=1, column=len(self.TradeInputField)+2+i, sticky=W)  
        
        #To-do: add a choice for dollar value vs raw
        for i, calc in enumerate(tradeCalc):
            if calc:
                for j, f in enumerate(fieldName):
                    #s = "%2.3f" % (calc[f]*self.tradeRecord[i]["Notional"]) #dollar value
                    s = "%2.3f" % calc[f] #raw
                    calcLabel = Label(self.topFrame, text=s)
                    calcLabel.grid(row=i+2, column=len(self.TradeInputField)+2+j, sticky=W)  

        
        
        #Output 2: portfolioi wide analytics
        #=====================================                
        resTitleLabel = Label(self.seFrame, text = "Portfolio Calc")
        resTitleLabel.grid(row=0, column=0, sticky=W)
        
        #Showing dollar values for the greeks and fair value
        prtfRes = self.prtfCalc()
        for j, f in enumerate(fieldName):
            resFieldLabel = Label(self.seFrame, text = f)
            resValueLabel = Label(self.seFrame, text = f"{prtfRes[f]:2.3f}")
            resFieldLabel.grid(row=j+1, column=0, sticky=W)
            resValueLabel.grid(row=j+1, column=1, sticky=W)
            
            
        
        #Output 3: payoff and sensitivity charts
        # generate likely to be most interesting range [s +/- 3*vol*sqrt(t)]
        # To-do: add a scroll bar to control the range        
        nXForPlot, ylimAdj = 21, 1.01
        stkUsed = {tr["Strike"] for tr in self.tradeRecord if tr}
        volUsed = {tr["ImplVol"] for tr in self.tradeRecord if tr}
        ttmUsed = {tr["DayToExpiry"] for tr in self.tradeRecord if tr}
        volSqT = max(volUsed)*(max(ttmUsed)/365.0)**0.5
        xMin, xMax = max(0.0,self.spot-3.0*volSqT), self.spot+3.0*volSqT
        #if vol specified is small, the profile calc should at least show behaviour around all strikes
        xMin, xMax = min(xMin, min(stkUsed)/1.01), max(xMax,max(stkUsed)*1.01)
        sArr = set(np.linspace(xMin, xMax, nXForPlot))
        sArr.update(stkUsed)
        sArr = list(sArr)
        sArr.sort()
        
        setSpotMVAsZero=True        
        ax = self.canvas.figure.axes[0]        
        ax.cla()
        payoffNow = self.payoffProfile(sArr, setSpotMVAsZero)
        ax.plot(sArr,payoffNow,color='blue', label='ValDt')   
        minY, maxY = min(payoffNow), max(payoffNow)
        if max(ttmUsed)==min(ttmUsed):
            payoffExpiry = self.payoffProfile(sArr, setSpotMVAsZero, max(ttmUsed))                
            ax.plot(sArr,payoffExpiry,color='red', label='Expiry')   
            minY, maxY = min(minY, min(payoffExpiry)), max(maxY, max(payoffExpiry))            
        else:
            payoffNext = self.payoffProfile(sArr, setSpotMVAsZero, min(ttmUsed))                
            ax.plot(sArr,payoffNext,color='red', label='NxtExpiry')   
            minY, maxY = min(minY, min(payoffNext)), max(maxY, max(payoffNext))            
            
            
        ax.set_xlim(min(sArr), max(sArr))
        ax.set_ylim(minY*ylimAdj, maxY*ylimAdj)
        
        
        ax.set_title('Payoff Profile')
        ax.legend()   


        
        deltaProfile = self.greekProfile(sArr, 'delta')
        vegaProfile = self.greekProfile(sArr, 'vega')
        ax = self.canvas.figure.axes[1]        
        ax.cla()        
        ax.set_xlim(min(sArr), max(sArr))
        ax.set_ylim(min(deltaProfile)*ylimAdj, max(deltaProfile)*ylimAdj)
        ax.plot(sArr,deltaProfile,color='green', label='Delta')                   
        ax.set_ylabel('Delta')        
        ax.set_title('Greek Profile')
        

        if len(self.canvas.figure.axes) == 2: 
            ax2=ax.twinx()
        else:
            ax2 = self.canvas.figure.axes[2]        
        ax2.cla()
        ax2.plot(sArr,vegaProfile,color='goldenrod', label='Vega')   
        ax2.set_ylabel('Vega')
        
 
        #Combine the legend of dual y-axes to the same box 
        line1, label1 = ax.get_legend_handles_labels()
        line2, label2 = ax2.get_legend_handles_labels()
        ax.legend(line1+line2, label1+label2, loc=0)


        self.canvas.draw()


    #Read the trade input data from tradeEntry TK Entry boxes to an array
    def parseTradeRecord(self, tradeEntry, entryFieldName):
        nTradeEntry = len(tradeEntry)
        tradeRecord = [ {} for i in range(nTradeEntry) ]        
        hasAllInput = [None] * nTradeEntry
        
        #tradeEntry is an array of TK Entry
        #row x col = self.NTradeInput x #entryFieldName
        for i,r in enumerate(tradeEntry):
            
            nValidField = 0
            for elem in r:
                val = elem.get()
                if val: nValidField+=1
                
            if nValidField == len(self.TradeInputField):
                hasAllInput[i] = True                      
                for j, field in enumerate(entryFieldName):
                    fld, _, ftype = field
                    val = r[j].get().strip()
                    if ftype == "f":
                        tradeRecord[i][fld]=float(val)
                    elif ftype=="putCall":
                        tradeRecord[i][fld]= "Call" if val.upper() == "C" else "Put"                                                                
            elif nValidField >0:
                hasAllInput[i] = False
            else:
                hasAllInput[i] = None
        
        return (tradeRecord, hasAllInput)
          
    def payoffProfile(self, sArr, spotMVAsZero=True, dayFromNow=0):
        if spotMVAsZero:
            mvNow = 0.0    
            for tr in self.tradeRecord:
                if tr:
                    opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"], tr["DvdYield"]/100.0)                
                    opt.setLevel(self.spot, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                    mvNow += opt.fairValue()*tr["Notional"]                                
        payoff = [0.0] * len(sArr)
        
        for tr in self.tradeRecord:
            if tr:
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], max(0.0, tr["DayToExpiry"]-dayFromNow), tr["DvdYield"]/100.0)                                                
                for i,s in enumerate(sArr):
                    opt.setLevel(s, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                    payoff[i] += opt.fairValue()*tr["Notional"]            
                    
        for i in range(len(sArr)):
            payoff[i] -= mvNow
        return payoff

    def greekProfile(self, sArr, greekName):
        greekArr = [0.0] * len(sArr)
        for tr in self.tradeRecord:
            if tr:
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"], tr["DvdYield"]/100.0)                
                for i,s in enumerate(sArr):
                    opt.setLevel(s, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                    if greekName.lower() == "delta":
                        greekArr[i] += opt.delta()*tr["Notional"]            
                    if greekName.lower() == "gamma":
                        greekArr[i] += opt.gamma()*tr["Notional"]            
                    if greekName.lower() == "vega":
                        greekArr[i] += opt.vega()*tr["Notional"]            
                    if greekName.lower() == "rho":
                        greekArr[i] += opt.rho()*tr["Notional"]            
                    
        return greekArr
   
         
    #Do calculation trade by trade (one set of analytics per trade)
    def perTradeCalc(self):
        tradeCalc = [ {} for i in range(self.NTradeInput) ]
        for i, tr in enumerate(self.tradeRecord):
            if tr:
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"], tr["DvdYield"]/100.0)
                opt.setLevel(self.spot, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                tradeCalc[i]["FairValue"] =  opt.fairValue()
                tradeCalc[i]["Delta"] =  opt.delta()
                tradeCalc[i]["Gamma"] =  opt.gamma()
                tradeCalc[i]["Vega"] =  opt.vega()
                tradeCalc[i]["Rho"] =  opt.rho()
        return tradeCalc
   
    #Do calculation at portfolio wide level
    def prtfCalc(self):
        calc = {}
        calc["FairValue"], calc["Delta"], calc["Gamma"], calc["Vega"], calc["Rho"] = 0.0, 0.0, 0.0, 0.0, 0.0
        
        for i, tr in enumerate(self.tradeRecord):
            if tr:
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"], tr["DvdYield"]/100.0)
                opt.setLevel(self.spot, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                calc["FairValue"] +=  opt.fairValue() * tr["Notional"]
                calc["Delta"] +=  opt.delta() * tr["Notional"]
                calc["Gamma"] +=  opt.gamma() * tr["Notional"]
                calc["Vega"] +=  opt.vega() * tr["Notional"]
                calc["Rho"] +=  opt.rho() * tr["Notional"]
                
        return calc   
          
      
    #Validate input float number (allow -.[0-9])
    def validateFloat(self, new_text):
        if not new_text: # the field is being cleared
            return True        
        try:
            if new_text == "-": 
                return True
            else:
                float(new_text)
            return True
        except ValueError:
            return False   

    #Validate input that sets put or call (p,P for Put; c,C for Call)
    def validatePutCall(self, new_text):
        if not new_text: # the field is being cleared
            return True
        if len(new_text) != 1:
            return False
        if new_text == "p" or new_text == "P":
            return True
        elif new_text == "c" or new_text == "C":
            return True
        else:
            return False


root = Tk()
my_gui = OptionViewerGUI(root)
root.mainloop()