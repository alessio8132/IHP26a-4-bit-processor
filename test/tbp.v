// Personal test bench for personalized tests of the verilog.
`timescale 1ns/1ps

module tb();
    // 1. Create signals to connect to your chip
    reg clk;
    reg rst_n;
    reg [7:0] ui_in;
    wire [7:0] uo_out;

    // 2. Instantiate your chip (The "Unit Under Test")
    tt_um_example uut (
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
        $dumpfile("sim.vcd"); // Creates the file for GTKWave
        $dumpvars(0, tb);

        clk = 0;
        rst_n = 0; #20 rst_n = 1;  // Start in Reset
        ui_in = 8'h15; #20; //LDA 5
        ui_in = 8'h23; #20; //ADD 3
        ui_in = 8'hF0; #20; //HALT
        
        //#50 rst_n = 1; // Release Reset after 50ns
        
        #500 $finish; // Stop the simulation after some time
    end
endmodule