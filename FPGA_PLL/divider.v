module divider (input        clk_ref_12M,
                input        clk_rf,
                output reg   clk_div_ref,
                output reg   clk_div_rf,
                input        spi_clk_i, 
                input        spi_ncs_i, 
                input        spi_mosi, 
                output [4:0] dbg,
                output [4:0] led
                );
   

   reg [9:0]       N_counter;
   reg [12:0]      A_counter;
   reg [31:0]      spi_data;
   
   reg [9:0]       N_div_val;
   reg [12:0]      A_div_val;
   
   parameter N_div = 480/2;
   parameter A_div = 1980/2;

   assign led[0] = spi_mosi;
   assign led[1] = spi_ncs_i;
   assign led[2] = spi_clk_i;
   assign led[3] = N_div_val[8];
   assign led[4] = A_div_val[9];
   

   assign dbg[4:3] = N_counter[8:7];
   assign dbg[2:0] = A_counter[9:7];
   
   always @ (posedge clk_ref_12M)
     if (N_counter == N_div_val) begin
        N_counter <= 0;
        clk_div_ref <= ~clk_div_ref;
     end
     else
       N_counter <= N_counter + 1;
   

   always @ (posedge clk_rf)
     if (A_counter == A_div_val) begin
        A_counter <= 0;
        clk_div_rf <= ~clk_div_rf;
     end
     else
       A_counter <= A_counter + 1;

   always @ (posedge spi_clk_i)
     if (~spi_ncs_i)
       begin
          spi_data[31:1] <= spi_data[30:0];
          spi_data[0] <= spi_mosi;
       end

   always @ (posedge spi_ncs_i) begin
      N_div_val <= spi_data[25:16];
      A_div_val <= spi_data[12:0];
   end
   

endmodule //


     
        
