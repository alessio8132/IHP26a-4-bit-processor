// Personal test bench for personalized tests of the verilog.
`timescale 1ns/1ps

module tb();
    // 1. Create signals to connect to your chip
    reg clk;
    reg rst_n;
    reg [7:0] ui_in;
    wire [7:0] uo_out;

    // 2. Instantiate your chip (The "Unit Under Test")
    tt_um_alessio8132 uut (
        .clk(clk),
        .rst_n(rst_n),
        .ui_in(ui_in),
        .uo_out(uo_out),
        .ena(1'b1),
        .uio_in(8'b0),
        .uio_oe (),
        .uio_out ()
        // ... connect other pins as 0 or unused
    );

    // 3. Create the Clock (flips every 10 time units)
    always #10 clk = ~clk;

    // 4. The Test Sequence
    // Helper task to pulse the reset line
    task reset_cpu;
        begin
            ui_in = 8'b0000_0000; // Clear input to avoid unintended instructions
            rst_n = 1'b0; // Pull reset low
            @(negedge clk);
            rst_n = 1'b1; // Release reset
        end
    endtask

    integer j; // Loop counter for dumping RAM contents
    initial begin
        $dumpfile("sim.vcd"); // Generate a VCD file for waveform viewing
        $dumpvars(0, tb);    // Dump all variables in the testbench
        for (j = 0; j < 16; j = j + 1) begin
            $dumpvars(0, uut.ram[j]); 
        end
        // 1. INITIAL SETUP
        clk = 0;
        ui_in = 8'b00000000;
        reset_cpu();

        // 2. TEST LDA (Load)
        $display("Testing LDA: Load 5");
        @(negedge clk) ui_in = 8'b0001_0101; // LDA 5
        @(negedge clk);                      // Wait for execution

        reset_cpu();

        // 3. TEST ADD
        $display("Testing ADD: 5 + 3 = 8");
        @(negedge clk) ui_in = 8'b0001_0101; // LDA 5
        @(negedge clk) ui_in = 8'b0010_0011; // ADD 3
        @(negedge clk);

        reset_cpu();

        // 4. TEST SUB
        $display("Testing SUB: 7 - 2 = 5");
        @(negedge clk) ui_in = 8'b0001_0111; // LDA 7
        @(negedge clk) ui_in = 8'b0011_0010; // SUB 2
        @(negedge clk);

        reset_cpu();

        // 5. TEST JZ (Jump if Zero)
        $display("Testing JZ: ACC is 0 after reset, so should jump to PC 9");
        // We don't load anything, ACC is 0 from reset
        @(negedge clk) ui_in = 8'b0100_1001; // JZ 9
        @(negedge clk);

        reset_cpu();

        // 6. TEST JMP (Unconditional Jump)
        $display("Testing JMP: Jump to PC 12");
        @(negedge clk) ui_in = 8'b1100_1100; // JMP 12 (4'b1100)
        @(negedge clk);

        reset_cpu();

        // 7. TEST SHL (Shift Left)
        $display("Testing SHL: 3 << 1 = 6");
        @(negedge clk) ui_in = 8'b0001_0011; // LDA 3
        @(negedge clk) ui_in = 8'b0110_0000; // SHL (bottom bits ignored)
        @(negedge clk);

        reset_cpu();

        // 8. TEST XOR
        $display("Testing XOR: 5 (0101) ^ 3 (0011) = 6 (0110)");
        @(negedge clk) ui_in = 8'b0001_0101; // LDA 5
        @(negedge clk) ui_in = 8'b0111_0011; // XOR 3
        @(negedge clk);

        reset_cpu();

        // 9. TEST AND
        $display("Testing AND: 11 (1011) & 7 (0111) = 3 (0011)");
        @(negedge clk) ui_in = 8'b0001_1011; // LDA 11
        @(negedge clk) ui_in = 8'b1011_0111; // AND 7
        @(negedge clk);

        reset_cpu();

        // 10. TEST OR
        $display("Testing OR: 4 (0100) | 2 (0010) = 6 (0110)");
        @(negedge clk) ui_in = 8'b0001_0100; // LDA 4
        @(negedge clk) ui_in = 8'b1101_0010; // OR 2
        @(negedge clk);
        
        reset_cpu();

        // 11. TEST OUT
        $display("Testing OUT: Outputting 9 to output_register");
        @(negedge clk) ui_in = 8'b0001_1001; // LDA 9
        @(negedge clk) ui_in = 8'b1000_0000; // OUT (bottom bits ignored)
        @(negedge clk);
        
        reset_cpu();

        // 7. TEST INTERNAL RAM (STORE and LOAD)
        $display("Testing RAM: Store 7 to addr 3, clear ACC, Load from addr 3");
        
        // Step A: Load 7 into Accumulator
        @(negedge clk) ui_in = 8'b0001_0111; // LDA 7
        
        // Step B: Store Accumulator (7) into RAM Address 3
        @(negedge clk) ui_in = 8'b0101_0011; // STORE to Addr 3
        
        // Step C: Clear the Accumulator to prove we aren't cheating
        @(negedge clk) ui_in = 8'b0001_0000; // LDA 0
        
        // Step D: Load RAM Address 3 back into Accumulator
        @(negedge clk) ui_in = 8'b1010_0011; // LOAD from Addr 3
        
        // Step E: Output the result (Should be 7)
        @(negedge clk) ui_in = 8'b1000_0000; // OUT
        @(negedge clk);
        reset_cpu();

        // FINISH SIMULATION
        $display("All tests completed.");
        $finish;
    end
endmodule