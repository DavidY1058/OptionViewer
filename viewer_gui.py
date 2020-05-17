from european_option import EuropeanOption
from tkinter import Tk, Label, Button, Entry, W, E, Frame, RIGHT, LEFT, Toplevel, IntVar, END

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
    NTradeInput = 6
    NScenario = 5
    
    #TradeRecord: dict for the inputs for each option trade
    #Spot: current level of the underlying asset
    
    def __init__(self, master):
        self.tradeRecord = []
                
        self.master = master
        master.title("Option Viewer")
   
        #Set the framework for the components     
        topFrame = Frame(master)
        topFrame.pack()
        
        nwFrame = Frame(topFrame)
        nwFrame.pack(side=LEFT)
        self.neFrame = Frame(topFrame)
        self.neFrame.pack(side=RIGHT)

        botFrame = Frame(master)
        botFrame.pack()
                
        swFrame = Frame(botFrame)
        swFrame.pack(side=LEFT)
        seFrame = Frame(botFrame)
        seFrame.pack(side=RIGHT)

        self.swFrame=swFrame
     
        #Input for individual trades (NW Frame)        
        nwFrameTitleLabel=Label(nwFrame, text="Option Trades")
        nwFrameTitleLabel.grid(row=0, column=0, columnspan=2, sticky=W)

        spotLabel=Label(nwFrame, text="Spot")
        spotLabel.grid(row=0, column=len(self.TradeInputField)-1, sticky=E)

        
        trade_input_label=[]
        self.trade_entry = [ [] for i in range(self.NTradeInput) ]
                
        vcmdFloat = nwFrame.register(self.validateFloat) # we have to wrap the command
        vcmdPutCall = nwFrame.register(self.validatePutCall) # we have to wrap the command
        
        for _, dispName, _ in self.TradeInputField:
            trade_input_label.append(Label(nwFrame, text=dispName))
            
        for j in range(self.NTradeInput):
            for _, _, ftype  in self.TradeInputField:
                if ftype == "f":
                    self.trade_entry[j].append(Entry(nwFrame, validate="key", validatecommand=(vcmdFloat, '%P')))
                elif ftype == "putCall":
                    self.trade_entry[j].append(Entry(nwFrame, validate="key", validatecommand=(vcmdPutCall, '%P')))

        for i, data in enumerate(self.TradeInputField):
            _, dispName, _ = data
            trade_input_label.append(Label(nwFrame, text=dispName))
        
        nTradeInputField = len(self.TradeInputField)
        
        #print trade/row number 
        for j in range(self.NTradeInput):
            rowNumLabel = Label(nwFrame, text=str(j+1))
            rowNumLabel.grid(row=j+2, column=0, sticky=W)           
                
        for i in range(nTradeInputField):            
            trade_input_label[i].grid(row=1, column=i+1, sticky=W)           
            for j in range(self.NTradeInput):
                self.trade_entry[j][i].grid(row=j+2, column=i+1, sticky=W+E)
                        
        self.calcButton = Button(nwFrame, text="Calculate", command=self.calcOptions)
        self.calcButton.grid(row=self.NTradeInput+2, column=nTradeInputField-1, sticky=W+E)
        
        
        self.scenButton = Button(nwFrame, text="Scenario", command=self.scenarioWin)
        self.scenButton.grid(row=self.NTradeInput+2, column=nTradeInputField, sticky=W+E)
        

        
        
        fig = Figure(figsize=(10,5))
        a = fig.add_subplot(121)
        x,y=[],[]
        self.line1, = a.plot(x,y,color='blue')   
        self.line2, = a.plot(x,y,color='red')   
        #self.canvas = FigureCanvasTkAgg(fig, master=swFrame)
        #self.canvas.get_tk_widget().pack()
        
        
        b = fig.add_subplot(122)
        self.line3, = b.plot(x,y,color='green')   
        #self.canvas2 = FigureCanvasTkAgg(fig, master=swFrame)
        #self.canvas2.get_tk_widget().pack()
        
        self.canvas = FigureCanvasTkAgg(fig, master=swFrame)
        self.canvas.get_tk_widget().pack()
        
        
        resTitleLabel = Label(seFrame, text = "Portfolio Calc")
        resTitleLabel.pack()
        
        prtfRes = self.prtfCalc()
        s = f"FV:{prtfRes['FairValue']:.2f} Delta:{prtfRes['Delta']:.2f}"
        resLabel = Label(seFrame, text = s)
        resLabel.pack()
   
    def uniqueStrike(self, tradeRecord):
        return [101.0, 103.0]
    
    
    
    def scenarioWin(self):        
        newWindow = Toplevel(self.master)
        newWindow.title("Scenario")
   
        #Set the framework for the components     
        leftFrame = Frame(newWindow)
        leftFrame.pack(side=LEFT)
        rightFrame = Frame(newWindow)
        rightFrame.pack(side=RIGHT)
        self.rightFrame = rightFrame

        uniqStrike = self.uniqueStrike(self.tradeRecord)
        self.uniqStrike = uniqStrike
        
        titleLabel = Label(leftFrame, text = "Scenario")
        titleLabel.grid(row=0, column=0, columnspan=2)
        
        calcButton = Button(leftFrame, text = "Calculate", command=self.calcScen)
        calcButton.grid(row=self.NScenario+3, column=len(uniqStrike)+3)
        
        scenInputHeading = ["Spot", "DayToExpiry", "RiskFree"]
        for i in range(len(uniqStrike)):
            scenInputHeading.append(f"k={uniqStrike[i]:.2f}")
        self.scenInputHeading = scenInputHeading

        ivLable = Label(leftFrame, text = "ImplVol For strike=")
        ivLable.grid(row=0, column=4, columnspan=len(uniqStrike))

        for i,s in enumerate(scenInputHeading):
            l = Label(leftFrame, text = s)
            l.grid(row=1, column=i+1)
            
        for i in range(self.NScenario):
            l = Label(leftFrame, text = str(i+1))
            l.grid(row=i+2, column=0)
    
        self.scenarioEntry = [ [] for i in range(self.NScenario) ]                
        vcmdFloat = leftFrame.register(self.validateFloat) # we have to wrap the command
                
        #for _, dispName, _ in self.TradeInputField:
        #    trade_input_label.append(Label(nwFrame, text=dispName))
            
        for j in range(self.NScenario):            
            for i in range(3+len(uniqStrike)):
                self.scenarioEntry[j].append(Entry(leftFrame, validate="key", validatecommand=(vcmdFloat, '%P')))
                self.scenarioEntry[j][i].grid(row=j+2, column=i+1, sticky=W+E)
     

    def prtfCalc(self):
        calc = {}
        calc["FairValue"], calc["Delta"] = 0.0, 0.0
        for i, tr in enumerate(self.tradeRecord):
            if tr:
                #!!!!
                spot = 100
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"], tr["DvdYield"]/100.0)
                opt.setLevel(spot, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                calc["FairValue"] +=  opt.fairValue() * tr["Notional"]
                calc["Delta"] +=  opt.delta() * tr["Notional"]
        return calc           
   
    def perScenCalc(self):
        #scenCalc = [ {} for i in range(self.NScenario) ]
        res = [0] * self.NScenario
        for i, sc in enumerate(self.scenRecord):
            if sc:
                res[i] = self.scenCalc(sc)
        return res
        
    def scenCalc(self, scen):
        calc = {}
        calc["FairValue"], calc["Delta"] = 0.0, 0.0
        for i, tr in enumerate(self.tradeRecord):
            if tr:
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], scen["DayToExpiry"], tr["DvdYield"]/100.0)
                opt.setLevel(scen["Spot"], tr["ImplVol"]/100.0, scen["RiskFree"]/100.0)
                calc["FairValue"] +=  opt.fairValue() * tr["Notional"]
                calc["Delta"] +=  opt.delta() * tr["Notional"]
        return calc

    def calcScen(self):
        self.scenRecord = [ {} for i in range(self.NScenario) ]        
        
        for i,r in enumerate(self.scenarioEntry):
            
            nValidField = 0
            for elem in r:
                val = elem.get()
                if val: nValidField+=1
                

            if nValidField == len(self.uniqStrike)+3:
                statusStr = "ok"                      
                for j, fld in enumerate(self.scenInputHeading):
                    val = r[j].get().strip()
                    self.scenRecord[i][fld]=float(val)
                                                                
            elif nValidField >0:
                statusStr = "Input Error"
            else:
                statusStr = ""
            rowNumLabel = Label(self.rightFrame, text=statusStr )
            rowNumLabel.grid(row=i+3, column=0, padx=10, sticky=W)  
        
        scenCalcRes=self.perScenCalc()
        for i, calc in enumerate(scenCalcRes):
            if calc:
                s = f"{calc['FairValue']:2.3f} {calc['Delta']:2.3f}"
                calcLabel = Label(self.rightFrame, text=s)
                calcLabel.grid(row=i+3, column=1, sticky=W)  


     
    def calcOptions(self):
        self.tradeRecord = [ {} for i in range(self.NTradeInput) ]        
        
        for i,r in enumerate(self.trade_entry):
            
            nValidField = 0
            for elem in r:
                val = elem.get()
                if val: nValidField+=1
                

            if nValidField == len(self.TradeInputField):
                statusStr = "ok"      
                
                for j, field in enumerate(self.TradeInputField):
                    fld, _, ftype = field
                    val = r[j].get().strip()
                    print(val)
                    if ftype == "f":
                        self.tradeRecord[i][fld]=float(val)
                    elif ftype=="putCall":
                        self.tradeRecord[i][fld]= "Call" if val.upper() == "C" else "Put"
                                                                
            elif nValidField >0:
                statusStr = "Input Error"
            else:
                statusStr = ""
            rowNumLabel = Label(self.neFrame, text=statusStr )
            rowNumLabel.grid(row=i+1, column=0, padx=10, sticky=W)  
        
        tradeCalc=self.perTradeCalc()
        for i, calc in enumerate(tradeCalc):
            if calc:
                s = f"{calc['FairValue']:2.3f} {calc['Delta']:2.3f}"
                calcLabel = Label(self.neFrame, text=s)
                calcLabel.grid(row=i+1, column=1, sticky=W)  
                
        sArr = [ 80.0+2.0*i for i in range(21)]
        payoffNow = self.payoffProfile(sArr)
        payoffExpiry = self.payoffProfile(sArr, True)
        self.line1.set_data(sArr, payoffNow)
        self.line2.set_data(sArr, payoffExpiry)
        ax = self.canvas.figure.axes[0]
        ax.set_xlim(min(sArr), max(sArr))
        ax.set_ylim(min(payoffExpiry)*1.01, max(payoffExpiry)*1.01)
        #self.canvas.draw()
        
        deltaProfile = self.deltaProfile(sArr)
        self.line3.set_data(sArr, deltaProfile)
        #ax = self.canvas2.figure.axes[1]
        ax = self.canvas.figure.axes[1]
        ax.set_xlim(min(sArr), max(sArr))
        ax.set_ylim(min(deltaProfile)*1.01, max(deltaProfile)*1.01)
        #self.canvas2.draw()
        self.canvas.draw()
            
    def payoffProfile(self, sArr, isAtExpiry=False):
        payoff = [0.0] * len(sArr)
        for tr in self.tradeRecord:
            if tr:
                if isAtExpiry: 
                    opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], 0.00, tr["DvdYield"]/100.0)
                else:                    
                    opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"], tr["DvdYield"]/100.0)                
                for i,s in enumerate(sArr):
                    opt.setLevel(s, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                    payoff[i] += opt.fairValue()*tr["Notional"]            
        return payoff

    def deltaProfile(self, sArr):
        deltaArr = [0.0] * len(sArr)
        for tr in self.tradeRecord:
            if tr:
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"], tr["DvdYield"]/100.0)                
                for i,s in enumerate(sArr):
                    opt.setLevel(s, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                    deltaArr[i] += opt.delta()*tr["Notional"]            
        return deltaArr
   
         
    
    def perTradeCalc(self):
        tradeCalc = [ {} for i in range(self.NTradeInput) ]
        for i, tr in enumerate(self.tradeRecord):
            if tr:
                opt = EuropeanOption(tr["CallOrPut"]=="Call", tr["Strike"], tr["DayToExpiry"], tr["DvdYield"]/100.0)
                #!!!! spot
                spot = 100
                opt.setLevel(spot, tr["ImplVol"]/100.0, tr["RiskFree"]/100.0)
                tradeCalc[i]["FairValue"] =  opt.fairValue()
                tradeCalc[i]["Delta"] =  opt.delta()
        return tradeCalc
                
                

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

#    def update(self, method):
#        if method == "add":
#            self.total += self.entered_number
#        elif method == "subtract":
#            self.total -= self.entered_number
#        else: # reset
#            self.total = 0
#
#        self.total_label_text.set(self.total)
#        self.entry.delete(0, END)

root = Tk()
my_gui = OptionViewerGUI(root)
root.mainloop()