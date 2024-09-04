from tricont_cseries_DT_Driver import cseries_DT, cseries_configurator, cseries_Status
from time import sleep

# cseries_configurator.write_csv()

string = input('Enter a Valid command string: ')
pump_name_1 = 'Test2' # input('Enter name of pump to command (defualt is Test): ') or 'Test'
# pump_name_2 = 'Test2'

print('\r')

cmd = string[0]
op = string[1:]

print('\rInital Inputs')
print('\r  Pump Name: ' + pump_name_1)
# print('\r  Pump Name: ' + pump_name_2)

print('\r  cmd: ' + cmd)
print('\r  op: ' + op,'\n')

pump_1 = cseries_DT(pump_name_1)
cseries_DT.open_serial(pump_1)
cseries_DT.config_pump(pump_1)
cseries_DT.send_cmd(pump_1,cmd,op)
print(pump_1.max_steps)
# cseries_DT.send_cmd(pump_1,'V','6000')
# pump_2 = cseries_DT(pump_name_2)
# cseries_DT.open_serial(pump_2)
# cseries_DT.config_pump(pump_2)
# cseries_DT.send_cmd(pump_2,cmd,op)


# print('Info Sent to Syringe Pump #1')
# print('\rString of command to cseries: ' + pump_1.string2send)
# print('\rDevice Adress Sent: ' + str(pump_1.pump_address))
# print('\rCommand Sent: ' + str(pump_1.command))
# print('\rOperand Sent: ' + str(pump_1.operand),'\n')

# # print('\rcseries is on Port: ' + pump_1.pump_port,'\n')

# print('Response from Pump')
# print('\rResponse from Pump (bytes): ', pump_1.read_text_bytes)
# print('\rDecoded Response from Pump (coded string): ' + pump_1.read_text_str)

# print('Info Sent to Syringe Pump #2')
# print('\rString of command to cseries: ' + pump_2.string2send)
# print('\rDevice Adress Sent: ' + str(pump_2.pump_address))
# print('\rCommand Sent: ' + str(pump_2.command))
# print('\rOperand Sent: ' + str(pump_2.operand),'\n')

# print('\rcseries is on Port: ' + pump_2.pump_port,'\n')

# print('Response from Pump')
# print('\rResponse from Pump (bytes): ', pump_2.read_text_bytes)
# print('\rDecoded Response from Pump (coded string): ' + pump_2.read_text_str)



# status_instance = cseries_Status(pump_1.read_text_bytes)
# cseries_Status.parse(status_instance)

# print('Pump Response from inputed command')
# print('Status Address (0 Means sent to Pi/Controller): ' + status_instance.address)
# print('Device Status Code: ' + status_instance.status)
# print('Device Status Code Message: '+ status_instance.status_message)
# print('Device Busy/Idle: '+ status_instance.status_BusyOrIdle)
# print('Deivce is Error Free: '+ str(status_instance.status_bool))
# print('Device Status Data: ' + status_instance.data)
# print('\r')

# cseries_DT.wait4idle(pump_1,pump_1.pump_address)
# cseries_DT.wait4idle(pump_2,pump_2.pump_address)

##############################################################
## Testing Ground ##

cseries_DT.disp_ml(pump_1,.5)
#cseries_DT.disp_ml(pump_2,2.745)
# cseries_DT.move2pos_abs_ml(pump_1,1)
# status = cseries_Status(pump_1.read_text_bytes)
# print(status.address)
##############################################################
## Always Close port at end of program ##
cseries_DT.close_serial(pump_1)
# cseries_DT.close_serial(pump_2)