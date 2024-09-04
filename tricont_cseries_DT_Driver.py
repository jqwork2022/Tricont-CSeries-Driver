###################################################################################################################################################
#  tricont_cseries_DT_Driver.py - A python based code to connect to and send commands to a Tricontinent cseries Syringe Pump using the Data Terminal Protocol 
#
#  Author: John Quinn
#
#  Created: 6/22/23 
#
#  Last Modified: 7/18/24
#
#  Purpose: Low level command singnaling to the cseries pump and library of commands for use in higher level functionality in Novus Project
#
#  Refrences:
#       Tricontent CSeries User manual - c-series-manual.pdf
#           Contains Use and Programming instructions for Tricontinet C Series Pumps
#           Can be found at: https://www.tricontinent.com/en-us/c-series-syringe-pumps
#           See page 119 for Data Terminal Programming Info 
#
#       pycont Github Repository 
#           https://github.com/croningp/pycont
#           Open-Source Repository that controls Tricontent cseries pumps using python
#           Used as guide for this code
#
###################################################################################################################################################
# Python Package Imports and Syntax Setup 
import serial
import csv

from serial.tools import list_ports
from time import sleep
from pathlib import Path
from itertools import zip_longest

###################################################################################################################################################
# Constants / Common Strings / Dictionaries to be used in code 
# Common Command Strings hjkl;'

start_cmd_str =     '/'
end_cmd_str =       "\r" 
exe_cmd_str =       'R'

# Hexidecmial Identifiers for Tricont Pump
target_vendor_id = 0x10c4
target_product_id = 0xea60

#: Command to execute
CMD_EXECUTE = 'R'
#: Command to initialise with the right valve position as output
CMD_INITIALIZE_VALVE_RIGHT = 'Z'
#: Command to initialise with the left valve position as output
CMD_INITIALIZE_VALVE_LEFT = 'Y'
#: Command to initialise with no valve
CMD_INITIALIZE_NO_VALVE = 'W'
#: Command to initialise with valves only
CMD_INITIALIZE_VALVE_ONLY = 'w'
#: Command to invoke microstep mode
CMD_MICROSTEPMODE = 'N'
#: Command to move the pump to a location
CMD_MOVE_TO = 'A'
#: Command to access a specific pump
CMD_PUMP = 'P'
#: Command to deliver payload
CMD_DELIVER = 'D'
#: Command to achieve top velocity
CMD_TOPVELOCITY = 'V'
#: Command to access the EEPROM configuration
CMD_EEPROM_CONFIG = 'U'      # Requires power restart to take effect
CMD_EEPROM_LOWLEVEL_CONFIG = 'u'      # Requires power restart to take effect
#: Command to terminate current operation
CMD_TERMINATE = 'T'

CMD_Dict = {'CMD_EXECUTE' : 'R', #: Command to execute
"CMD_INITIALIZE_VALVE_RIGHT" : 'Z',#: Command to initialise with the right valve position as output
'CMD_INITIALIZE_VALVE_LEFT' : 'Y',#: Command to initialise with the left valve position as output
'CMD_INITIALIZE_NO_VALVE' : 'W', #: Command to initialise with no valve
'CMD_INITIALIZE_VALVE_ONLY' : 'w',#: Command to initialise with valves only
'CMD_MICROSTEPMODE' : 'N',#: Command to invoke microstep mode
'CMD_MOVE_TO' : 'A',#: Command to move the pump to a location
'CMD_PUMP' : 'P',#: Command to access a specific pump
'CMD_DELIVER' : 'D',#: Command to deliver payload
'CMD_TOPVELOCITY' : 'V',#: Command to achieve top velocity
'CMD_EEPROM_CONFIG' : 'U',#: Command to access the EEPROM configuration ; Requires power restart to take effect
'CMD_EEPROM_LOWLEVEL_CONFIG' : 'u',#: Command to access the EEPROM low level configuration Requires power restart to take effect
'CMD_TERMINATE' : 'T'#: Command to terminate current operation
}

