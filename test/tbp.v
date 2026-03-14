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
    initial begin
        $dumpfile("sim.vcd");
        $dumpvars(0, tb);

        // 1. Setup initial state
        clk = 0;
        rst_n = 0;   
        ui_in = 8'h00;

        // 2. Wait a bit, then release reset (Not on a clock edge)
        #45 rst_n = 1; 

        // 3. Now use clock edges to sync your instructions
        @(posedge clk); #1; ui_in = 8'h15; // PC 0: Load 5
        @(posedge clk); #1; ui_in = 8'b00100011; // PC 1: Add 3
        @(posedge clk); #1; ui_in = 8'b10000000; // OUT: Output current ACC content (should be 8)
        //@(posedge clk); ui_in = 8'h23; // PC 1: Add 3 again
        
        // 4. Force a termination after a few more cycles
        repeat (10) @(posedge clk);
        
        $display("Simulation finished successfully!");
        $finish;
    end
endmodule