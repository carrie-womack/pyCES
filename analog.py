import math
import time
import config

def configure_AI():
    """Opens config file analog parameters"""
    config_data = config.open_config()

    return config_data["analog"]

file_path = "/sys/bus/iio/devices/iio:device0/"

def ReadAI(config_params):
    """Reads analog file on BBB and splits it into a dictionary consisting of each anolg item"""

    i = 0
    AIdict = {}
    AIdict.clear()

    #for each variable in the file, add it to the AIdict dictionary with the appropriate name
    while i < 7:
        
        file_name = f"in_voltage{i}_raw"
        file_path_full = file_path + file_name
        file = open(file_path_full, 'r')
        content = file.readline()

        if i == 0:
            AIdict.update({"Therm0": float(content)}) #labeled Therm2 on schematic
        if i == 1:
            AIdict.update({"Therm1": float(content)}) #labeled LED_Therm on schematic
        if i == 2:
            AIdict.update({"Spare": float(content)}) #labeled Spare_AI on schematic
        if i == 3:
            AIdict.update({"Therm2": float(content)})  #labeled Therm1 on schematic 
        if i == 4:
            AIdict.update({"LED_Curr": float(content)})#labeled LED_Curr on schematic
        if i == 5:
            AIdict.update({"Press": float(content)})#labeled Press on schematic
        if i == 6:
            AIdict.update({"Vin_Volt": float(content)})#labeled Vin_Volt on schematic
        
        i +=1
    
    #Convert AIdict (analog) into ValuesDict (real units) using ConverAI function
    ValuesDict = ConvertAI(AIdict,config_params)
    return ValuesDict

def ConvertAI(AIdict,config_params):
    """Calls an analog to "real units" function for each type of variable"""

    ValuesDict = AIdict

    #cycles through each key in the dictionary to convert each variable into its correct units
    for x in AIdict:
        
        if "Therm" in x:
            #A–D parameters are established in config.yaml
            A = config_params['A']
            B = config_params['B']
            C = config_params['C']
            D = config_params['D']

            Therm = AI_to_Therm(AIdict[x],A,B,C,D)
            ValuesDict[x] = Therm

        if "Press" in x:
            #Slope and offset are established in config.yaml
            Pres_Slope = config_params['Pres_Slope']
            Pres_Offset = config_params['Pres_Offset']

            Press = AI_to_Press(AIdict[x],Pres_Offset,Pres_Slope)
            ValuesDict[x] = Press

        if "Volt" in x:

            Volt = AI_to_Volt(AIdict[x])
            ValuesDict[x] = Volt

        if "Curr" in x:

            Curr = AI_to_Curr(AIdict[x])
            ValuesDict[x] = Curr

    #returns a dictionary that has keys with appropriate names and values in correct units
    # print(ValuesDict)
    return ValuesDict

def AI_to_Therm(AI,A,B,C,D): 
    """Converts analog value to temperature in Celcius"""

    if AI == 0:
        return 0

    else: 

        LR = math.log(1.24*((3601.6/(AI/2.275))-1)*1000)
        int1 = B*LR
        int2 = C*LR*LR*LR
        int3 = D*LR*LR*LR*LR*LR

        Therm = (1/(A + int1 + int2 + int3)) - 273.15

        return round(Therm,2)

def AI_to_Press(AI,Pres_Offset,Pres_Slope):
    """Converts analog value to pressure in mbar"""

    if AI == 0:
        return 0

    else:     

        Press = (AI*2.79787/(1000*2.275))*Pres_Slope + Pres_Offset
        
        return round(Press,2)

def AI_to_Volt(AI):
    """Converts analog value to battery voltage in Volts"""

    if AI == 0:
        return 0

    else: 
        Volt = (AI*0.01117699115/2.275)

        return round(Volt,2)

def AI_to_Curr(AI):
    """Currently a placeholder for converting analog value to current"""
    
    if AI == 0:
        return 0

    else: 
        Curr = AI/2270 #placeholder

        return round(Curr,2)

def makeAuxFileString(analog_string):
    # print(analog_string)
    aux_string = []
    # print(analog_string["Therm0"])
    aux_string.append(analog_string["Therm0"])
    aux_string.append(analog_string["Therm1"])
    aux_string.append(analog_string["Press"])
    aux_string.append(analog_string["LED_Curr"])
    # print(aux_string)   

    return aux_string

def main():

    config_params = configure_AI()
    
    while True:
        try: 
            analog_string = ReadAI(config_params)
            print(analog_string)
            auxfile_string = makeAuxFileString(analog_string)
            print(auxfile_string)
            time.sleep(1)
        except KeyboardInterrupt:
            print("\tClosing pyCES now")
            break


if __name__ == '__main__':
    main()
