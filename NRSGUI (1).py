"""
CSC308 Term Project: Python PWR Sim GUI
Johnathon Glatz, Shawn Carl, Dalton Obitko
4/25/2021 - v0.85
"""
"""
Description: Basic simulation game for an older generation pressurized
water fission reactor. GUI and terminal based. Provides player with
control over the power plant's reactor control rods, primary coolant
pumps, secondary coolant pumps, and emergency coolant pumps, as well
as SCRAM controls and damage control teams. Game is turn based with
an adjustable length of 5 to 150 turns. Primary objective is to generate
as much power as possible in the turns

Classes:
    PWRSim()
        Description:
        Methods:
            __init__:
                Description:
                Parameters:
                Returns:
Functions:
    main():
        Description: Main function. Prompts user for game length between 5 and 150 then starts game based on user's answer
        Parameters: None
        Returns: 0 on good execution
            
"""
import tkinter as gui   #main gui module
from tkinter.messagebox import *  #gui popups

#prints startup text block
def help():
    print('------------------------------------------------------------\n')
    print("""
Welcome to the Python Pressurized Water Reactor Sim!
This is a gamified simulation of an older generation
PWR power plant. PWRs are the most common form of
power generating nuclear reactors in the world. Modern
PWRs are incredibly safe and are designed to make
meltdowns all but impossible. That being said, both TMI-2
and Chernobyl No.4 were PWRs that failed due to poor
ancillary equipment and operator training.
In this sim you will control the daily operations
at a brand new (for the 1970s) PWR power plant with
a nameplate safe output rating of 500 MWe per day. You will
be given full control of the reactor's control rod actuators,
primary coolant pumps, seconday coolant pumps, and emergency
coolant pumps. Your goal is to generate as much energy as
possible in a set number of days without destroying the plant.
Oh, one last thing. None of the safety interlocks are enabled,
so a SCRAM will not be triggered automatically no matter how
much damage the plant takes. A real leader goes down with
the ship.
Tips:
    - Higher values for control rod depth raises the rods out
    of the core. This increases core power output.
    - The maximum safe temperature of the reactor is 700F
    - The maximum safe temperature of the heat exhangers is 450F
    - The maximum safe temperature of the condensor is 200F
    Exceed any of these temperature limits and you will damage
    the associated components. A damaged plant will tend to run
    hotter and produce less power.
    - A safe but inefficient way to start the plant is to set
    primary and secondary coolant pumps to 100% and control rods
    to 15%. This will bring the core to a safe generating
    temperature, but it is very slow and wastes fuel.
Stay safe and good luck!\n""")
    print('------------------------------------------------------------\n')


