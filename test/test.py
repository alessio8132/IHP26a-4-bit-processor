# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge

async def reset_cpu(dut):
    """Helper task to safely pulse the reset line."""
    dut.ui_in.value = 0b0000_0000
    dut.rst_n.value = 0
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1

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

    # 2. TEST LDA (Load)
    dut._log.info("Testing LDA: Load 5")
    # Feed instruction immediately after reset
    dut.ui_in.value = 0b0001_0101 # LDA 5 (PC becomes 1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT   (PC becomes 2)
    await FallingEdge(dut.clk)                      
    # PC is 2, OUT is 5. Combined: 0x25
    assert dut.uo_out.value == 0x25, f"LDA Failed: Expected 0x25, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 3. TEST ADD
    dut._log.info("Testing ADD: 5 + 3 = 8")
    dut.ui_in.value = 0b0001_0101 # LDA 5 (PC becomes 1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0010_0011 # ADD 3 (PC becomes 2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT   (PC becomes 3)
    await FallingEdge(dut.clk)
    # PC is 3, OUT is 8. Combined: 0x38
    assert dut.uo_out.value == 0x38, f"ADD Failed: Expected 0x38, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 4. TEST SUB
    dut._log.info("Testing SUB: 7 - 2 = 5")
    dut.ui_in.value = 0b0001_0111 # LDA 7 (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0011_0010 # SUB 2 (PC=2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT   (PC=3)
    await FallingEdge(dut.clk)
    # PC is 3, OUT is 5. Combined: 0x35
    assert dut.uo_out.value == 0x35, f"SUB Failed: Expected 0x35, got {hex(dut.uo_out.value)}"
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
    dut.ui_in.value = 0b0001_0011 # LDA 3 (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0110_0000 # SHL   (PC=2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT   (PC=3)
    await FallingEdge(dut.clk)
    # PC is 3, OUT is 6. Combined: 0x36
    assert dut.uo_out.value == 0x36, f"SHL Failed: Expected 0x36, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 8. TEST XOR
    dut._log.info("Testing XOR: 5 ^ 3 = 6")
    dut.ui_in.value = 0b0001_0101 # LDA 5 (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0111_0011 # XOR 3 (PC=2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT   (PC=3)
    await FallingEdge(dut.clk)
    # PC is 3, OUT is 6. Combined: 0x36
    assert dut.uo_out.value == 0x36, f"XOR Failed: Expected 0x36, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 9. TEST AND
    dut._log.info("Testing AND: 11 & 7 = 3")
    dut.ui_in.value = 0b0001_1011 # LDA 11 (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1011_0111 # AND 7  (PC=2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT    (PC=3)
    await FallingEdge(dut.clk)
    # PC is 3, OUT is 3. Combined: 0x33
    assert dut.uo_out.value == 0x33, f"AND Failed: Expected 0x33, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 10. TEST OR
    dut._log.info("Testing OR: 4 | 2 = 6")
    dut.ui_in.value = 0b0001_0100 # LDA 4 (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1101_0010 # OR 2  (PC=2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT   (PC=3)
    await FallingEdge(dut.clk)
    # PC is 3, OUT is 6. Combined: 0x36
    assert dut.uo_out.value == 0x36, f"OR Failed: Expected 0x36, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 11. TEST OUT (Directly)
    dut._log.info("Testing OUT: Outputting 9 to uo_out")
    dut.ui_in.value = 0b0001_1001 # LDA 9 (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT   (PC=2)
    await FallingEdge(dut.clk)
    # PC is 2, OUT is 9. Combined: 0x29
    assert dut.uo_out.value == 0x29, f"OUT Failed: Expected 0x29, got {hex(dut.uo_out.value)}"
    await reset_cpu(dut)

    # 12. TEST INTERNAL RAM (STORE and LOAD)
    dut._log.info("Testing RAM: Store 7 to addr 3, clear ACC, Load from addr 3")
    dut.ui_in.value = 0b0001_0111 # LDA 7         (PC=1)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0101_0011 # STORE Addr 3  (PC=2)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b0001_0000 # LDA 0         (PC=3)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1010_0011 # LOAD Addr 3   (PC=4)
    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b1000_0000 # OUT           (PC=5)
    await FallingEdge(dut.clk)
    # PC is 5, OUT is 7. Combined: 0x57
    assert dut.uo_out.value == 0x57, f"RAM Test Failed: Expected 0x57, got {hex(dut.uo_out.value)}"
    
    dut._log.info("All CPU tests passed successfully! Tapeout ready.")