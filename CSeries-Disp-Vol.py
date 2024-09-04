from tricont_cseries_DT_Driver import cseries_DT, cseries_configurator, cseries_Status
from time import sleep, time

# cseries_configurator.write_csv()

Vol2Disp = float(input ("How much to dispense? (mL):  "))

pump_name_1 = 'Tecan' 
pump_name_2 = 'TriCont'



pump_1 = cseries_DT(pump_name_1)
cseries_DT.open_serial(pump_1)
cseries_DT.config_pump(pump_1)

# cseries_DT.send_cmd(pump_1,'V','6000')

pump_2 = cseries_DT(pump_name_2)
cseries_DT.open_serial(pump_2)
cseries_DT.config_pump(pump_2)

print(pump_1.max_steps)
print(pump_2.max_steps)

# cseries_DT.send_cmd(pump_1,'Z','')
# cseries_DT.send_cmd(pump_2,'Z','')

##############################################################
## Testing Ground ##

wait = input('Press Enter to Dispense First Payload (From Tecan)')
Start1= time()
cseries_DT.disp_ml(pump_1, Vol2Disp)
End1= time()
Run1_time = End1-Start1 
print('Dispense 1 Time: ', Run1_time,'(sec)')

wait = input('Press Enter to Dispense Second Payload (From TriCont)')
Start2= time()
cseries_DT.disp_ml(pump_2, Vol2Disp)
End2= time()
Run2_time = End2-Start2
print('Dispense 2 Time: ', Run2_time,'(sec)')

##############################################################
## Always Close port at end of program ##
cseries_DT.close_serial(pump_1)
cseries_DT.close_serial(pump_2)