class PWRSim():
    def __init__(self, gameLength):
        self.rState = {'rodPosition':0, 'pPump':0, 'sPump':0, 'ePump':0, 'rTemp':70.0,
            'eTemp':80.0, 'cTemp':80.0, 'damage':0, 'fuel':100.0, 'dailyOutput':0,
            'totalOutput':0, 'day':1, 'damageControl':False, 'scram':False, 'gameLength':100
        }

        self.rState['gameLength'] = gameLength
        
        self.window = gui.Tk()  #create the window
        self.window.minsize(580,280)    #set a minimum size x,y in pixels
        self.window.columnconfigure((0,1,2,3,4), weight=1)   #set row and column weights for UI scaling
        self.window.rowconfigure((0,1,2,3,4,5,6,7,8), weight=1)
        self.window.title('Python Pressurized Water Reactor Simulator')  #give it a title bar

        self.annPanel = gui.Canvas(self.window,width=100,height=100, bg='black')  #create a canvas for annunciator panel
        self.annPanel.grid(row=0, rowspan=2, column=0, columnspan=5, sticky = 'NESW') #set the canvas onto the grid layout

        self.rodEntry = gui.Entry(width = 10, justify = 'center')   #create entry fields and place on grid layout
        self.rodEntry.grid(row=2)
        self.pcEntry = gui.Entry(width = 10, justify = 'center')
        self.pcEntry.grid(row=2, column=1)
        self.scEntry = gui.Entry(width = 10, justify = 'center')
        self.scEntry.grid(row=2, column=2)
        self.ecEntry = gui.Entry(width = 10, justify = 'center')
        self.ecEntry.grid(row=2, column=3)

        self.scramButton = gui.Button(text = 'SCRAM', width = 8, bg = '#a7a7a7', command = self.triggerScram)   #create scram button
        self.scramButton.grid(row=2, column=4)
        self.rodLabel = gui.Label(text = 'Control Rods')#create labels
        self.rodLabel.grid(row=3)
        self.pcLabel = gui.Label(text = 'Primary Coolant')
        self.pcLabel.grid(row=3, column=1)
        self.scLabel = gui.Label(text = 'Secondary Coolant')
        self.scLabel.grid(row=3, column=2)
        self.ecLabel = gui.Label(text = 'Emergency Coolant')
        self.ecLabel.grid(row=3, column=3)
        self.damageControlButton = gui.Button(text = 'Damage\nControl', width = 8, bg = '#a7a7a7', command = self.triggerDamageControl)#create damage control button
        self.damageControlButton.grid(row=3, column=4)
        self.rTempDisplay = gui.Label(text = format(self.rState['rTemp'], '.2f') + ' F')
        self.rTempDisplay.grid(row=4)
        self.eTempDisplay = gui.Label(text = format(self.rState['eTemp'], '.2f') + ' F')
        self.eTempDisplay.grid(row=4, column=1)
        self.cTempDisplay = gui.Label(text = format(self.rState['cTemp'], '.2f') + ' F')
        self.cTempDisplay.grid(row=4, column=2)
        self.fuelDisplay = gui.Label(text = format(self.rState['fuel'], '.2f') + ' %')
        self.fuelDisplay.grid(row=4, column=3)
        self.damageDisplay = gui.Label(text = str(self.rState['damage']) + ' %')
        self.damageDisplay.grid(row=4, column=4)
        self.rTempLabel = gui.Label(text = 'Reactor Temp')
        self.rTempLabel.grid(row=5)
        self.eTempLabel = gui.Label(text = 'Exchanger Temp')
        self.eTempLabel.grid(row=5, column=1)
        self.cTempLabel = gui.Label(text = 'Condensor Temp')
        self.cTempLabel.grid(row=5, column=2)
        self.fuelLabel = gui.Label(text = 'Fuel')
        self.fuelLabel.grid(row=5, column=3)
        self.damageLabel = gui.Label(text = 'Damage')
        self.damageLabel.grid(row=5, column=4)
        self.dayDisplay = gui.Label(text = str(self.rState['day']) + ' / ' + str(self.rState['gameLength']))

        self.layoutLine = gui.Canvas(self.window,width=100,height=1, bg='black')  #create a canvas for annunciator panel
        self.layoutLine.grid(row=6, rowspan=1, column=0, columnspan=5, sticky = 'NESW') #set the canvas onto the grid layout
        
        self.dayDisplay.grid(row=7)
        self.dailyPowerDisplay = gui.Label(text = format(self.rState['dailyOutput'], '.3f') + ' MWe')
        self.dailyPowerDisplay.grid(row=7, column=1)
        self.totalPowerDisplay = gui.Label(text = format(self.rState['totalOutput'], '.3f') + ' MWe')
        self.totalPowerDisplay.grid(row=7, column=2)
        self.dayLabel = gui.Label(text = 'Current Day').grid(row=8)
        self.dailyPowerLabel = gui.Label(text = 'Daily Power Generated')
        self.dailyPowerLabel.grid(row=8, column=1)
        self.totalPowerLabel = gui.Label(text = 'Total Power Generated')
        self.totalPowerLabel.grid(row=8, column=2)
        self.helpButton = gui.Button(text = 'Help', width = 8, bg = '#a7a7a7', command = self.helpscreen) #create help button
        self.helpButton.grid(row=7, column=4)
        self.nextDayButton = gui.Button(text = 'Next Day', width = 8, bg = '#a7a7a7', command = self.gameloop) #create next day button
        self.nextDayButton.grid(row=8, column=4)

        #fill in annunciator panel, x and y position are center of text
        self.damageControlAnn = self.annPanel.create_text(58,30, text='DAMAGE\nCONTROL', justify=gui.CENTER, fill='red', state=gui.HIDDEN) #annunciators red when on, hidden when off for colorblind accessibility
        self.rTempAnn = self.annPanel.create_text(174,30, text='REACTOR\nOVERTEMP', justify=gui.CENTER, fill='red', state=gui.HIDDEN)
        self.eTempAnn = self.annPanel.create_text(290,30, text='EXCHANGER\nOVERTEMP', justify=gui.CENTER, fill='red', state=gui.HIDDEN)
        self.cTempAnn = self.annPanel.create_text(406,30, text='CONDENSOR\nOVERTEMP', justify=gui.CENTER, fill='red', state=gui.HIDDEN)
        self.powerLimitAnn = self.annPanel.create_text(522,30, text='OVER POWER\nLIMIT', justify=gui.CENTER, fill='red', state=gui.HIDDEN)
        self.genOfflineAnn = self.annPanel.create_text(58,70, text='GENERATORS\nOFFLINE', justify=gui.CENTER, fill='red', state=gui.NORMAL)
        self.lowPAnn = self.annPanel.create_text(174,70, text='LOW PRIMARY\nFLOW', justify=gui.CENTER, fill='red', state=gui.NORMAL)
        self.lowCAnn = self.annPanel.create_text(290,70, text='LOW SECONDARY\nFLOW', justify=gui.CENTER, fill='red', state=gui.NORMAL)
        self.eOpenAnn = self.annPanel.create_text(406,70, text='EMERGENCY\nCOOLANT', justify=gui.CENTER, fill='red', state=gui.HIDDEN)
        self.lowFuelAnn = self.annPanel.create_text(522,70, text='LOW FISSION\nFUEL', justify=gui.CENTER, fill='red', state=gui.HIDDEN)

        gui.mainloop()  #start tkinter mainloop to wait for gui events

    def helpscreen(self):
        helpStr = """
Welcome to the Python Pressurized Water Reactor Simulator!
At the top of the GUI is a black box. You might see some red
text here. These are annunciators or warning lights for the
power plant. Ideally, you want these all to disappear (except
the "OVER POWER LIMIT" light). That one is actually a good sign
if you aren't overheating the plant. You should also see 4 gray
buttons on the right. The SCRAM button, short for "Safety Rod
Axe Man" if you're a fan of Enrico Fermi, is a last ditch, fast
method to shut down a fission reactor. In the real world this
would plunge the control rods and likely inject a neutron poison
such as boron into the coolant. In the sim it is simply a way to
end game at any time you wish. The damage control button is used
dispatch damage control teams to slowly repair the plant as long
as the reactor temperature remains below 212F. This may be neccessary
if you are playing a long game and trying for a high power output.
The help button get you to this screen and the next day button simply
advances the day count forward and calculates the new plant state.
Directly under the black annunciator panel is 4 text entry fields.
These are where you set the control input for the reactor control
rods, primary coolant, secondary coolant, and emergency coolant.
All of thesemust be integer values between 0 and 100. The control rods
are the reactor's neutron moderators. A higher value means less
control rod in the reactor, thus less moderation and a higher heat
output. The energy in the plant flows from reactor to condensor through
the exchangers via coolant. More coolant flow means more energy travel.
Ideally, all of the reactors heat should be taken up by the exchangers,
driving the generators. Any heat in the condensors is wasted energy.
The term "Emergency Coolant" is somewhat of a misnomer. In the real world
emergency coolant tanks are not only used in emergencies but also in the
daily operation of the plant to refill the coolant loop to account for
leaks. As this game does not simulate coolant levels or leaks, you may
instead use it as a backup to the primary coolant if you must pull
more heat out of the reactor than the primary loop can sustain. This
should be all you need to get the reactor going. Remember, it is only
a simulation so part of the fun is learning the mechanics on your own!"""
        gui.messagebox.showinfo(title='Help', message=str(helpStr));

    def updateEntries(self):    #return True on success, False for bad values
        temp = 0
        validInputs = True

        try:
            temp = int(self.rodEntry.get())
            if(temp >= 0 and temp <= 100):
                self.rState['rodPosition'] = temp
            else:
                validInputs = False
        except:
            validInputs = False
            
        try:
            temp = int(self.pcEntry.get())
            if(temp >= 0 and temp <= 100):
                self.rState['pPump'] = temp
            else:
                validInputs = False
        except:
            validInputs = False
            
        try:
            temp = int(self.scEntry.get())
            if(temp >= 0 and temp <= 100):
                self.rState['sPump'] = temp
            else:
                validInputs = False
        except:
            validInputs = False
            
        try:
            temp = int(self.ecEntry.get())
            if(temp >= 0 and temp <= 100):
                self.rState['ePump'] = temp
            else:
                validInputs = False
        except:
            validInputs = False

        return validInputs

    def gameloop(self):
        print('DEBUG: gameloop triggered')

        if(int(self.rState['day']) >= int(self.rState['gameLength'])):  #check if the day counter is up
            gui.messagebox.showinfo(title='Game over', message=str('GAME OVER: Your ' + str(self.rState['day']) + " days are up. Let's see how you did."))
            self.endScreen()
        else:
            if((self.updateEntries()) != True):    #if we have bad input do not update the game state, instead throw an error popup
                gui.messagebox.showerror(title='INPUT ERROR', message='Rod position, primary, secondary, and emergency pumps must be set to an integer value between 0 and 100 to continue!')
            else:
                self.updatePlantState()
                self.updateLabels()
                self.updateAnnunciators()

    def updatePlantState(self):
        def rtrMap(val, inMin, inMax, outMin, outMax):  #math from Arduino C++ map function
            return ((val - inMin) * (outMax - outMin) / (inMax - inMin) + outMin)
        
        turbineEfficiency = 0.83 - (self.rState['damage'] / 200)

        #term 1 gives the reactor a positive void coefficient, similar to Chernobyl No.4, higher temps decrease reactor stability and accelerate reaction faster
        #term 2 maps rod position to a value between -100 and 100 for reasonable temperature deltas
        #term 3 prevents the reactor from creating free energy with no fuel
        #term 4 increases temperature by 1 for each point of damage
        #reactor stablizes at 15% rods, 100% fuel, 0% damage, 600F core temp
        #(t/600) (((r-0) * (100-(0-100)) / (100-0) + (-100)) + ((f-0) * (70-(-150)) / (100-0) + (-150)) + d)
        #tune terms 2 and 3 for balance/realism
        if self.rState['rodPosition'] > 0:
            rTempDelta = (self.rState['rTemp']/600) * (rtrMap(self.rState['rodPosition'], 0, 100, -100, 100) + rtrMap(self.rState['fuel'], 0, 100, -150, 70) + self.rState['damage'])
        elif self.rState['rTemp'] > 70:
            rTempDelta = -2
        else:
            rTempDelta = 0
            
        #this block simulates the effects of coolant flow on reactor core temperature
        if rTempDelta > 0:  #if the reactor is heating, slow heating below 50% core flow, else speed it up
            if (self.rState['pPump']+self.rState['ePump'] > 50):    #high flow
                rTempDelta -= rtrMap((self.rState['pPump']+self.rState['ePump']), 50, 200, 5, 25)
            else:   #low flow
                rTempDelta += rtrMap((self.rState['pPump']+self.rState['ePump']), 0, 50, 25, 5)
        elif rTempDelta < 0:    #if the reactor is cooling, slow cooling below 50% core flow, else speed it up
            if (self.rState['pPump']+self.rState['ePump'] > 50):    #high flow
                rTempDelta -= rtrMap((self.rState['pPump']+self.rState['ePump']), 50, 200, 5, 25)
            else:   #low flow
                rTempDelta += rtrMap((self.rState['pPump']+self.rState['ePump']), 0, 50, 25, 5)
        elif rTempDelta == 0 and self.rState['rTemp'] == 70:   #let the reactor be stable when off       ####THESE NEED EDITED AS THEY ALLOW FREE ENERGY GENERATION
            pass #this is a no-op to satisfy interpreter
        else:   #if the reactor is running do not let reach perfect stability
            if self.rState['pPump'] > 20 or self.rState['ePump'] > 40:
                rTempDelta -= 2
            else:
                rTempDelta += 2

        self.rState['rTemp'] += rTempDelta   #set new reactor core temperature
        
        #heat exchanger temp based on reactor core temp and primary and secondary coolant flow
        #((rState['rTemp'] * 1/rState['pCoolant']) takes energy into the exchanger based on core temp and secondary coolant flow
        self.rState['eTemp'] = self.rState['rTemp'] - (self.rState['sPump'] * 1.5)

        if self.rState['eTemp'] >= 212:  #if the exchanger is above boiling point
            #every degree of temperature generates 1.4MWe
            self.rState['dailyOutput'] = self.rState['eTemp'] * 1.4

        #condensor temp based on energy drop from turbines
        self.rState['cTemp'] = self.rState['eTemp'] - (self.rState['eTemp'] * turbineEfficiency)

        #ensure temperatures don't drop below ambient
        if(self.rState['rTemp']) < 70:
            self.rState['rTemp'] = 70
        if(self.rState['eTemp']) < 80:
            self.rState['eTemp'] = 80
        if(self.rState['cTemp']) < 80:
            self.rState['cTemp'] = 80
        
        #Damage logic block
        if(self.rState['rTemp'] > 700):  #If reactor over 700F add 1 point of damage for each 50 degrees
            self.rState['damage'] += int(round((self.rState['rTemp'] - 700) / 50))
            self.rState['damage'] += 1
        if(self.rState['eTemp'] > 450):  #If exchangers over 450F add add 1 point of damage for each 50 degrees
            self.rState['damage'] += int(round((self.rState['eTemp'] - 450) / 50))
        if(self.rState['cTemp'] > 212):  #If condensor over 200F add add 1 point of damage for each 50 degrees
            self.rState['damage'] += int(round((self.rState['cTemp'] - 212) / 50))

        if(self.rState['damageControl']):
            if(self.rState['rTemp'] < 212):
                if(self.rState['damage'] > 0):
                    self.rState['damage'] -= 2
                if(self.rState['damage'] == 0):
                    gui.messagebox.showinfo(title='Repairs complete', message='Repairs on the plant have been completed. Damage control measures deactivated.')
                    self.rState['damageControl'] = False
            else:
                gui.messagebox.showinfo(title='Damage control parties recalled!', message='WARNING: Core temperatures exceeded 212F. All damage control teams have been recalled for safety.')
                self.rState['damageControl'] = False

        if(self.rState['damage'] >= 100):   #If plant damage reaches or exceeds 100, end the game
            gui.messagebox.showinfo(title='Game over', message='GAME OVER: You have destroyed the plant. Nearby gas turbine generators will take up the grid load, but thousands of families have been forced to evacuate the area. Be more careful next time!')
            self.endScreen()

        #update plant output, fuel totals, and increment day counter
        self.rState['totalOutput'] += self.rState['dailyOutput']
        self.rState['fuel'] -= self.rState['rodPosition'] / 150
        self.rState['day'] += 1

    def updateAnnunciators(self):   #update the annunciator panel lights
        if(self.rState['damageControl'] == True):   #damage control indicator
            self.annPanel.itemconfig(self.damageControlAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.damageControlAnn, state=gui.HIDDEN)

        if(self.rState['rTemp'] > 700):   #reactor overtemp indicator
            self.annPanel.itemconfig(self.rTempAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.rTempAnn, state=gui.HIDDEN)

        if(self.rState['eTemp'] > 450):   #exchanger overtemp indicator
            self.annPanel.itemconfig(self.eTempAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.eTempAnn, state=gui.HIDDEN)

        if(self.rState['cTemp'] > 212):   #condensor overtemp indicator
            self.annPanel.itemconfig(self.cTempAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.cTempAnn, state=gui.HIDDEN)

        if(self.rState['dailyOutput'] >= 500.0):   #plant power limit indicator
            self.annPanel.itemconfig(self.powerLimitAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.powerLimitAnn, state=gui.HIDDEN)

        if(self.rState['eTemp'] < 212.0):   #secondary loop low temp/generator inactive indicator
            self.annPanel.itemconfig(self.genOfflineAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.genOfflineAnn, state=gui.HIDDEN)

        if(self.rState['pPump'] <= 10):   #primary loop low pressure indicator
            self.annPanel.itemconfig(self.lowPAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.lowPAnn, state=gui.HIDDEN)

        if(self.rState['sPump'] <= 10):   #secondary loop low pressure indicator
            self.annPanel.itemconfig(self.lowCAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.lowCAnn, state=gui.HIDDEN)

        if(self.rState['ePump'] > 0):   #emergency coolant valve indicator
            self.annPanel.itemconfig(self.eOpenAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.eOpenAnn, state=gui.HIDDEN)

        if(self.rState['fuel'] <= 15.0):   #fuel low indicator
            self.annPanel.itemconfig(self.lowFuelAnn, state=gui.NORMAL)
        else:
            self.annPanel.itemconfig(self.lowFuelAnn, state=gui.HIDDEN)

    def updateLabels(self): #Update all of the plant state labels
        self.rTempDisplay.config(text=format(self.rState['rTemp'], '.2f') + ' F')
        self.eTempDisplay.config(text=format(self.rState['eTemp'], '.2f') + ' F')
        self.cTempDisplay.config(text=format(self.rState['cTemp'], '.2f') + ' F')
        self.fuelDisplay.config(text=format(self.rState['fuel'], '.2f') + ' %')
        self.damageDisplay.config(text=str(self.rState['damage']) + ' %')
        self.dayDisplay.config(text=str(self.rState['day']) + ' / ' + str(self.rState['gameLength']))
        self.dailyPowerDisplay.config(text=format(self.rState['dailyOutput'], '.3f') + ' MWe')
        self.totalPowerDisplay.config(text=format(self.rState['totalOutput'], '.3f') + ' MWe')

    def triggerScram(self): #end the game early if user accepts prompt
        userReturn = gui.messagebox.askyesno(title='Are you sure?', message='Are you sure you want to SCRAM the reactor?.')
        if(userReturn == True):
            self.endScreen()
            
    def triggerDamageControl(self):
        if(self.rState['damageControl'] == True):
            self.rState['damageControl'] = False
            self.annPanel.itemconfig(self.damageControlAnn, state=gui.HIDDEN)
            gui.messagebox.showinfo(title='Damage control deactivated', message='Damage control measures deactivated.')
        else:
            if(self.rState['rTemp'] < 212.0):
                self.rState['damageControl'] = True
                self.annPanel.itemconfig(self.damageControlAnn, state=gui.NORMAL)
                gui.messagebox.showinfo(title='Damage control activated', message='Damage control measures activated. Keep core temperatures below 212F for crew safety!')
            else:
                self.annPanel.itemconfig(self.damageControlAnn, state=gui.HIDDEN)
                gui.messagebox.showinfo(title='Core temperatures too high', message='Reactor core temperatures are too high to send in the repair crews. Lower temperatures to <212F and try again.')

    def endScreen(self):
        print('DEBUG: Game over.')
        #print out game statistics, add in a profit/losses metric based on power generated and ending damage

def main():
    validInput = False
    gameLength = 100
    
    #On startup output help prompt then get a game length from user
    help()
    while validInput == False:
        userin = input('Input a game length in days (min:5 max:150) or press enter to play\nwith the default 100 day game: ')
        if userin == '':
            validInput = True
        else:
            try:
                userin = int(userin)
                if userin >= 5 and userin <= 150:
                    gameLength= userin
                    validInput = True
                else:
                    print('ERROR: Game length must be between 5 and 150 days.')
            except:
                print('ERROR: Invalid length. Please use a positive integer between 5 and 150 only.')

    print('Game length set to', gameLength, 'days.')
    print('Starting...')
    
    pwrWindow = PWRSim(gameLength)    #Start the game with gui
    return 0

main()