#: Command for the valve init_all_pump_parameters
#: .. note:: Depending on EEPROM settings (U4 or U11) 4-way distribution valves either use IOBE or I<n>O<n>
CMD_VALVE_INPUT = 'I'   # Depending on EEPROM settings (U4 or U11) 4-way distribution valves either use IOBE or I<n>O<n>
#: Command for the valve output
CMD_VALVE_OUTPUT = 'O'
#: Command for the valve bypass
CMD_VALVE_BYPASS = 'B'
#: Command for the extra valve
CMD_VALVE_EXTRA = 'E'

# Valve Position Dictionary 
Valve_Pos = {
    'Inlet' : 'I',
    'Outlet' : 'O',
    'Bypass' : 'B',
    'Extra' : 'E'
}

#: Microstep Mode 0
MICRO_STEP_MODE_0 = 0
#: Microstep Mode 2
MICRO_STEP_MODE_2 = 2

#: Number of steps in Microstep Mode 0
N_STEP_MICRO_STEP_MODE_0 = 3000
#: Number of steps in Microstep Mode 2
N_STEP_MICRO_STEP_MODE_2 = 24000

#: The maximum top velocity for Microstep Mode 0
MAX_TOP_VELOCITY_MICRO_STEP_MODE_0 = 6000
#: The maximum top velocity for Microstep Mode 2
MAX_TOP_VELOCITY_MICRO_STEP_MODE_2 = 48000

#: default Input/Output (I/O) Baudrate
DEFAULT_IO_BAUDRATE = 9600
#: Default timeout for I/O operations
DEFAULT_IO_TIMEOUT = 1

#: Command for the reporting the status
CMD_REPORT_STATUS = 'Q'
#: Command for reporting hte plunger position
CMD_REPORT_PLUNGER_POSITION = '?'
#: Command for reporting the start velocity
CMD_REPORT_START_VELOCITY = '?1'
#: Command for reporting the peak velocity
CMD_REPORT_PEAK_VELOCITY = '?2'
#: Command for reporting the cutoff velocity
CMD_REPORT_CUTOFF_VELOCITY = '?3'
#: Command for reporting the valve position
CMD_REPORT_VALVE_POSITION = '?6'
#: Command for reporting initialisation
CMD_REPORT_INTIALIZED = '?19'
#: Command for reporting the EEPROM
CMD_REPORT_EEPROM = '?27'
#: Command for reporting the status of J2-5 for 3 way-Y valve (i.e. 120 deg rotation)
CMD_REPORT_JUMPER_3WAY = '?28'

# ERROR Free Statuses 
#: Idle status when there are no errors
STATUS_IDLE_ERROR_FREE = '`'
#: Busy status when there are no errors
STATUS_BUSY_ERROR_FREE = '@'

# ERROR STATUSES
#: Idle status for initialization failure
STATUS_IDLE_INIT_FAILURE = 'a'
#: Busy status for initialization failure
STATUS_BUSY_INIT_FAILURE = 'A'
#: Idle status for invalid command
STATUS_IDLE_INVALID_COMMAND = 'b'
#: Busy status for invalid command
STATUS_BUSY_INVALID_COMMAND = 'B'
#: Idle status for invalid operand
STATUS_IDLE_INVALID_OPERAND = 'c'
#: Busy status for invalid operand
STATUS_BUSY_INVALID_OPERAND = 'C'
#: Idle status for EEPROM failure
STATUS_IDLE_EEPROM_FAILURE = 'f'
#: Busy status for EEPROM failure
STATUS_BUSY_EEPROM_FAILURE = 'F'
#: Idle status for pump not initialized
STATUS_IDLE_NOT_INITIALIZED = 'g'
#: Busy status for pump not initialized
STATUS_BUSY_NOT_INITIALIZED = 'G'
#: Idle status for plunger overload error
STATUS_IDLE_PLUNGER_OVERLOAD = 'i'
#: Busy status for plunger overload error
STATUS_BUSY_PLUNGER_OVERLOAD = 'I'
#: Idle status for valve overload error
STATUS_IDLE_VALVE_OVERLOAD = 'j'
#: Busy status for plunger overload error
STATUS_BUSY_VALVE_OVERLOAD = 'J'
#: Idle status for plunger not allowed to move
STATUS_IDLE_PLUNGER_STUCK = 'k'
#: Busy status for plunger not allowed to move
STATUS_BUSY_PLUNGER_STUCK = 'K'

