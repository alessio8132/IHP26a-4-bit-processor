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
always @(posedge clk) begin
        if (!rst_n) begin
            pc  <= 4'b0000;
            acc <= 4'b0000;
        end else begin
            pc <= pc + 1;

            // DECODE & EXECUTE
            case (ui_in[7:4])      // Look at the top 4 bits
                4'b0001: acc <= ui_in[3:0];       // LDA: Load bottom 4 bits into acc
                4'b0010: acc <= acc + ui_in[3:0]; // ADD: Add bottom 4 bits to acc
                4'b1111: pc  <= pc;               // HALT: Don't move the PC
                default: acc <= acc;              // NOP: Do nothing
            endcase
        end
    end



assign uo_out = {pc, acc};
assign uio_out = 0;
assign uio_oe = 0;

wire _unused = &{ena, uio_in, 1'b0};

endmodule
