from european_option import EuropeanOption
from tkinter import Tk, Label, Button, Entry, W, E, Frame, RIGHT, LEFT, Toplevel, Checkbutton, IntVar, TOP

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
    GreekTSField = ["Delta", "Gamma", "Vega", "Theta"]
    
    
    NTradeInput = 6
    NScenario = 10
    DaysPerYear = 365
    
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
        
        self.scenWin = None
     
        self.tsPlotSeries1="Delta"
        self.tsPlotSeries2="Gamma"
        

        
        
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
        fig = Figure(figsize=(18,5))
        fig.add_subplot(141)        
        ax2=fig.add_subplot(142)        
        ax2.twinx()
        ax3=fig.add_subplot(143)                
        ax3.twinx()
        ax4=fig.add_subplot(144)                
        ax4.twinx()        
        self.canvas = FigureCanvasTkAgg(fig, master=swFrame)
        self.canvas.get_tk_widget().pack(side=LEFT)
        

        #Choose the greeks to be displayed in timeseries plot

        cbFrame = Frame(swFrame)
        cbFrame.pack(side=RIGHT)
                        
        self.greekChoice=[IntVar() for i in range(len(self.GreekTSField))]
        
        Label(cbFrame, text="Select up to 2 greeks     ").pack()
        Label(cbFrame, text="for timeseries chart      ").pack()
        
        for i, f in enumerate(self.GreekTSField):
            Checkbutton(cbFrame, text=f, variable=self.greekChoice[i], command=self.cbCtrl).pack(side=TOP, anchor=W)
   


    
    def cbCtrl(self):
        nPick = 0
        for i,c in enumerate(self.greekChoice):
            if nPick==0 and c.get()==1: 
                self.tsPlotSeries1=self.GreekTSField[i]
                nPick+=1
            elif nPick==1 and c.get()==1: 
                self.tsPlotSeries2=self.GreekTSField[i]
                nPick+=1
        
    
    def scenarioWin(self):        
        self.scenButton['state']='disabled'
        
        
        newWindow = Toplevel(self.master)        
        newWinOffset=f"+{self.master.winfo_rootx()}+{self.master.winfo_rooty()+self.master.winfo_height()}"
        newWindow.geometry(newWinOffset)                    
        newWindow.title("Scenario")
   
        self.scenWin = newWindow 
    
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
        calc["FairValue"], calc["Delta"], calc["Gamma"], calc["Vega"], calc["Rho"], calc["Theta"] = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
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
                calc["Theta"] +=  opt.theta()* tr["Notional"]/ self.DaysPerYear 
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

        fieldName = ['FairValue', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho']
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
        self.scenButton['state']='normal'
        if self.scenWin is not None:
           self.scenWin.destroy() 
        
        
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
        fieldName = ['FairValue', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho']
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

        
        #Output 2: payoff and sensitivity charts
        # generate likely to be most interesting range [s +/- 3*vol*sqrt(t)]
        # To-do: add a scroll bar to control the range        
        nXForPlot, xlimAdj, ylimAdj = 21, 1.01, 1.01
        stkUsed = {tr["Strike"] for tr in self.tradeRecord if tr}
        volUsed = {tr["ImplVol"] for tr in self.tradeRecord if tr}
        ttmUsed = {tr["DayToExpiry"] for tr in self.tradeRecord if tr}
        volSqT = (self.spot*max(volUsed)/100.0)*(max(ttmUsed)/365.0)**0.5
        
        xMin, xMax = max(0.0,self.spot-3.0*volSqT), self.spot+3.0*volSqT
        #if vol specified is small, the profile calc should at least show behaviour around all strikes
        xMin, xMax = min(xMin, min(stkUsed)/xlimAdj), max(xMax,max(stkUsed)*xlimAdj)
        sArr = set(np.linspace(xMin, xMax, nXForPlot))
        sArr.update(stkUsed)
        sArr = list(sArr)
        sArr.sort()
        
        #First chart: payoff profile
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
            payoffExpiry = self.payoffProfile(sArr, setSpotMVAsZero, min(ttmUsed))                
            ax.plot(sArr,payoffExpiry,color='red', label='NxtExpiry')   
            minY, maxY = min(minY, min(payoffExpiry)), max(maxY, max(payoffExpiry))            
        
        ax.set_xlim(min(sArr), max(sArr))
        ax.set_ylim(minY*ylimAdj, maxY*ylimAdj)
        ax.plot([self.spot, self.spot],[min(min(payoffNow), min(payoffExpiry)), max(max(payoffNow), max(payoffExpiry))], color='darkgray', linestyle='dashed')
        ax.plot([min(sArr),max(sArr)],[0.0,0.0], color='darkgray', linestyle='dashed')
        
        
        ax.set_title('Payoff Profile')
        ax.legend()   
        ax.grid()

        #Second chart: delta and gamma profile        
        deltaProfile = self.greekProfile(sArr, 'delta')
        gammaProfile = self.greekProfile(sArr, 'gamma')
        ax2a = self.canvas.figure.axes[1]        
        ax2a.cla()        
        ax2a.set_xlim(min(sArr), max(sArr))
        ax2a.set_ylim(min(deltaProfile)*ylimAdj, max(deltaProfile)*ylimAdj)
        ax2a.plot(sArr,deltaProfile,color='green', label='Delta')                   
        ax2a.plot([self.spot, self.spot],[min(deltaProfile), max(deltaProfile)], color='lightgray', linestyle='dashed')
        ax2a.set_ylabel('Delta', labelpad=3)        
        ax2a.set_title('Greek Profile-1')
        
        ax2b = self.canvas.figure.axes[2]        
        ax2b.cla()
        ax2b.plot(sArr,gammaProfile,color='olive', label='Gamma')   
        ax2b.set_ylabel('Gamma', labelpad=3)
         
        #Combine the legend of dual y-axes to the same box 
        line1, label1 = ax2a.get_legend_handles_labels()
        line2, label2 = ax2b.get_legend_handles_labels()
        ax2a.legend(line1+line2, label1+label2, loc=0)
        ax2a.grid()

        #Third chart: theta and vega profile
        vegaProfile = self.greekProfile(sArr, 'vega')
        thetaProfile = self.greekProfile(sArr, 'theta')
        ax3a = self.canvas.figure.axes[3]        
        ax3a.cla()        
        ax3a.set_xlim(min(sArr), max(sArr))
        ax3a.set_ylim(min(vegaProfile)*ylimAdj, max(vegaProfile)*ylimAdj)
        ax3a.plot(sArr,vegaProfile,color='maroon', label='Vega')                   
        ax3a.plot([self.spot, self.spot],[min(vegaProfile), max(vegaProfile)], color='lightgray', linestyle='dashed')
        ax3a.set_ylabel('Vega', labelpad=1)        
        ax3a.set_title('Greek Profile-2')
        
        ax3b = self.canvas.figure.axes[4]        
        ax3b.cla()
        ax3b.plot(sArr,thetaProfile,color='goldenrod', label='Theta')   
        ax3b.set_ylabel('Theta', labelpad=1)
         
        #Combine the legend of dual y-axes to the same box 
        line1, label1 = ax3a.get_legend_handles_labels()
        line2, label2 = ax3b.get_legend_handles_labels()
        ax3a.set_xlabel('s')
        ax3a.legend(line1+line2, label1+label2, loc=0)
        ax3a.grid()


        
        #Fourth chart: Greek time series
        tArr = list(np.linspace(1, min(ttmUsed), max(3, int(min(ttmUsed)), nXForPlot)))
        s1, s2 = self.tsPlotSeries1.strip(), self.tsPlotSeries2.strip()
        
        ts1 = self.greekTimeSeries(tArr, s1.lower())
        ts2 = self.greekTimeSeries(tArr, s2.lower())
        
        ax4a = self.canvas.figure.axes[5]        
        ax4a.cla()        
        ax4a.set_xlim(min(tArr), max(tArr))
        ax4a.set_ylim(min(ts1)*ylimAdj, max(ts1)*ylimAdj)
        ax4a.plot(tArr,ts1,color='midnightblue', label=s1)                           
        ax4a.set_ylabel(s1, labelpad=1)        
        ax4a.set_title('Greek Timeseries')
        
        ax4b = self.canvas.figure.axes[6]        
        ax4b.cla()
        ax4b.plot(tArr,ts2,color='teal', label=s2)   
        ax4b.set_ylabel(s2, labelpad=1)
         
        #Combine the legend of dual y-axes to the same box 
        line1, label1 = ax4a.get_legend_handles_labels()
        line2, label2 = ax4b.get_legend_handles_labels()
        ax4a.set_xlabel('Days to Expiry')
        ax4a.legend(line1+line2, label1+label2, loc=0)
        ax4a.grid()
        
        self.canvas.figure.tight_layout()
        self.canvas.draw()

        #Output 3: portfolioi wide analytics
        #=====================================                
        for widget in self.seFrame.winfo_children():
            widget.destroy()
        
        resTitleLabel = Label(self.seFrame, text = "Portfolio Calc")
        resTitleLabel.grid(row=0, column=0, sticky=W)
        
        #Showing dollar values for the greeks and fair value
        prtffieldName = ['FairValue', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho', 'Vanna','Volga','Veta','DeltaDecay']
        prtfRes = self.prtfCalc()                
        for j, f in enumerate(prtffieldName ):
            resFieldLabel = Label(self.seFrame, text = f)
            resValueLabel = Label(self.seFrame, text = f"{prtfRes[f]:2.3f}")
            resFieldLabel.grid(row=j+1, column=0, sticky=W)
            resValueLabel.grid(row=j+1, column=1, sticky=W)


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
                    elif greekName.lower() == "gamma":
                        greekArr[i] += opt.gamma()*tr["Notional"]            
                    elif greekName.lower() == "vega":
                        greekArr[i] += opt.vega()*tr["Notional"]            
                    elif greekName.lower() == "rho":
                        greekArr[i] += opt.rho()*tr["Notional"]            
                    elif greekName.lower() == "theta":
                        greekArr[i] += opt.theta()*tr["Notional"]/self.DaysPerYear             

                    
        return greekArr
   
    def greekTimeSeries(self, tArr, greekName):
        greekArr = [0.0] * len(tArr)
        for tr in self.tradeRecord:
            if tr:                
                for i,t in enumerate(tArr):
                    opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], t, tr["DvdYield"]/100.0)                
                    opt.setLevel(self.spot, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                    if greekName.lower() == "delta":
                        greekArr[i] += opt.delta()*tr["Notional"]            
                    elif greekName.lower() == "gamma":
                        greekArr[i] += opt.gamma()*tr["Notional"]            
                    elif greekName.lower() == "vega":
                        greekArr[i] += opt.vega()*tr["Notional"]            
                    elif greekName.lower() == "rho":
                        greekArr[i] += opt.rho()*tr["Notional"]            
                    elif greekName.lower() == "theta":
                        greekArr[i] += opt.theta()*tr["Notional"]/self.DaysPerYear             

                    
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
                tradeCalc[i]["Theta"] =  opt.theta()/self.DaysPerYear 
        return tradeCalc
   
    #Do calculation at portfolio wide level
    def prtfCalc(self):
        calc={}
        calc["FairValue"], calc["Delta"], calc["Gamma"], calc["Vega"], calc["Rho"], calc["Theta"] = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        calc["Vanna"], calc["Volga"], calc["Veta"], calc["DeltaDecay"]= 0.0, 0.0, 0.0, 0.0
                            
        for i, tr in enumerate(self.tradeRecord):
            if tr:
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"], tr["DvdYield"]/100.0)
                opt.setLevel(self.spot, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                calc["FairValue"] +=  opt.fairValue() * tr["Notional"]
                calc["Delta"] +=  opt.delta() * tr["Notional"]
                calc["Gamma"] +=  opt.gamma() * tr["Notional"]
                calc["Vega"] +=  opt.vega() * tr["Notional"]
                calc["Rho"] +=  opt.rho() * tr["Notional"]
                calc["Theta"] +=  opt.theta() * tr["Notional"]/ self.DaysPerYear 
                calc["Vanna"] +=  opt.vanna() * tr["Notional"]
                calc["Volga"] +=  opt.volga() * tr["Notional"]
                calc["Veta"] +=  opt.veta() * tr["Notional"]
                calc["DeltaDecay"] +=  opt.deltaDecay() * tr["Notional"]
                
                
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
root.geometry("+50+50")
my_gui = OptionViewerGUI(root)
root.mainloop()