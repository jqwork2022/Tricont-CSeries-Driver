from tricont_cseries_DT_Driver import cseries_DT


prime = cseries_DT('Test1')

cseries_DT.open_serial(prime)

cseries_DT.send_cmd(prime,'Z',None)

cseries_DT.wait4idle(prime, prime.pump_address)

# cseries_DT.send_cmd(prime,'V','6000')

cseries_DT.wait4idle(prime, prime.pump_address)

multi_commands = ['g','I','A','O','A','G']
multi_operands = ['','','3000','','0','25']

cseries_DT.send_cmd_multi(prime, multi_commands,multi_operands)

cseries_DT.wait4idle(prime, prime.pump_address)

cseries_DT.close_serial(prime)

# prime2 = cseries_DT('Test2')

# cseries_DT.open_serial(prime2)

# cseries_DT.send_cmd(prime2,'Z',None)

# cseries_DT.wait4idle(prime2, prime2.pump_address)

# cseries_DT.send_cmd(prime2,'V','6000')

# cseries_DT.wait4idle(prime2, prime2.pump_address)

# cseries_DT.send_cmd_multi(prime2, multi_commands,multi_operands)

# cseries_DT.wait4idle(prime2, prime2.pump_address)

# cseries_DT.close_serial(prime2)