ERROR_STATUSES_IDLE = (STATUS_IDLE_INIT_FAILURE, STATUS_IDLE_INVALID_COMMAND, STATUS_IDLE_INVALID_OPERAND,
                       STATUS_IDLE_EEPROM_FAILURE, STATUS_IDLE_NOT_INITIALIZED, STATUS_IDLE_PLUNGER_OVERLOAD,
                       STATUS_IDLE_VALVE_OVERLOAD, STATUS_IDLE_PLUNGER_STUCK)
ERROR_STATUSES_BUSY = (STATUS_BUSY_INIT_FAILURE, STATUS_BUSY_INVALID_COMMAND, STATUS_BUSY_INVALID_OPERAND,
                       STATUS_BUSY_EEPROM_FAILURE, STATUS_BUSY_NOT_INITIALIZED, STATUS_BUSY_PLUNGER_OVERLOAD,
                       STATUS_BUSY_VALVE_OVERLOAD, STATUS_BUSY_PLUNGER_STUCK)

#consider changing Pump error status bool for some, should only be false for mechnaicla problems, invalid commands should be reported but dont hold latr operation 
# form of dict Key : Value
# Key = status strng vairbale name 
#vlaue is list in format [response string, error message, pump idle or busy, pump status bool(tells system if pump is good to run/for next command)]
STATUS_DICT = {
    'STATUS_IDLE_ERROR_FREE' : ['`','Error Free','Idle',True], #: Idle status when there are no errors
    'STATUS_BUSY_ERROR_FREE' : ['@','Error Free','Busy',True], #: Busy status when there are no errors
    'STATUS_IDLE_INIT_FAILURE' : ['a','Init Failure','Idle', False] , #: Idle status for initialization failure
    'STATUS_BUSY_INIT_FAILURE' : ['A','Busy Init Failure','Busy', False], #: Busy status for initialization failure
    'STATUS_IDLE_INVALID_COMMAND' : ['b','Invalid Command','Idle',False], #: Idle status for invalid command
    'STATUS_BUSY_INVALID_COMMAND' : ['B','Invalid Command','Busy',False], #: Busy status for invalid command
    'STATUS_IDLE_INVALID_OPERAND' : ['c','Invalid Operand','Idle',False], #: Idle status for invalid operand
    'STATUS_BUSY_INVALID_OPERAND' : ['C','Invlaid Operand','Busy',False], #: Busy status for invalid operand
    'STATUS_IDLE_EEPROM_FAILURE' : ['f','EEPROM Failure','Idle',False],  #: Idle status for EEPROM failure
    'STATUS_BUSY_EEPROM_FAILURE' : ['F','EEPROM Failure','Busy',False],   #: Busy status for EEPROM failure
    'STATUS_IDLE_NOT_INITIALIZED' : ['g','Pump not Initalized','Idle',False], #: Idle status for pump not initialized
    'STATUS_BUSY_NOT_INITIALIZED' : ['G','Pump not Initialized','Busy',False], #: Busy status for pump not initialized
    'STATUS_IDLE_PLUNGER_OVERLOAD' : ['i','Plunger Overload','Idle',False],  #: Idle status for plunger overload error
    'STATUS_BUSY_PLUNGER_OVERLOAD' : ['I','Plunger Overload','Busy',False], #: Busy status for plunger overload error
    'STATUS_IDLE_VALVE_OVERLOAD' : ['j','Valve Overload','Idle',False],  #: Idle status for valve overload error
    'STATUS_BUSY_VALVE_OVERLOAD' : ['J','Valve Overload','Busy',False],  #: Busy status for plunger overload error
    'STATUS_IDLE_PLUNGER_STUCK' : ['k','Pluger Stuck','Idle',False],#: Idle status for plunger not allowed to move
    'STATUS_BUSY_PLUNGER_STUCK' : ['K','Plunger Stuck','Busy',False]#: Busy status for plunger not allowed to move
    }


