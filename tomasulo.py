class Simulator():
    
    def __init__(self, filename, startingAddress = 0, MEM = {}):  # if no starting address is given, assume it's 0
        self.filename = filename
        self.startingAddress = startingAddress
        
        
        
        # dictionary to store the value corresponding to each register 
        # (all initialized to zero)
        self.REGS = {"R0": 0, "R1": 0, "R2": 0, "R3": 0, "R4": 0, \
                     "R5": 0, "R6": 0, "R7": 0}
            
        # RESERVATION STATIONS
        # DEFAULT NUMBER OF STATIONS
        self.LD_RS_count = 2
        self.ST_RS_count = 2
        self.JMP_RS_count = 2
        self.BEQ_RS_count = 2
        self.ADD_RS_count = 3
        self.NAND_RS_count = 2
        self.MUL_RS_count = 2
        
        #DICTIONARY FOR EACH INSTRUCTION CLASS
        self.LD_RS = {}
        self.ST_RS = {} 
        self.JMP_RS = {}
        self.BEQ_RS = {}
        self.ADD_RS = {}
        self.NAND_RS = {}
        self.MUL_RS = {}
        
        # CREATING A RESERVATION STATION AT EVERY KEY
        for i in range(self.LD_RS_count):
            self.LD_RS[i+1] = []
        
        for i in range(self.ST_RS_count):
            self.ST_RS[i+1] = []
        
        for i in range(self.JMP_RS_count):
            self.JMP_RS[i+1] = []
        
        for i in range(self.BEQ_RS_count):
            self.BEQ_RS[i+1] = []
            
        for i in range(self.ADD_RS_count):
            self.ADD_RS[i+1] = []
        
        for i in range(self.NAND_RS_count):
            self.NAND_RS[i+1] = []
            
        for i in range(self.MUL_RS_count):
            self.MUL_RS[i+1] = []
        
        
        # REORDER BUFFER
        self.ROB = {} 
        self.ROB_ENTRIES = 8
            
        # DEFAULT EXECUTION TIMES (could be changed by user)
        self.LD_cycles = 2
        self.ST_cycles = 2
        self.JMP_cycles = 1
        self.BEQ_cycles = 1
        self.ADD_cycles = 2
        self.NAND_cycles = 1
        self.MUL_cycles = 10
        
        # stores how many cycles each instruction takes to comlete execution (for convenience)
        self.cycles = {"LOAD": self.LD_cycles, "STORE": self.ST_cycles, \
                       "JMP": self.JMP_cycles, "JAL": self.JMP_cycles, \
                       "RET": self.JMP_cycles, "BEQ": self.BEQ_cycles, \
                       "ADD": self.ADD_cycles, "SUB": self.ADD_cycles, \
                       "ADDI": self.ADD_cycles, "NAND": self.NAND_cycles, \
                       "MUL": self.MUL_cycles}
          
            
        #for each destination register, all of the cycles where it's busy
        self.dest_regs = {"R0": [], "R1": [], "R2": [], "R3": [], "R4": [], \
                          "R5": [], "R6": [], "R7": []} 
        
        self.writes = [] # list of cycles where writes happened 
                         # (to prevent multiple writes in the same cycle)
                         
        self.mem_writes = [] # list of cycles where writes TO MEMORY happened
                             # (to prevent multiple writes to memory in the same cycle)
        self.issues = [-1] # list of cycles where issues happend
        
        self.MEMORY = MEM # dictionary to store memory addresses as keys and data as values
        
        
        # DICTIONARIES TO STORE SIGNIFICANT CYCLES FOR EACH INSTRUCTION
        self.issue_cycle = {} # store the issue cycle for each instruction (key is the PC)
        self.exec_start = {}
        self.exec_end = {}
        self.write_cycle = {}
        self.commit_cycle = {}
        
        # VARIABLE THAT WILL REPRESENT CURRENT CYCLE AS PROGRAM PROGRESSES
        self.tmp = -1
        
        self.program_sequence = []
        
        
        
    # FUNCTION THAT ALLOWS USER TO CUSTOMIZE THE HARDWARE OF THE PROCESSOR
    def editHardware(self):
        print("\nEnter number of available reservation stations for: ")
        self.LD_RS_count = int(input("LOAD: "))
        self.ST_RS_count = int(input("STORE: "))
        self.JMP_RS_count = int(input("JMP/JAL/RET: "))
        self.BEQ_RS_count = int(input("BEQ: "))
        self.ADD_RS_count = int(input("ADD/ADDI/SUB: "))
        self.NAND_RS_count = int(input("NAND: "))
        self.MUL_RS_count = int(input("MUL: "))
    
        for i in range(self.LD_RS_count):
            self.LD_RS[i+1] = []
        
        for i in range(self.ST_RS_count):
            self.ST_RS[i+1] = []
        
        for i in range(self.JMP_RS_count):
            self.JMP_RS[i+1] = []
        
        for i in range(self.BEQ_RS_count):
            self.BEQ_RS[i+1] = []
            
        for i in range(self.ADD_RS_count):
            self.ADD_RS[i+1] = []
        
        for i in range(self.NAND_RS_count):
            self.NAND_RS[i+1] = []
            
        for i in range(self.MUL_RS_count):
            self.MUL_RS[i+1] = []
            
            
        print("\nEnter number of cycles needed (to complete execution) for: ")
        self.LD_cycles = int(input("LOAD: "))
        self.ST_cycles = int(input("STORE: "))
        self.JMP_cycles = int(input("JMP/JAL/RET: "))
        self.BEQ_cycles = int(input("BEQ: "))
        self.ADD_cycles = int(input("ADD/ADDI/SUB: "))
        self.NAND_cycles = int(input("NAND: "))
        self.MUL_cycles = int(input("MUL: "))
        
        # stores how many cycles each instruction takes to comlete execution (for convenience)
        self.cycles = {"LOAD": self.LD_cycles, "STORE": self.ST_cycles, \
                       "JMP": self.JMP_cycles, "JAL": self.JMP_cycles, \
                       "RET": self.JMP_cycles, "BEQ": self.BEQ_cycles, \
                       "ADD": self.ADD_cycles, "SUB": self.ADD_cycles, \
                       "ADDI": self.ADD_cycles, "NAND": self.NAND_cycles, \
                       "MUL": self.MUL_cycles}
            
        self.ROB_ENTRIES = int(input("\nEnter number of ROB entries: "))
            
            

    # function to convert input program to list of instructions
    def getInstrList(self):
        try:
            in_file = open(self.filename, 'r')
        except IOError:
            print("Failed to open", self.filename)
            return
            
        self.tmp = in_file.read()
        instr_initial = self.tmp.split("\n") # initial list, might contain empty lines
        instr = [] # final list with no empty lines
        
        for i in range(len(instr_initial)): # remove empty lines
            if instr_initial[i] == '':
                continue
            else:
                instr.append(instr_initial[i]) # copy to final list
                
        in_file.close()
        
        return instr # returns list of instructions (no empty lines)
    
    
    # function to convert list of instructions to dictionary with the key being 
    # the PC and data being the corresponding instruction
    def getInstrDict(self):
        instrList = self.getInstrList()
        instrDict = {}
        key = self.startingAddress # first key is the provided starting address
        
        for i in instrList:
            instruction = ""
            for j in i:
                if j != " ":
                    instruction += j # will eventually store the operation (e.g. ADDI)
                else:
                    new_str = i[len(instruction)+1:len(i)] # store rest of 
                                                           # instruction in new_str
                    break
            
            if(instruction != "RET"):
                registers = new_str.split(", ") 
                instrDict[key] = [instruction] 
                for reg in registers:
                    instrDict[key].append(reg)
            else:
                instrDict[key] = [instruction] 
                
                
            # instrDict will eventually have the form: 
            # {"PC": [OP, rd, rs1, rs2], ...} depending on instruction format
            
            key += 1 # increment PC by 1 each instruction (16-bit Word-Addressable)
        
        return instrDict # returns dictionary with key being the PC at each instruction
    
    '''
     FUNCTION THAT ENCAPSULATES THE LOGIC OF ISSUING AN INSTRUCTION
     THIS FUNCTION IS COMMON BETWEEN ALL INSTRUCTION CLASSES
    '''
    def issueInstruction(self, PC, reservation_station, RS_count, current_cycle):
        label = False
        while(True):
            if len(self.ROB) == self.ROB_ENTRIES + 1 and label == False: # if the ROB is full
                max_list = [] # list to store the commit cycle of each ROB entry
                for r in self.ROB: # for each key in the ROB
                    if r != PC: # if the key is not equal to the current PC
                        max_list.append(max(self.ROB[r])) # append the largest 
                                                          # cycle (commit cycle) to the max_list
                
                if current_cycle <= min(max_list): # if the current cycle is less than or equal to the minimum commit cycle
                    current_cycle += 1 # increment cycle and try again
                    continue
                else: # if the current cycle is greater than the minimum commit cycle (can replace it in ROB)
                    for r in list(self.ROB): 
                        if self.ROB[r] != [] and max(self.ROB[r]) == min(max_list): # find entry where commit cycle is the minimum
                            self.ROB.pop(r) # delete it from ROB
                            self.issue_cycle[PC] = current_cycle # set issue cycle to current cycle
                            label = True # mark label == True to avoid entering ROB logic again for current instruction
                            break
                    
            res_station = 1
            break_label = False
            while (res_station <= RS_count):
                if current_cycle not in reservation_station[res_station]: # if the reservation station is not busy at current cycle
                    
                    while current_cycle <= max(self.issues):
                        current_cycle += 1
                        
                    self.issue_cycle[PC] = current_cycle # We are issuing in current cycle
                    reservation_station[res_station].append(self.issue_cycle[PC]) # mark reservation station as busy at current cycle
                    self.ROB[PC].append(self.issue_cycle[PC])
                    current_cycle += 1 # increment cycle
                    break_label = True
                    break 
                
                res_station += 1
                
            if (break_label == True):
                break_label = False
                break
            current_cycle += 1 # if current reservation station is busy, increment cycle and try again
                                
        label = False
        self.issues.append(self.issue_cycle[PC])
        self.tmp = current_cycle
        
        return res_station # return the res_station number for use in the main function
    
    
    '''
     FUNCTION TO PERFORM THE ALGORITHM
    '''
    def performTomasulo(self):
        instrDict = self.getInstrDict() # generate the instruction dictionary
        
        '''
        i: instruction number (e.g. i1,i2,etc..)
        instrDict[i]: list of instruction components(e.g. ['ADDI', 'R2', 'R0', '#3'])
        instrDict[i][0]: operation (e.g. ADDI)
        instrDict[i][1]: rd (destination register) (if not jmp, jal or ret) (different usage if store or beq)
        instrDict[i][2]: rs1 (src register 1)(could also be of the form N(Register) w/ load or store)
        instrDict[i][3]: rs2 (src register 2) (if not imm) 
        '''
        instrCount = len(instrDict) # number of instructions in input programs
        i = self.startingAddress # set i to the provided starting address
        mispredictions = 0
        BEQ_count = 0
        cnt = 0
        
        current_cycle = 0 # initialize current cycle to zero (first issue happens at zero)
        while (i < (instrCount + self.startingAddress)): 
            # i IS THE PROGRAM COUNTER
            
            OP = instrDict[i][0] # current operation
            self.ROB[i] = []
            
            
            if (1 <= len(instrDict[i]) <= 2): # if JMP or JAL or RET
                
                #HANDLING JMP/JAL/RET
                #2 RESERVATION STATIONS AVAILABLE
                self.tmp = current_cycle
                if OP != "RET":
                    # FORMAT: JMP imm/JAL imm
                    imm = int(instrDict[i][1])
                    
                '''
                ISSUING
                '''
                
                res_station = self.issueInstruction(i, self.JMP_RS, self.JMP_RS_count, self.tmp)
                current_cycle = self.issue_cycle[i]
                
                            
                '''
                EXEC START
                '''
                # execution will never be delayed because there are no src registers
                self.exec_start[i] = self.tmp # mark current cycle as start of execution
                self.ROB[i].append(self.tmp)
                self.JMP_RS[res_station].append(self.tmp)
                    
                    
                '''
                EXEC END
                '''
                for c in range(self.exec_start[i], self.exec_start[i] + self.cycles[OP]): # for the N cycles it takes to execute
                    self.tmp += 1 # increment current cycle each time
                    self.ROB[i].append(self.tmp)
                    self.JMP_RS[res_station].append(self.tmp)
                self.exec_end[i] = self.tmp # after loop completes, current cycle will be when execution ends
                
                
                '''    
                WRITE BACK
                '''
                while (True):
                    self.tmp += 1 # increment current cycle
                    if(self.tmp in self.writes): # if another instruction previously wrote back in the same cycle
                        self.JMP_RS[res_station].append(self.tmp)
                        self.ROB[i].append(self.tmp)
                        
                    else: # if no previous instruction wrote back in the current cycle
                        self.JMP_RS[res_station].append(self.tmp)
                        self.ROB[i].append(self.tmp)    
                        self.writes.append(self.tmp)  # append current cycle to list of writes to prevent multiple writes to the same register
                        self.write_cycle[i] = self.tmp # mark current cycle as the write cycle
                        current_cycle += 1 # increment the current cycle (this time it's not self.tmp, allows next issue 
                                           # to be 1 cycle after last issue)
                        break
                
                
                '''
                COMMIT
                '''
                self.tmp += 1 
                
                #finding the previous instruction's commit cycle
                largest_ROB = 0 # var to store the commit cycle of prev instruction
                for r in self.ROB:
                    for s in self.ROB[r]:
                        if s > largest_ROB:
                            largest_ROB = s 
                
              
                if self.tmp > largest_ROB: # if current cycle > commit cycle of prev instruction
                    self.commit_cycle[i] = self.tmp # set commit cycle to current cycle
                else:
                    self.commit_cycle[i] = largest_ROB + 1 # else it needs to be 1 cycle bigger than prev commit
                
                self.ROB[i].append(self.commit_cycle[i]) # append commit cycle to ROB
                
                
                
                if OP == "JAL":
                    self.REGS["R1"] = i + 1
                    
                    
                # NEW i (PC) IS COMPUTED AT THE VERY END OF THE FUNCTION 
                
            
                
            
            elif len(instrDict[i]) == 3: #if ST or LD
            
                #HANDLING STORE
                #2 RESERVATION STATIONS AVAILABLE
                if OP == "STORE":
                    self.tmp = current_cycle
                    # FORMAT: STORE rs2, imm(rs1)
                    rs2 = instrDict[i][1]
                    imm = ""
                    cnt = 0
                    for c in instrDict[i][2]:
                        if c == '(':
                            rs1 = instrDict[i][2][cnt + 1: -1]
                            break
                        imm += c
                        cnt += 1
                        
                    imm = int(imm)
                    
                    '''
                    ISSUING
                    '''
                    res_station = self.issueInstruction(i, self.ST_RS, self.ST_RS_count, self.tmp)
                    current_cycle = self.issue_cycle[i]
                    
                    
                    '''
                    EXEC START
                    '''
                    if rs1 in self.dest_regs: # if rs1 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs1]: # if rs1 was previously marked busy as a destination register in the current cycle
                                self.ROB[i].append(self.tmp)
                                self.ST_RS[res_station].append(self.tmp)
                                    
                                self.tmp += 1 # increment current cycle and try again
                                
                            else: # if rs1 was not previously marked busy at the current cycle
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.ROB[i].append(self.tmp)
                                self.ST_RS[res_station].append(self.tmp)
                                break
                            
                    if rs2 in self.dest_regs: # if rs2 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs2]: # if rs2 was previously marked busy as a destination register in the current cycle
                                self.ROB[i].append(self.tmp)
                                self.ST_RS[res_station].append(self.tmp)
                                    
                                self.tmp += 1 # increment current cycle and try again
                            
                            else: # if rs2 was not previously marked busy at the current cycle
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.ROB[i].append(self.tmp)
                                self.ST_RS[res_station].append(self.tmp)
                                break
                            
                    if rs1 not in self.dest_regs and rs2 not in self.dest_regs: # if rs1 and rs2 were never destination registers before
                        self.exec_start[i] = self.tmp # mark current cycle as start of execution
                        self.ROB[i].append(self.tmp)
                        self.ST_RS[res_station].append(self.tmp)
                            
                            
                    '''
                    EXEC END
                    '''
                    for c in range(self.exec_start[i], self.exec_start[i] + self.cycles[OP]): # for the N cycles it takes to execute
                        self.tmp += 1 # increment current cycle each time
                        self.ROB[i].append(self.tmp)
                        self.ST_RS[res_station].append(self.tmp)
                    self.exec_end[i] = self.tmp # after loop completes, current cycle will be when execution ends
                    self.tmp += 1 # extra cycle for address computation     
                    self.ST_RS[res_station].append(self.tmp)
                    self.ROB[i].append(self.tmp)
                
                    
                    '''    
                    WRITE BACK
                    '''
                    while (True):
                        self.tmp += 1 # increment current cycle
                        # IT IS FINE TO WRITEBACK IN THE SAME CYCLE AS ANOTHER NON-MEMORY INSTRUCTION
                        if(self.tmp in self.mem_writes): # if another instruction previously wrote back TO MEMORY in the same cycle
                            self.ST_RS[res_station].append(self.tmp)
                            self.ROB[i].append(self.tmp)
                            
                        else: # if no previous instruction wrote back in the current cycle
                            self.ST_RS[res_station].append(self.tmp)
                            self.ROB[i].append(self.tmp)
                            self.mem_writes.append(self.tmp)  # append current cycle to list of writes TO MEMORY to prevent multiple writes to memory in the same cycle
                            self.write_cycle[i] = self.tmp # mark current cycle as the write cycle
                            current_cycle += 1 # increment the current cycle (this time it's not self.tmp, allows next issue 
                                               # to be 1 cycle after last issue)
                            break
                        
                    '''
                    COMMIT
                    '''
                    self.tmp += 1 
                    
                    #finding the previous instruction's commit cycle
                    largest_ROB = 0 # var to store the commit cycle of prev instruction
                    for r in self.ROB:
                        for s in self.ROB[r]:
                            if s > largest_ROB:
                                largest_ROB = s 
                    
                  
                    if self.tmp > largest_ROB: # if current cycle > commit cycle of prev instruction
                        self.commit_cycle[i] = self.tmp # set commit cycle to current cycle
                    else:
                        self.commit_cycle[i] = largest_ROB + 1 # else it needs to be 1 cycle bigger than prev commit
                    
                    self.ROB[i].append(self.commit_cycle[i]) # append commit cycle to ROB
                    
                    
                    # set data at proper location to contents of rs2
                    self.MEMORY[imm + self.REGS[rs1]] = self.REGS[rs2] 
                    

                #HANDLING LOAD
                #2 RESERVATION STATIONS AVAILABLE
                if OP == "LOAD":
                    self.tmp = current_cycle
                    # FORMAT: LOAD rd, imm(rs1)
                    rd = instrDict[i][1]
                    imm = ""
                    cnt = 0
                    for c in instrDict[i][2]:
                        if c == '(':
                            rs1 = instrDict[i][2][cnt + 1: -1]
                            break
                        imm += c
                        cnt += 1
                        
                    imm = int(imm)
                    
                    '''
                    ISSUING
                    '''
                    res_station = self.issueInstruction(i, self.LD_RS, self.LD_RS_count, self.tmp)
                    current_cycle = self.issue_cycle[i]
                    
                    
                    '''
                    EXEC START
                    '''
                    if rs1 in self.dest_regs: # if rs1 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs1]: # if rs1 was previously marked busy as a destination register in the current cycle
                                self.dest_regs[rd].append(self.tmp)   # mark rd for the current instruction as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.LD_RS[res_station].append(self.tmp)
                                    
                                self.tmp += 1 # increment current cycle and try again
                                
                            else: # if rs1 was not previously marked busy at the current cycle
                                
                                self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.LD_RS[res_station].append(self.tmp)
                                
                                self.tmp += 1 # extra cycle for address computation
                                
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.LD_RS[res_station].append(self.tmp)
                                    
                                break
                            
                    if rs1 not in self.dest_regs:    
                        self.exec_start[i] = self.tmp # mark current cycle as start of execution
                        self.dest_regs[rd].append(self.tmp)
                        self.ROB[i].append(self.tmp)
                        self.LD_RS[res_station].append(self.tmp)
                    
                    '''
                    EXEC END
                    '''
                    for c in range(self.exec_start[i], self.exec_start[i] + self.cycles[OP]): # for the N cycles it takes to execute
                        self.tmp += 1 # increment current cycle each time
                        self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                        self.ROB[i].append(self.tmp)
                        self.LD_RS[res_station].append(self.tmp)
                    
                        
                    self.exec_end[i] = self.tmp 
                    

                    '''    
                    WRITE BACK
                    '''
                    while (True):
                        self.tmp += 1 # increment current cycle
                        if(self.tmp in self.writes): # if another instruction previously wrote back in the same cycle
                            self.LD_RS[res_station].append(self.tmp)
                            self.dest_regs[rd].append(self.tmp) # mark rd as still busy 
                            self.ROB[i].append(self.tmp)
                            
                        else: # if no previous instruction wrote back in the current cycle
                            self.LD_RS[res_station].append(self.tmp)
                            self.ROB[i].append(self.tmp)
                            self.writes.append(self.tmp)  # append current cycle to list of writes to prevent multiple writes to the same register
                            self.write_cycle[i] = self.tmp # mark current cycle as the write cycle
                            current_cycle += 1 # increment the current cycle (this time it's not self.tmp, allows next issue 
                                               # to be 1 cycle after last issue)
                                               
                            # ADD MORE CODE HERE IF YOU WANNA MAKE ISSUING AFTER WB NOT CONCURRENT
                            break
                        
                        
                        
                    '''
                    COMMIT
                    '''
                    self.tmp += 1 
                    
                    #finding the previous instruction's commit cycle
                    largest_ROB = 0 # var to store the commit cycle of prev instruction
                    for r in self.ROB:
                        for s in self.ROB[r]:
                            if s > largest_ROB:
                                largest_ROB = s 
                    
                  
                    if self.tmp > largest_ROB: # if current cycle > commit cycle of prev instruction
                        self.commit_cycle[i] = self.tmp # set commit cycle to current cycle
                    else:
                        self.commit_cycle[i] = largest_ROB + 1 # else it needs to be 1 cycle bigger than prev commit
                    
                    self.ROB[i].append(self.commit_cycle[i]) # append commit cycle to ROB
                                
                    
                                
                    
                    if (imm + self.REGS[rs1]) in self.MEMORY: # if there is data at this location 
                        self.REGS[rd] = self.MEMORY[imm + self.REGS[rs1]] # set rd to this data
                    
                    
                    
                        
            
            
            
            
            
            elif len(instrDict[i]) == 4: #if not LD, ST, JMP, JAL, RET
                    
                # HANDLING BEQ
                # 2 RESERVATION STATIONS AVAILABLE
                if OP == "BEQ":
                    # FORMAT: BEQ rs1, rs2, imm
                    self.tmp = current_cycle # store value of current cycle (sequential issue) in self.tmp
                    rs1 = instrDict[i][1]
                    rs2 = instrDict[i][2]
                    imm = int(instrDict[i][3].replace('#',''))
                    BEQ_count += 1
                    
                    '''
                    ISSUING
                    '''
                    res_station = self.issueInstruction(i, self.BEQ_RS, self.BEQ_RS_count, self.tmp)
                    current_cycle = self.issue_cycle[i]
                    
                    
                    '''
                    EXEC START
                    '''
                    if rs1 in self.dest_regs: # if rs1 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs1]: # if rs1 was previously marked busy as a destination register in the current cycle
                                self.ROB[i].append(self.tmp)
                                self.BEQ_RS[res_station].append(self.tmp)
                                    
                                self.tmp += 1 # increment current cycle and try again
                                
                            else: # if rs1 was not previously marked busy at the current cycle
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.ROB[i].append(self.tmp)
                                self.BEQ_RS[res_station].append(self.tmp)
                                break
                            
                    if rs2 in self.dest_regs: # if rs2 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs2]: # if rs2 was previously marked busy as a destination register in the current cycle
                                self.ROB[i].append(self.tmp)
                                self.BEQ_RS[res_station].append(self.tmp)
                                    
                                self.tmp += 1 # increment current cycle and try again
                            
                            else: # if rs2 was not previously marked busy at the current cycle
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.ROB[i].append(self.tmp)
                                self.BEQ_RS[res_station].append(self.tmp)
                                break
                            
                    if rs1 not in self.dest_regs and rs2 not in self.dest_regs: # if rs1 and rs2 were never destination registers before
                        self.exec_start[i] = self.tmp # mark current cycle as start of execution
                        self.ROB[i].append(self.tmp)
                        self.BEQ_RS[res_station].append(self.tmp)
                            
                
                            
                    '''
                    EXEC END
                    '''
                    for c in range(self.exec_start[i], self.exec_start[i] + self.cycles[OP]): # for the N cycles it takes to execute
                        self.tmp += 1 # increment current cycle each time
                        self.ROB[i].append(self.tmp)
                        self.BEQ_RS[res_station].append(self.tmp)
                    self.exec_end[i] = self.tmp # after loop completes, current cycle will be when execution ends
                        
                    
                    '''    
                    WRITE BACK
                    '''
                    while (True):
                        self.tmp += 1 # increment current cycle
                        if(self.tmp in self.writes): # if another instruction previously wrote back in the same cycle
                            self.BEQ_RS[res_station].append(self.tmp)
                            self.ROB[i].append(self.tmp)
                            
                        else: # if no previous instruction wrote back in the current cycle
                            self.BEQ_RS[res_station].append(self.tmp)
                            self.ROB[i].append(self.tmp)
                            self.write_cycle[i] = self.tmp # mark current cycle as the write cycle
                            current_cycle += 1 # increment the current cycle (this time it's not self.tmp, allows next issue 
                                               # to be 1 cycle after last issue)
                            break
                        
                        
                    '''
                    COMMIT (ASK ABOUT OFFSET AND BRANCH MISPREDICTION)
                    '''
                    self.tmp += 1 
                    
                    #finding the previous instruction's commit cycle
                    largest_ROB = 0 # var to store the commit cycle of prev instruction
                    for r in self.ROB:
                        for s in self.ROB[r]:
                            if s > largest_ROB:
                                largest_ROB = s 
                    
                  
                    if self.tmp > largest_ROB: # if current cycle > commit cycle of prev instruction
                        self.commit_cycle[i] = self.tmp # set commit cycle to current cycle
                    else:
                        self.commit_cycle[i] = largest_ROB + 1 # else it needs to be 1 cycle bigger than prev commit
                    
                    self.ROB[i].append(self.commit_cycle[i]) # append commit cycle to ROB
                    
                    
                    
                # HANDLING ADD/SUB/ADDI
                # 3 RESERVATION STATIONS AVAILABLE
                elif OP in ["ADD", "ADDI", "SUB"] :
                    self.tmp = current_cycle # store value of current cycle (sequential issue) in self.tmp
                    rd = instrDict[i][1]
                    rs1 = instrDict[i][2]
                    
                    if OP == "ADDI":
                        imm = int(instrDict[i][3].replace('#',''))
                    else:
                        rs2 = instrDict[i][3]
                    
                    
                    '''
                    ISSUING
                    '''
                    res_station = self.issueInstruction(i, self.ADD_RS, self.ADD_RS_count, self.tmp)
                    current_cycle = self.issue_cycle[i]
                    
                    
                    '''
                    EXEC START
                    '''
                    if rs1 in self.dest_regs: # if rs1 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs1]: # if rs1 was previously marked busy as a destination register in the current cycle
                                self.dest_regs[rd].append(self.tmp)   # mark rd for the current instruction as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.ADD_RS[res_station].append(self.tmp)
                                self.tmp += 1 # increment current cycle and try again
                                
                            else: # if rs1 was not previously marked busy at the current cycle
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.ADD_RS[res_station].append(self.tmp)
                                break
                            
                    if OP != "ADDI":
                        if rs2 in self.dest_regs: # if rs2 is one of the destination registers from previous instructions
                            while(True):
                                if self.tmp in self.dest_regs[rs2]: # if rs2 was previously marked busy as a destination register in the current cycle
                                    self.dest_regs[rd].append(self.tmp)   # mark rd for the current instruction as busy at current cycle
                                    self.ROB[i].append(self.tmp)
                                    self.ADD_RS[res_station].append(self.tmp)
                                    self.tmp += 1 # increment current cycle and try again
                                
                                else: # if rs2 was not previously marked busy at the current cycle
                                    self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                    self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                                    self.ROB[i].append(self.tmp)
                                    self.ADD_RS[res_station].append(self.tmp)
                                    break
                            
                    if OP != "ADDI":
                        if rs1 not in self.dest_regs and rs2 not in self.dest_regs: # if rs1 and rs2 were never destination registers before
                            self.exec_start[i] = self.tmp # mark current cycle as start of execution
                            self.dest_regs[rd].append(self.tmp)
                            self.ROB[i].append(self.tmp)
                            self.ADD_RS[res_station].append(self.tmp)
                    if OP == "ADDI":
                        if rs1 not in self.dest_regs:    
                            self.exec_start[i] = self.tmp # mark current cycle as start of execution
                            self.dest_regs[rd].append(self.tmp)
                            self.ROB[i].append(self.tmp)
                            self.ADD_RS[res_station].append(self.tmp)
                            
                    '''
                    EXEC END
                    '''
                    for c in range(self.exec_start[i], self.exec_start[i] + self.cycles[OP]): # for the N cycles it takes to execute
                        self.tmp += 1 # increment current cycle each time
                        self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                        self.ROB[i].append(self.tmp)
                        self.ADD_RS[res_station].append(self.tmp)  
                    self.exec_end[i] = self.tmp # after loop completes, current cycle will be when execution ends
                        
                            
                            
                    '''    
                    WRITE BACK
                    '''
                    while (True):
                        self.tmp += 1 # increment current cycle
                        if(self.tmp in self.writes): # if another instruction previously wrote back in the same cycle
                            self.ADD_RS[res_station].append(self.tmp)
                            self.dest_regs[rd].append(self.tmp) # mark rd as still busy 
                            self.ROB[i].append(self.tmp)
                            
                        else: # if no previous instruction wrote back in the current cycle
                            self.ADD_RS[res_station].append(self.tmp)
                            self.ROB[i].append(self.tmp)
                            self.writes.append(self.tmp)  # append current cycle to list of writes to prevent multiple writes to the same register
                            self.write_cycle[i] = self.tmp # mark current cycle as the write cycle
                            current_cycle += 1 # increment the current cycle (this time it's not self.tmp, allows next issue 
                                               # to be 1 cycle after last issue)
                            break
                        
                    '''
                    COMMIT
                    '''
                    self.tmp += 1 
                    
                    #finding the previous instruction's commit cycle
                    largest_ROB = 0 # var to store the commit cycle of prev instruction
                    for r in self.ROB:
                        for s in self.ROB[r]:
                            if s > largest_ROB:
                                largest_ROB = s 
                    
                  
                    if self.tmp > largest_ROB: # if current cycle > commit cycle of prev instruction
                        self.commit_cycle[i] = self.tmp # set commit cycle to current cycle
                    else:
                        self.commit_cycle[i] = largest_ROB + 1 # else it needs to be 1 cycle bigger than prev commit
                    
                    self.ROB[i].append(self.commit_cycle[i]) # append commit cycle to ROB
                                    
                    
                                
                    if OP == "ADDI":
                        self.REGS[rd] = self.REGS[rs1] + imm # perform the operation and store the value in rd (not sure yet if it's useful)
                    elif OP == "ADD":
                        self.REGS[rd] = self.REGS[rs1] + self.REGS[rs2]
                    elif OP == "SUB":
                        self.REGS[rd] = self.REGS[rs1] - self.REGS[rs2]
                        
                        
            
                # HANDLING NAND
                # 2 RESERVATION STATIONS AVAILABLE
                elif OP == "NAND":
                    self.tmp = current_cycle # store value of current cycle (sequential issue) in self.tmp
                    rd = instrDict[i][1]
                    rs1 = instrDict[i][2]
                    rs2 = instrDict[i][3]
                    
                    '''
                    ISSUING
                    '''
                    res_station = self.issueInstruction(i, self.NAND_RS, self.NAND_RS_count, self.tmp)
                    current_cycle = self.issue_cycle[i]
                    
                    '''
                    EXEC START
                    '''
                    if rs1 in self.dest_regs: # if rs1 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs1]: # if rs1 was previously marked busy as a destination register in the current cycle
                                self.dest_regs[rd].append(self.tmp)   # mark rd for the current instruction as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.NAND_RS[res_station].append(self.tmp)
                                    
                                self.tmp += 1 # increment current cycle and try again
                                
                            else: # if rs1 was not previously marked busy at the current cycle
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.NAND_RS[res_station].append(self.tmp)
                                break
                            
                    if rs2 in self.dest_regs: # if rs2 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs2]: # if rs2 was previously marked busy as a destination register in the current cycle
                                self.dest_regs[rd].append(self.tmp)   # mark rd for the current instruction as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.NAND_RS[res_station].append(self.tmp)
                                    
                                self.tmp += 1 # increment current cycle and try again
                            
                            else: # if rs2 was not previously marked busy at the current cycle
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.NAND_RS[res_station].append(self.tmp)
                                break
                            
                    if rs1 not in self.dest_regs and rs2 not in self.dest_regs: # if rs1 and rs2 were never destination registers before
                        self.exec_start[i] = self.tmp # mark current cycle as start of execution
                        self.dest_regs[rd].append(self.tmp)
                        self.ROB[i].append(self.tmp)
                        self.NAND_RS[res_station].append(self.tmp)
                            
                
                            
                    '''
                    EXEC END
                    '''
                    for c in range(self.exec_start[i], self.exec_start[i] + self.cycles[OP]): # for the N cycles it takes to execute
                        self.tmp += 1 # increment current cycle each time
                        self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                        self.ROB[i].append(self.tmp)
                        self.NAND_RS[res_station].append(self.tmp)
                    self.exec_end[i] = self.tmp # after loop completes, current cycle will be when execution ends
                        
                            
                            
                    '''    
                    WRITE BACK
                    '''
                    while (True):
                        self.tmp += 1 # increment current cycle
                        if(self.tmp in self.writes): # if another instruction previously wrote back in the same cycle
                            self.NAND_RS[res_station].append(self.tmp)
                            
                            self.dest_regs[rd].append(self.tmp) # mark rd as still busy 
                            self.ROB[i].append(self.tmp)
                            
                        else: # if no previous instruction wrote back in the current cycle
                            self.NAND_RS[res_station].append(self.tmp)    
                            self.ROB[i].append(self.tmp)
                            self.writes.append(self.tmp)  # append current cycle to list of writes to prevent multiple writes to the same register
                            self.write_cycle[i] = self.tmp # mark current cycle as the write cycle
                            current_cycle += 1 # increment the current cycle (this time it's not self.tmp, allows next issue 
                                               # to be 1 cycle after last issue)
                            break
                        
                    '''
                    COMMIT
                    '''
                    self.tmp += 1 
                    
                    #finding the previous instruction's commit cycle
                    largest_ROB = 0 # var to store the commit cycle of prev instruction
                    for r in self.ROB:
                        for s in self.ROB[r]:
                            if s > largest_ROB:
                                largest_ROB = s 
                    
                  
                    if self.tmp > largest_ROB: # if current cycle > commit cycle of prev instruction
                        self.commit_cycle[i] = self.tmp # set commit cycle to current cycle
                    else:
                        self.commit_cycle[i] = largest_ROB + 1 # else it needs to be 1 cycle bigger than prev commit
                    
                    self.ROB[i].append(self.commit_cycle[i]) # append commit cycle to ROB
                                
                    
                                
                
                    self.REGS[rd] = 1 if not(self.REGS[rs1] and self.REGS[rs2]) else 0
                    
                    
            
            
            
                ##### HANDLING MUL ######
                # 2 RESERVATION STATIONS AVAILABLE
                elif OP == "MUL":
                    self.tmp = current_cycle # store value of current cycle (sequential issue) in self.tmp
                    rd = instrDict[i][1]
                    rs1 = instrDict[i][2]
                    rs2 = instrDict[i][3]
                    
                    '''
                    ISSUING
                    '''
                    res_station = self.issueInstruction(i, self.MUL_RS, self.MUL_RS_count, self.tmp)
                    current_cycle = self.issue_cycle[i]

                    '''
                    EXEC START
                    '''
                    if rs1 in self.dest_regs: # if rs1 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs1]: # if rs1 was previously marked busy as a destination register in the current cycle
                                self.dest_regs[rd].append(self.tmp)   # mark rd for the current instruction as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.MUL_RS[res_station].append(self.tmp)
                                    
                                self.tmp += 1 # increment current cycle and try again
                                
                            else: # if rs1 was not previously marked busy at the current cycle
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.MUL_RS[res_station].append(self.tmp)
                                break
                            
                    if rs2 in self.dest_regs: # if rs2 is one of the destination registers from previous instructions
                        while(True):
                            if self.tmp in self.dest_regs[rs2]: # if rs2 was previously marked busy as a destination register in the current cycle
                                self.dest_regs[rd].append(self.tmp)   # mark rd for the current instruction as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.MUL_RS[res_station].append(self.tmp)
                                    
                                self.tmp += 1 # increment current cycle and try again
                            
                            else: # if rs2 was not previously marked busy at the current cycle
                                self.exec_start[i] = self.tmp # mark current cycle as the start of execution
                                self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                                self.ROB[i].append(self.tmp)
                                self.MUL_RS[res_station].append(self.tmp)
                                break
                            
                    if rs1 not in self.dest_regs and rs2 not in self.dest_regs: # if rs1 and rs2 were never destination registers before
                        self.exec_start[i] = self.tmp # mark current cycle as start of execution
                        self.dest_regs[rd].append(self.tmp)
                        self.ROB[i].append(self.tmp)
                        self.MUL_RS[res_station].append(self.tmp)
                            
                
                            
                    '''
                    EXEC END
                    '''
                    for c in range(self.exec_start[i], self.exec_start[i] + self.cycles[OP]): # for the N cycles it takes to execute
                        self.tmp += 1 # increment current cycle each time
                        self.dest_regs[rd].append(self.tmp) # mark current rd as busy at current cycle
                        self.ROB[i].append(self.tmp)
                        self.MUL_RS[res_station].append(self.tmp)
                    self.exec_end[i] = self.tmp # after loop completes, current cycle will be when execution ends
                        
                            
                        
                            
                    '''    
                    WRITE BACK
                    '''
                    while (True):
                        self.tmp += 1 # increment current cycle
                        if(self.tmp in self.writes): # if another instruction previously wrote back in the same cycle
                            self.MUL_RS[res_station].append(self.tmp)
                            self.dest_regs[rd].append(self.tmp) # mark rd as still busy 
                            self.ROB[i].append(self.tmp)
                            
                        else: # if no previous instruction wrote back in the current cycle
                            self.ROB[i].append(self.tmp)
                            self.MUL_RS[res_station].append(self.tmp)
                            self.writes.append(self.tmp)  # append current cycle to list of writes to prevent multiple writes to the same register
                            self.write_cycle[i] = self.tmp # mark current cycle as the write cycle
                            current_cycle += 1 # increment the current cycle (this time it's not self.tmp, allows next issue 
                                               # to be 1 cycle after last issue)
                            break
                        
                        
                        
                    '''
                    COMMIT
                    '''
                    self.tmp += 1 
                    
                    #finding the previous instruction's commit cycle
                    largest_ROB = 0 # var to store the commit cycle of prev instruction
                    for r in self.ROB:
                        for s in self.ROB[r]:
                            if s > largest_ROB:
                                largest_ROB = s 
                    
                  
                    if self.tmp > largest_ROB: # if current cycle > commit cycle of prev instruction
                        self.commit_cycle[i] = self.tmp # set commit cycle to current cycle
                    else:
                        self.commit_cycle[i] = largest_ROB + 1 # else it needs to be 1 cycle bigger than prev commit
                    

                        
                    self.ROB[i].append(self.commit_cycle[i]) # append commit cycle to ROB
                                
                    
                       
                
                    self.REGS[rd] = self.REGS[rs1] * self.REGS[rs2] 
                  
                    
            
            if(i == self.startingAddress): # if this is the first iteration
                strInstr = self.getInstrList()
                self.tmp = self.commit_cycle[i]
                print("\nStarting address:", self.startingAddress)
                if (len(self.MEMORY) > 0):
                    print("\nInitial memory:", self.MEMORY)
                print("\nINSTRUCTION","\t\t\t\tISSUE","EXEC START", "EXEC END", "WRITE BACK", " COMMIT", sep = "\t"*2)
            
            
            total_time = self.commit_cycle[i]
            cnt += 1
            relative_spacing = 16 - len(strInstr[i - self.startingAddress])
            print(strInstr[i - self.startingAddress] + " "*relative_spacing,self.issue_cycle[i], self.exec_start[i], self.exec_end[i], self.write_cycle[i], self.commit_cycle[i], sep = "\t\t\t\t")


            if (OP == "JMP" or OP == "JAL"):
                i = i + 1 + imm
            elif (OP == "RET"):
                i = self.REGS["R1"]
            elif (OP == "BEQ"):
                if self.REGS[rs1] == self.REGS[rs2]:
                    if(imm >= 0):
                        mispredictions += 1 # if the imm is not negative but the branch happens,
                                            # then the branch was assumed to not be taken, which is a misprediction
                    i = i + 1 + imm
                    continue
                else:
                    if(imm < 0):
                        mispredictions += 1 # if the immediate is negative and the branch was not taken,
                                            # then it's a misprediction
                    i += 1
            else:
                i += 1
                
            if (i == instrCount + self.startingAddress): # if this is the last iteration
                print("\nTotal execution time:", total_time, "cycles")
                if(BEQ_count != 0):
                    print("\nBranch misprediction percentage: ", "{:.2f}".format((mispredictions/BEQ_count)*100), "%", sep = "")
                else:
                    print("\nNo branches in program")
                print("\nIPC: ", "{:.2f}".format(cnt/total_time), sep = "") # NOT SURE THIS IS CORRECT
                print("\nRegister values:", self.REGS)
                if(len(self.MEMORY) > 0):
                    print("\nFinal memory:", self.MEMORY)
        
        
        
        
       
        
       
        
       

while(True):
    startingAddress = input("Enter the starting address of the program (integer): ")
    if(startingAddress.isnumeric() and int(startingAddress) >= 0):
        startingAddress = int(startingAddress)
        break
    else:
        print("Invalid input, try again")
        
MEMORY = {}
while(True):
    n = input("Enter 1 to add data to memory or anything else to continue: ")
    if (n.isnumeric() and int(n) == 1):
        while(True):
            address = input("Enter memory address (integer): ")
            if(address.isnumeric()):
                address = int(address)
            else:
                print("Invalid input, try again")
                continue
            data = input("Enter data (integer): ")
            if(data.isnumeric()):
                data = int(data)
                break
            else:
                print("Invalid input, try again")
                continue
        MEMORY[address] = data
    else:
        break

simulator = Simulator("program.txt", startingAddress, MEMORY)
n = input("Enter 1 to customize the hardware or anything else to use the default version: ")
if(n.isnumeric() and int(n) == 1):
    simulator.editHardware()
        

simulator.performTomasulo()
    