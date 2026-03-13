/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none
`timescale 1ns/1ps

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
reg [3:0] pc; //4-bit Program Counter
reg [3:0] acc; //4-Bit accumulator
reg [3:0] output_register; //4-bit output register
reg [3:0] mem_to_send;
reg mem_write_en;
wire is_zero = (acc == 4'b0000); // Check if ACC is zero
always @(posedge clk) begin
        if (!rst_n) begin
            pc  <= 4'b0000;
            acc <= 4'b0000;
        end else begin
            if (ui_in[7:4] == 4'b1100) begin
                pc <= ui_in[3:0]; // Jump to the address in the bottom 4 bits
            end 
            if (ui_in[7:4] == 4'b0100) begin
                pc <= ui_in[3:0]; // Jumpt to address in the buttom 4 bits if ACC is zero
            end else begin
                pc <= pc + 1;     // Otherwise, just keep counting
            end

            // DECODE & EXECUTE
            case (ui_in[7:4])      // Look at the top 4 bits
                4'b0001: acc <= ui_in[3:0];       // LDA: Load bottom 4 bits into acc
                4'b0010: acc <= acc + ui_in[3:0]; // ADD: Add bottom 4 bits to acc
                4'b0011: acc <= acc - ui_in[3:0]; // SUB: Subtract bottom 4 bits to ACC
                4'b0110: acc <= acc << 1;         // SHL: Shift left 
                4'b0111: acc <= acc ^ ui_in[3:0]; // XOR: bitwise exclusive or
                4'b1011: acc <= acc & ui_in[3:0]; // AND: bitwise and
                4'b1101: acc <= acc | ui_in[3:0]; // OR: bitwise or
                4'b1000: output_register <= acc;  // OUT: output current ACC content
                4'b1111: pc  <= pc;               // HALT: Don't move the PC
                4'b0101: begin                    // STORE: Store ACC into memory
                    mem_to_send <= acc; 
                    mem_write_en <= 1'b1:
                end
                4'b1010: begin                    
                    acc <= uio_in[3:0];          //LOAD: Load memory into ACC
                    mem_write_en = 1'b0;
                end
                default: begin
                    acc <= acc;
                    mem_write_en <= 1'b0;  // NOP: Do nothing
                end              
            endcase
        end
    end



assign uo_out = {pc, output_register};
assign uio_out = {ui_in[3:0], mem_data_out};
assign uio_oe = (mem_write_en) ? 8'hFF : 8'h00;

wire _unused = &{ena, uio_in, 1'b0};

endmodule