###################################################################################################################################################
###################################################################################################################################################

# Classs Definitions 

class cseries_configurator(object):
    """Class for Setting up configuration files for this driver
    """
    def __init__() -> None:
        pass

    #Defaults for many values enteted in args line here; can be modified at use with Keyword Arg; defaults based on mode 0 power-up defaults
    def write_csv(baudrate = 9600, timeout = 1, acc_slope_code = 14, start_velo = 900, 
                  top_velo = 5600, cutoff_velo = 900, cutoff_incre = 0) :
        csv_top = ['Pump Name', 'Syringe Volume','Increment Mode', "Stepping Mode",
                   'Accleration/Decleration Slope Code', 'Start Velocity', 'Top Velocity',
                     'Cutoff Velocity', 'Cutoff Increments',  'Pump Address', 
                     'Pump Port', 'Baud Rate', 'Timeout']
        p = Path(__file__).with_name('cseries_config.csv')
        with p.open('w') as file:
            # Create a CSV writer object
            writer = csv.writer(file)
            writer.writerow(csv_top)
            num_pumps = int(input ('How many Pumps are being configured: '))
            for _ in range(num_pumps): 
                pump_name = input('Enter a Name for Pump: ')
                syringe_vol = input('Enter Volume of Syringe in Pump (in mL): ')
                pump_addy = input('Enter the adress which the Pump is using: ')
                incre_mode = input('''Enter Increment Mode for pump \n 
                                \n Default is Mode 0
                                \n(0 = Standard Increments ; 1 = MicroStep Increments):''') 
                pump_max_steps = input("How many steps is a standard full stroke for this pump (1 for 3000 or 2 for 24000):")
                # Get a list of available ports
                ports = list(serial.tools.list_ports.comports())
                # Iterate through each port and check if the device matches the target IDs
                for port in ports:
                    if port.vid == target_vendor_id and port.pid == target_product_id:
                        try:
                            ser = serial.Serial(port.device)
                            ser.close()
                            used_port = port.device
                            print("Serial connection found on port:", port.device)
                        except (OSError, serial.SerialException):
                            pass  # Move on to the next port
                    else:
                        print('No Tricont C-Series Pumps found')

                new_row = [pump_name, syringe_vol,incre_mode, pump_max_steps, acc_slope_code, start_velo, top_velo, 
                        cutoff_velo, cutoff_incre,  pump_addy, used_port, baudrate, timeout]
                
                writer.writerow(new_row)
        
