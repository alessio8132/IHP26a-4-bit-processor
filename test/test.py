import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ClockCycles

async def reset_cpu(dut):
    """Helper task to safely pulse the reset line."""
    dut.ui_in.value = 0b0000_0000
    dut.rst_n.value = 0
    # Hold reset for 2 full clock cycles to guarantee the chip sees it
    await ClockCycles(dut.clk, 2) 
    dut.rst_n.value = 1
    # Wait for the next falling edge before feeding the first instruction
    await FallingEdge(dut.clk)

@cocotb.test()
async def test_all_opcodes(dut):
    """Test all instructions of the 4-bit CPU."""
    
    # 1. INITIAL SETUP
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    
    await reset_cpu(dut)

    # 2. TEST LDA (Load) & OUT
    dut._log.info("Testing LDA & OUT: Load 5")
    dut.ui_in.value = 0b0001_0101 # LDA 5 (PC becomes 1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT   (PC becomes 2)
    await FallingEdge(dut.clk)                      
    # PC is 2, OUT is 5. Combined: 0x25
    assert dut.uo_out.value == 0x25, f"LDA Failed: Expected 0x25, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 3. TEST ADD (Memory-based)
    dut._log.info("Testing ADD (Memory): 5 + 3 = 8")
    dut.ui_in.value = 0b0001_0011 # LDA 3          (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0101_0000 # STORE Addr 0   (PC=2, RAM[0]=3)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0001_0101 # LDA 5          (PC=3)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0010_0000 # ADD Addr 0     (PC=4, ACC=5+3=8)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT            (PC=5)
    await FallingEdge(dut.clk)
    # PC is 5, OUT is 8. Combined: 0x58
    assert dut.uo_out.value == 0x58, f"ADD Failed: Expected 0x58, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 4. TEST SUB (Memory-based)
    dut._log.info("Testing SUB (Memory): 7 - 2 = 5")
    dut.ui_in.value = 0b0001_0010 # LDA 2          (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0101_0001 # STORE Addr 1   (PC=2, RAM[1]=2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0001_0111 # LDA 7          (PC=3)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0011_0001 # SUB Addr 1     (PC=4, ACC=7-2=5)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT            (PC=5)
    await FallingEdge(dut.clk)
    # PC is 5, OUT is 5. Combined: 0x55
    assert dut.uo_out.value == 0x55, f"SUB Failed: Expected 0x55, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 5. TEST JZ (Jump if Zero)
    dut._log.info("Testing JZ: ACC is 0 after reset, so should jump to PC 9")
    dut.ui_in.value = 0b0100_1001 # JZ 9 (PC jumps to 9)
    await FallingEdge(dut.clk)
    # Out_reg is 0 from reset. PC is 9. Combined: 0x90
    assert dut.uo_out.value == 0x90, f"JZ Failed: Expected 0x90, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 6. TEST JMP (Unconditional Jump)
    dut._log.info("Testing JMP: Jump to PC 12")
    dut.ui_in.value = 0b1100_1100 # JMP 12 (PC jumps to 12 / 0xC)
    await FallingEdge(dut.clk)
    # Out_reg is 0. PC is 12 (0xC). Combined: 0xC0
    assert dut.uo_out.value == 0xC0, f"JMP Failed: Expected 0xC0, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 7. TEST SHL (Shift Left)
    dut._log.info("Testing SHL: 3 << 1 = 6")
    dut.ui_in.value = 0b0001_0011 # LDA 3          (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0110_0000 # SHL            (PC=2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT            (PC=3)
    await FallingEdge(dut.clk)
    # PC is 3, OUT is 6. Combined: 0x36
    assert dut.uo_out.value == 0x36, f"SHL Failed: Expected 0x36, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 8. TEST XOR (Memory-based)
    dut._log.info("Testing XOR (Memory): 5 ^ 3 = 6")
    dut.ui_in.value = 0b0001_0011 # LDA 3          (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0101_0010 # STORE Addr 2   (PC=2, RAM[2]=3)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0001_0101 # LDA 5          (PC=3)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0111_0010 # XOR Addr 2     (PC=4, ACC=5^3=6)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT            (PC=5)
    await FallingEdge(dut.clk)
    assert dut.uo_out.value == 0x56, f"XOR Failed: Expected 0x56, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 9. TEST AND (Memory-based)
    dut._log.info("Testing AND (Memory): 11 & 7 = 3")
    dut.ui_in.value = 0b0001_0111 # LDA 7          (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0101_0011 # STORE Addr 3   (PC=2, RAM[3]=7)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0001_1011 # LDA 11 (0xB)   (PC=3)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1011_0011 # AND Addr 3     (PC=4, ACC=11&7=3)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT            (PC=5)
    await FallingEdge(dut.clk)
    assert dut.uo_out.value == 0x53, f"AND Failed: Expected 0x53, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 10. TEST OR (Memory-based)
    dut._log.info("Testing OR (Memory): 4 | 2 = 6")
    dut.ui_in.value = 0b0001_0010 # LDA 2          (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0101_0100 # STORE Addr 4   (PC=2, RAM[4]=2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0001_0100 # LDA 4          (PC=3)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1101_0100 # OR Addr 4      (PC=4, ACC=4|2=6)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT            (PC=5)
    await FallingEdge(dut.clk)
    assert dut.uo_out.value == 0x56, f"OR Failed: Expected 0x56, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 11. FIBONACCI ROM FREE-RUN TEST
    dut._log.info("--- Starting Fibonacci Auto-Run ---")
    await reset_cpu(dut)
    
    # We define our ROM as a Python list!
    rom = [
        0b0001_0000, # 0: LDA 0
        0b0101_0000, # 1: STORE 0 (x = 0)
        0b0001_0001, # 2: LDA 1
        0b0101_0001, # 3: STORE 1 (y = 1)
        0b1010_0000, # 4: LOAD 0  (ACC = x)
        0b1000_0000, # 5: OUT
        0b0010_0001, # 6: ADD 1   (ACC = x + y)
        0b0101_0010, # 7: STORE 2 (temp = x + y)
        0b1010_0001, # 8: LOAD 1  (ACC = y)
        0b0101_0000, # 9: STORE 0 (x = y)
        0b1010_0010, # 10: LOAD 2 (ACC = temp)
        0b0101_0001, # 11: STORE 1 (y = temp)
        0b1100_0100, # 12: JMP 4  (Loop back to output)
        0b1111_0000, # 13: HALT
        0b1111_0000, # 14: HALT
        0b1111_0000  # 15: HALT
    ]
    
    # Expected Fibonacci sequence in 4-bit space
    expected_fib = [0, 1, 1, 2, 3, 5, 8]
    fib_index = 0

    # Let it run for 40 cycles, acting as the Arduino feeding the instructions
    for _ in range(40):
        # 1. Read the PC from the top 4 bits of uo_out
        current_pc = int(dut.uo_out.value) >> 4 
        
        # 2. Feed the instruction from our Python ROM array
        dut.ui_in.value = rom[current_pc]
        
        # 3. Wait for the clock to fall (execution)
        await FallingEdge(dut.clk)
        
        # 4. If the instruction we just executed was OUT, log and verify it
        if (rom[current_pc] >> 4) == 0b1000:
            current_out = int(dut.uo_out.value) & 0x0F # Bottom 4 bits
            dut._log.info(f"Fibonacci output: {current_out}")
            
            if fib_index < len(expected_fib):
                assert current_out == expected_fib[fib_index], f"Fibonacci Failed at index {fib_index}: Expected {expected_fib[fib_index]}, got {current_out}"
                fib_index += 1

    dut._log.info("All CPU tests, including Fibonacci, passed successfully! Tapeout ready.")