# import kivy module  
import kivy  
    
# this restrict the kivy version i.e  
# below this kivy version you cannot  
# use the app or software  
kivy.require("1.9.1") 
  
# Kivy Example App for the slider widget 
from kivy.app import App 
  
# The GridLayout arranges children in a matrix. 
from kivy.uix.gridlayout import GridLayout 
  
# If we will not import this module 
# It will through the error 
from kivy.uix.slider import Slider 
  
# The Label widget is for rendering text. 
from kivy.uix.label import Label 
  
# Property that represents a numeric value 
# within a minimum bound and / or maximum 
# bound – within a numeric range. 
from kivy.properties  import NumericProperty 
  
# class in which we are defining the 
# sliders and its effects 
class WidgetContainer(GridLayout): 
  
    def __init__(self, **kwargs): 
          
        # super function can be used to gain access  
        # to inherited methods from a parent or sibling  
        # class that has been overwritten in a class object.  
        super(WidgetContainer, self).__init__(**kwargs) 
  
        # 4 columns in grid layout 
        self.cols = 4
          
        # declaring the slider and adding some effects to it 
        self.brightnessControl = Slider(min = 0, max = 100) 
           
  
        # 1st row - one label, one slider     
        self.add_widget(Label(text ='brightness')) 
        self.add_widget(self.brightnessControl)  
  
        # 2nd row - one label for caption, 
        # one label for slider value 
        self.add_widget(Label(text ='Slider Value')) 
        self.brightnessValue = Label(text ='0') 
        self.add_widget(self.brightnessValue) 
  
  
        # On the slider object Attach a callback 
        # for the attribute named value 
        self.brightnessControl.bind(value = self.on_value) 
         
    # Adding functionality behind the slider 
    # i.e when pressed increase the value 
    def on_value(self, instance, brightness): 
        self.brightnessValue.text = "% d"% brightness 
  
  
# The app class 
class SliderExample(App): 
    def build(self): 
        widgetContainer = WidgetContainer() 
        return widgetContainer 
   
  
# creating the object root for ButtonApp() class   
root = SliderExample() 
    
# run function runs the whole program  
# i.e run() method which calls the  
# target function passed to the constructor.  
root.run()