# Create Driver Class for cseries Command Driver 
class cseries_DT(object):
    """Class for intefacing with and commanding a Trincontinent cseries Syringe Pump 

        """ 
    def __init__(self, pump_name:str):
        p = Path(__file__).with_name('cseries_config.csv')
        with p.open('r') as file:
            reader=csv.reader(file)
            found_pump = False
            for row in reader:
                if row[0] == pump_name:
                    self.syringe_volume = int(row[1])
                    self.incre_mode = row[2]
                    self.pump_max_steps = row[3]
                    self.acc_slope = row[4]
                    self.start_velo = row[5]
                    self.top_velo = row[6]
                    self.cutoff_velo = row[7]
                    self.cutoff_incre = row[8]
                    self.pump_address = row[9]
                    self.pump_port = row[10]
                    self.baudrate = int(row[11])
                    self.timeout = int(row[12])
                    self.connection = serial.Serial(timeout = self.timeout)
                    self.connection.port = self.pump_port
                    found_pump = True
                    print('Pump found, config data loaded')
                    break
            if not found_pump:
                print('Error Pump Config info not found')

    def open_serial(self):
        self.connection.open()
        print('Opening connection on port'+str(self.pump_port))
       
    def close_serial(self):
        """Closes the connection again."""
        self.connection.close()
        print("Closing connection on port " + str(self.pump_port))

    def config_pump(self):
        ''' Configures Pump with information from configuration file '''
        cseries_DT.send_cmd(self, 'N', self.incre_mode)
        if self.incre_mode == '0':
            if  self.pump_max_steps == "1":
                self.max_steps = 3000
            elif self.pump_max_steps == "2":
                self.max_steps = 24000
            else: 
                print('Configuration Error , Max Steps Invalid')
                
        elif self.incre_mode == '1':
            if self.pump_max_steps == "1":
                self.max_steps = 24000
            elif self.pump_max_steps == "2":
                self.max_steps = 196000
            else: 
                print('Configuration Error , Max Steps Invalid')
                
        else:
            print('Configuration Error , Increment Mode Invalid')
            exit()
            
        cseries_DT.wait4idle(self, self.pump_address)
        

        cseries_DT.send_cmd(self, 'L', self.acc_slope)
        cseries_DT.wait4idle(self, self.pump_address)

        cseries_DT.send_cmd(self, 'v', self.start_velo)
        cseries_DT.wait4idle(self, self.pump_address)

        cseries_DT.send_cmd(self, 'V', self.top_velo)
        cseries_DT.wait4idle(self, self.pump_address)

        cseries_DT.send_cmd(self, 'c', self.cutoff_velo)
        cseries_DT.wait4idle(self, self.pump_address)     

        cseries_DT.send_cmd(self, 'C', self.cutoff_incre)
        cseries_DT.wait4idle(self, self.pump_address)    

    def send_cmd(self, command, operand):
        self.command = command
        if operand is not None:
            cmd2send = start_cmd_str + self.pump_address + self.command + operand + exe_cmd_str + end_cmd_str
            self.operand = operand 
        else:
            operand = None
            cmd2send = start_cmd_str + self.pump_address + self.command + exe_cmd_str + end_cmd_str
            #MAKE IF STATMENT FOR EXE COMAND VS STATUS COMMAND!
            
        self.cmd2send = cmd2send.encode()
        self.string2send = cmd2send
        
        self.connection.write(self.cmd2send)
        self.read_text_bytes = self.connection.readline()
    
        self.read_text_str = self.read_text_bytes.decode()

    def send_cmd_multi(self, commands=list, operands=list):
        self.commands = commands
        self.operands  = operands
        combined = [x + y for x, y in zip_longest(self.commands, self.operands, fillvalue="")]
        combined_str = ''.join(combined)
        cmd2send = start_cmd_str + self.pump_address + combined_str + exe_cmd_str + end_cmd_str
        #MAKE IF STATMENT FOR EXE COMAND VS STATUS COMMAND!
            
        self.cmd2send = cmd2send.encode()
        self.string2send = cmd2send
        
        self.connection.write(self.cmd2send)
        self.read_text_bytes = self.connection.readline()
    
        self.read_text_str = self.read_text_bytes.decode()
    
    def wait4idle(self, address):
        """Waits until the pump is ready. Code snippet by Alon."""
        out_data = "/" + str(address) + "QR\r"
        while True:
            sleep(0.05)
            self.connection.write(out_data.encode())
            self.connection.flushInput()  # added to flush buffer from nonsense
            back = self.connection.readline()
            if 96 in back:  # 64 is @ (busy) and 48 is 0 (idle) 96 is ' which is also good
                return True

    def switch_valve(self,destination_valve=str,verbose=False):
        """ Checks to see if pump is already at destination valve, then if it is not 
            Switches to the desired valve position as set by destination valve.
            Prints message and passes if valve is already at destination."""
        
        cseries_DT.wait4idle(self,self.pump_address)
        cseries_DT.send_cmd(self,'?','6')
       
        status_temp = cseries_Status(self.read_text_bytes)
       # cseries_Status.parse(status_temp)
        cseries_DT.wait4idle(self,self.pump_address)
        
        # Debugging Prints
        if verbose == True:
            print('\nSwitch Valve Debug Info')
            print('  Response Bytes: ', self.read_text_bytes)
            print('  Device Status Data: ' + status_temp.data)
            print('  Device Status Data (Uppercase): ' + status_temp.data.upper())
            print('  Key of destination_valve: '+ destination_valve)
            print('  Value of destination_valve: '+ Valve_Pos[destination_valve])

        if status_temp.data.upper() == Valve_Pos[destination_valve]:
            print('\nValve is already at destination valve '+ destination_valve + '! No change made by switch_valve')
        else:
            for key,value in Valve_Pos.items():
                if key == destination_valve:
                    self.send_cmd(value,None)
                    print('\nValve moved to Destination: '+ key)
                    break

    def move2pos_abs_ml(self,abs_ml,verbose=False):
        """ Collectes needed info / variables , 
            then calculates step position
            then perpares string to send
            then sends string using .send_cmd
        Calculates steps from mL in the process."""
        steps = int((self.max_steps/ int(self.syringe_volume)) * abs_ml)
        if steps in range(self.max_steps + 1):
            cseries_DT.send_cmd(self,'A',str(steps))
            if verbose == True: 
                print('Moving to Increment '+ str(steps))
        else:
            print("Request Position is Outside Possible Range")
            pass  # todo: error handling

    def disp_ml(self,ml2disp = float):
        total_strokes = int(ml2disp / int(self.syringe_volume))
        partial_stroke = ml2disp % float(self.syringe_volume)
        partial_vol = partial_stroke * float(self.syringe_volume)

        #Empty Current Syringe
        self.switch_valve('Inlet')
        self.wait4idle(self.pump_address)
        self.move2pos_abs_ml(0)
        self.wait4idle(self.pump_address)
        
        for i in range(total_strokes): 
            #Aspirate Needed Volume
            self.switch_valve('Inlet')
            self.wait4idle(self.pump_address)
            self.move2pos_abs_ml(self.syringe_volume)
            self.wait4idle(self.pump_address)
            #Switch back to Outlet Valve
            self.switch_valve('Outlet')
            self.wait4idle(self.pump_address)
            #Dispense to Outlet 
            self.move2pos_abs_ml(0)
            self.wait4idle(self.pump_address)

        # Dispense Partial Stroke
        #Aspirate Needed Volume
        self.switch_valve('Inlet')
        self.wait4idle(self.pump_address)
        self.move2pos_abs_ml(partial_vol)
        self.wait4idle(self.pump_address)
        #Switch back to Outlet Valve
        self.switch_valve('Outlet')
        self.wait4idle(self.pump_address)
        #Dispense to Outlet 
        self.move2pos_abs_ml(0)
        self.wait4idle(self.pump_address)

        print("Finished Dispensing "+str(ml2disp)+"ml to Outlet")

class cseries_Status(object):
    """ This class is used to represent a cseries pump status, the response of the device from a command.

        Args:
            response: The response from the device

        (for more details see http://www.tricontinent.com/products/cseries-syringe-pumps)
        """

    def __init__(self, response: bytes):
        try:
            self.response = response.decode()
        except UnicodeDecodeError:
            self.response = None  # type: ignore

        if self.response is not None:
            info = self.response.rstrip().rstrip('\x03').lstrip(start_cmd_str)
            self.address = info[0]
            self.status = info[1]
            self.data = info[2:]
        
    def parse(self):
        for key,value in STATUS_DICT.items():
            if value[0] == self.status:
                self.stats_info_key= key
                self.status_code = value[0]
                self.status_message= value[1]
                self.status_BusyOrIdle= value[2]
                self.status_bool = value[3]
                break
            else:
                self.status_message = 'ERROR STATUS CODE NOT RECOGNIZED'