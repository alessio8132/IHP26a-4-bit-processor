`timescale 1ns/1ps

module tb_cpu;

    // Inputs
    reg clk;
    reg rst_n;
    reg [7:0] ui_in;

    // Outputs
    // Tiny Tapeout Standard Output
    wire [7:0] uo_out;

    // Unpack the uo_out pins back into our separate signals!
    wire [3:0] pc = uo_out[7:4];
    wire [3:0] output_register = uo_out[3:0];

    // Opcodes for readability
    localparam LDA   = 4'b0001;
    localparam ADD   = 4'b0010;
    localparam SUB   = 4'b0011;
    localparam STORE = 4'b0101;
    localparam LOAD  = 4'b1010;
    localparam OUT   = 4'b1000;
    localparam AND_op= 4'b1011;
    localparam JMP   = 4'b1100;

    // Tiny simulated ROM for the Fibonacci sequence
    reg [7:0] rom [0:15];
    reg auto_run; // Switch to let the CPU fetch its own instructions


    tt_um_alessio8132 uut (
        .clk(clk),
        .rst_n(rst_n),
        .ui_in(ui_in),
        .uo_out(uo_out), 
        .uio_in(),   // Not used in this testbench
        .uio_out(),  // Not used in this testbench
        .uio_oe(),   // Not used in this testbench
        .ena(1'b1)   // Always enabled
    );

    // Clock Generation (10ns period / 100MHz)
    always #5 clk = ~clk;

    // Task from your prompt
    task reset_cpu;
        begin
            ui_in = 8'b0000_0000; 
            rst_n = 1'b0; 
            @(negedge clk);
            rst_n = 1'b1; 
        end
    endtask

    // Helper task to feed instructions safely on the falling edge
    task feed_inst(input [3:0] opcode, input [3:0] value);
        begin
            @(negedge clk);
            ui_in = {opcode, value};
        end
    endtask

    // Automatic ROM Fetching block (Runs only when auto_run is high)
    always @(negedge clk) begin
        if (auto_run) begin
            ui_in = rom[pc]; // Feed instruction based on CPU's Program Counter
        end
    end

    initial begin
        // Initialize
        clk = 0;
        auto_run = 0;
        
        $display("--- Starting CPU Tests ---");
        reset_cpu();

        // ==========================================
        // TEST 1: LDA, STORE, ADD, OUT
        // ==========================================
        $display("Testing ADD (Memory)...");
        feed_inst(LDA,   4'd3); // ACC = 3
        feed_inst(STORE, 4'd0); // RAM[0] = 3
        feed_inst(LDA,   4'd4); // ACC = 4
        feed_inst(ADD,   4'd0); // ACC = 4 + RAM[0] = 7
        feed_inst(OUT,   4'd0); // Output = 7
        @(negedge clk);         // Wait one tick for output to register
        $display("Output Register after ADD: %d (Expected: 7)", output_register);

        // ==========================================
        // TEST 2: SUB (Memory)
        // ==========================================
        $display("Testing SUB (Memory)...");
        feed_inst(LDA,   4'd5); // ACC = 5
        feed_inst(STORE, 4'd1); // RAM[1] = 5
        feed_inst(LDA,   4'd9); // ACC = 9
        feed_inst(SUB,   4'd1); // ACC = 9 - RAM[1] = 4
        feed_inst(OUT,   4'd0); // Output = 4
        @(negedge clk);
        $display("Output Register after SUB: %d (Expected: 4)", output_register);

        // ==========================================
        // TEST 3: AND (Memory)
        // ==========================================
        $display("Testing AND (Memory)...");
        feed_inst(LDA,   4'b1100); // ACC = 12
        feed_inst(STORE, 4'd2);    // RAM[2] = 12
        feed_inst(LDA,   4'b1010); // ACC = 10
        feed_inst(AND_op,4'd2);    // ACC = 1010 & 1100 = 1000 (8)
        feed_inst(OUT,   4'd0);
        @(negedge clk);
        $display("Output Register after AND: %b (Expected: 1000)", output_register);

        // ==========================================
        // TEST 4: FIBONACCI SEQUENCE & JMP
        // ==========================================
        $display("--- Loading Fibonacci ROM ---");
        reset_cpu();
        
        // Let x = RAM[0], y = RAM[1], temp = RAM[2]
        rom[0]  = {LDA,   4'd0}; // Start x at 0
        rom[1]  = {STORE, 4'd0}; 
        rom[2]  = {LDA,   4'd1}; // Start y at 1
        rom[3]  = {STORE, 4'd1}; 
        
        // --- LOOP STARTS HERE (Address 4) ---
        rom[4]  = {LOAD,  4'd0}; // ACC = x
        rom[5]  = {OUT,   4'd0}; // Output x!
        rom[6]  = {ADD,   4'd1}; // ACC = x + y
        rom[7]  = {STORE, 4'd2}; // temp = x + y
        rom[8]  = {LOAD,  4'd1}; // ACC = y
        rom[9]  = {STORE, 4'd0}; // x = y
        rom[10] = {LOAD,  4'd2}; // ACC = temp
        rom[11] = {STORE, 4'd1}; // y = temp
        rom[12] = {JMP,   4'd4}; // Jump back to output and repeat!
        
        // Turn on the ROM and let the CPU run wild!
        auto_run = 1;
        
        // Wait and watch the outputs
        $display("Running Fibonacci... Watch the outputs!");
        repeat (100) begin
            @(posedge clk);
            if (ui_in[7:4] == OUT) begin
                // Whenever the CPU executes an OUT instruction, print it
                @(negedge clk); // Wait for the output to register
                #1 $display("Fibonacci Number: %d", output_register);
            end
        end

        $display("Tests Complete!");
        $finish;
    end

endmodule