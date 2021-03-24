import pandas as pd
import numpy as np
from numpy.fft import rfft, rfftfreq
import matplotlib.pyplot as plotter
import datetime
import time
from datetime import datetime
from os import listdir
import ctypes 
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')

filenames_list = ''

class MyApp(App):
    
    def build(self):
        #return Label(text='Hello World')
        Window.bind(on_request_close=self.on_request_close)
        #Run_Button = Button(text='Analyze!', font_size=40)
        #Run_Button.bind(on_release=MyApp.pressed)
        #self.add_widget(self.Run_Button)
        
        btn = Button(text ="Analyze Data", 
        font_size ="20sp", 
        background_color =(1, 1, 1, 1), 
           color =(1, 1, 1, 1),  
           size =(32, 32), 
           size_hint =(.2, .2), 
           pos =(300, 250)) 
        btn.bind(on_release=MyApp.pressed)
        return btn 
        #return Label(text='Child')
    
        
    
    
    def pressed(self):
        #print("button pressed")
        
        
    
    #Converting the Timestamp from the rawdata into seconds
        def find_csv_filenames( path_to_dir, suffix=".csv" ):
           filenames = listdir(path_to_dir)
           ctypes.windll.user32.MessageBoxW(0, 'To batch process the respiratory data,\nmake sure the file names have a "BR" ending\nand are placed in the same folder of this program.\n\n For example,\n"Jenner_BR.csv"\n"Sarah_BR.csv" \n\n Hit OK to RUN', "Respiratory Analysis", 0)  
           return [ filename for filename in filenames if filename.endswith( suffix ) or filename.endswith (suffix.upper()) ]
        
        filenames = find_csv_filenames(".")
        
              #  process_BR(filenames[x])
        
        def process_BR(name):
            
                
            
                if 'BR' in name:
                       
                    global filenames_list
                    filenames_list = filenames_list + name + "\n"
                    
                    col_list = ["Timestamp", "Mode","Data"]
                    df = pd.read_csv(name, sep=',', usecols=col_list, encoding = 'utf8')
                  
                    df = df.dropna() #delete rows with NaN data
                                
                    check_string = df['Timestamp'].iloc[0] #Converting the new data format from Adafruit MC to the original format
                    check_data = len(str(df['Data'].iloc[0]))
                    
                   
                    if check_string.count(':') == 3:
                                
                        for x in range(0,len(df['Timestamp'])):
                            
                            check_string = str(df['Timestamp'].iloc[x])
                            last_char_index = check_string.rfind(":")
                            check_string = check_string[:last_char_index] + "." + check_string[last_char_index+1:]
                            df['Timestamp'].iloc[x] = check_string
                            
                                                
                    if check_data > 9:
                                
                        for x in range(0,len(df['Data'])):
                            
                                                                 
                            split_string = str(df['Data'].iloc[x])
        
                            
                            split_string = split_string.split(' ',1)
        
                            split_string = split_string[0]
                            if split_string == '':
                                split_string = 0
                            #print(split_string)               
                            df['Data'].iloc[x] = int(split_string)
                            
                            #df['Data'].iloc[x] = int(df['Data'].iloc[x])        
                    
                    
                    
                    
                    
                    
                    df['reftime'] = df['Timestamp'].iloc[0]
                    
                    d1 = df['reftime'].apply(lambda x: datetime.strptime(x, '%H:%M:%S.%f'))
                    d2 = df['Timestamp'].apply(lambda x: datetime.strptime(x, '%H:%M:%S.%f'))
                    
                    df['diff'] = d2 - d1
                    df['seconds'] = df['diff'].dt.total_seconds()
                    
                    D_Mean = df['Data'].mean()
                    
                    
            
                    
                    df = df[df['Data'] > (D_Mean/1.6)] #delete kinking data
                    
                    #print(max(df['seconds']))
                    
                    n=len(df["Data"])
                    #print(n)
                    
                    
                    dt=max(df['seconds'])/n #time increment in each data
                    
                    
                    acc=df["Data"].values.flatten() #to convert DataFrame to 1D array
                    
                    #acc value must be in numpy array format for half way mirror calculation
                    fft=rfft(acc)*dt
                    freq=rfftfreq(n,d=dt)
                    FFT=abs(fft)
                    
                    figure, axis = plotter.subplots(3, 1,figsize=(20,20))
                    plotter.subplots_adjust(hspace=0.4)
                    
                    
                    axis[0].set_title('Respiratory Pattern',fontsize = 38.0)
                    axis[0].plot(df["seconds"], df["Data"])
                    
                    axis[0].tick_params(axis = 'both', which = 'major', labelsize = 24)
                    axis[0].tick_params(axis = 'both', which = 'minor', labelsize = 24)
                    
                    axis[0].locator_params(axis="x", nbins=10) #set ticks intervals
                    
                    axis[0].set_xlabel('Time (s)',fontsize = 30.0)
                    axis[0].set_ylabel('Amplitude (arb.)',fontsize = 30.0)
                    
                    
                    dg = pd.DataFrame({'b_rate': freq*60, 'FFT': list(FFT), 'fft': list(fft)}, columns=['b_rate', 'FFT','fft']) #Convert NumPy three 1D Numpy Arrays to DataFram dg
                    
                    dg = dg[dg['b_rate'] > 1]
                    
                    axis[1].set_title('FFT',fontsize = 38.0)
                    axis[1].plot(freq*60, FFT,c = 'r') #axis[1].plot((1/freq)/60*100*(60/(n*dt)), FFT) #https://nbviewer.jupyter.org/github/balzer82/FFT-Python/blob/master/FFT-Tutorial.ipynb
                    
                    axis[1].tick_params(axis = 'both', which = 'major', labelsize = 24,width = 5)
                    axis[1].tick_params(axis = 'both', which = 'minor', labelsize = 24)
                    #axis[1].fill_between((1/(1/freq))*60, FFT,alpha=0.5, color='red')
                    #axis[1].yticks(np.arange(0, max(FFT), 2))
                    
                    axis[1].set_xlabel('Breath Rate (breaths/min)', fontsize = 30.0)
                    axis[1].set_ylabel('Amplitude (arb.)',fontsize = 30.0)
                    
                    avg_b_rate = dg['b_rate'].iloc[dg['FFT'].idxmax()] # Finding the average breath rate from FFT
                    
                    formatted_string = "{:.2f}".format(avg_b_rate) # Rounding the average breath rate to 2 decimal places
                    rnd_avg_b_rate = str(float(formatted_string))+" breaths/min"
                    
                    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
                    axis[1].text(0.73, 0.95, rnd_avg_b_rate, transform=axis[1].transAxes, fontsize=30,
                            verticalalignment='top', bbox=props)
                    
                    
                    axis[2].set_title('fft',fontsize = 38.0)
                    axis[2].plot(freq*60, fft,c = 'g') #axis[1].plot((1/freq)/60*100*(60/(n*dt)), FFT) #https://nbviewer.jupyter.org/github/balzer82/FFT-Python/blob/master/FFT-Tutorial.ipynb
                    
                    
                    
                    axis[2].tick_params(axis = 'both', which = 'major', labelsize = 24,width = 5)
                    axis[2].tick_params(axis = 'both', which = 'minor', labelsize = 24)
                    
                    #axis[1].yticks(np.arange(0, max(FFT), 2))
                    
                    axis[2].set_xlabel('Inhale [-] or Exhale [+] Rate (/min)', fontsize = 30.0)
                    axis[2].set_ylabel('Amplitude (arb.)',fontsize = 30.0)
                    
                    
                    
                    #axis[1].set_title('FFT')
                    #axis[1].plot((1/freq), FFT) #axis[1].plot((1/freq)/60*100*(60/(n*dt)), FFT) #https://nbviewer.jupyter.org/github/balzer82/FFT-Python/blob/master/FFT-Tutorial.ipynb
                    #axis[1].set_xlabel('Period')
                    #axis[1].set_ylabel('Absolute Amplitude')
                    
                    #axis[0].locator_params(axis="x", nbins=10) #set ticks intervals
                    #axis[0].set_xlim([0, 70]) #set x ticks limits
                    axis[0].set_ylim([D_Mean+200,D_Mean-200]) #set y ticks limits
                    
                    FFT_Max_Lim = max(dg['FFT'])*1.1
                    #print(max(dg['FFT']))
                    
                    axis[1].locator_params(axis="x", nbins=10) #set ticks intervals
                    axis[1].set_xlim([0, 70]) #set x ticks limits
                    axis[1].set_ylim([-100,FFT_Max_Lim]) #set y ticks limits
                    
                    
                    axis[2].locator_params(axis="x", nbins=10) #set ticks intervals
                    axis[2].set_xlim([0, 70]) #set x ticks limits
                    axis[2].set_ylim([FFT_Max_Lim*(-1.1),FFT_Max_Lim*1.1]) #set y ticks limits
                    
                    #print(df["seconds"])
                    now = datetime.now()
                    now = now.strftime("%m_%d_%Y_%H_%M_%S")
                    now = str(now)
                    new_name = name.replace(".csv", "")
                    plotter.savefig(new_name+'_processed_'+now+'.jpg')
                    plotter.show()
        
               
        
        #print(df["Data"])
        for x in range(0,len(filenames)):
            process_BR(filenames[x])
            
        
        ctypes.windll.user32.MessageBoxW(0, 'The following files have been processed: \n\n' + filenames_list, "Job Summary", 0)  
        
    
    

    def on_request_close(self, *args):
        self.textpopup(title='Exit', text='Are you sure?')
        return True

    def textpopup(self, title='', text=''):
        """Open the pop-up with the name.

        :param title: title of the pop-up to open
        :type title: str
        :param text: main text of the pop-up to open
        :type text: str
        :rtype: None
        """
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=text))
        mybutton = Button(text='OK', size_hint=(1, 0.25))
        box.add_widget(mybutton)
        popup = Popup(title=title, content=box, size_hint=(None, None), size=(600, 300))
        mybutton.bind(on_release=self.stop)
        popup.open()
    
if __name__ == '__main__':
    MyApp().run()
    


  