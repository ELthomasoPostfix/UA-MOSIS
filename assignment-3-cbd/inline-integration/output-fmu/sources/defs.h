/**
 *  Definition file. M must be set to the total amount of variables.
 *  The other defines may help you for debugging the generations.
 */

#define M 56

// Variable References in-memory

#define PID_prod2_IN1 (cbd->modelData[0])
#define PID_prod2_IN2 (cbd->modelData[1])
#define PID_der_delta_t_OUT1 (cbd->modelData[2])
#define PID_der_sum1_IN1 (cbd->modelData[3])
#define PID_prod1_IN1 (cbd->modelData[4])
#define PID_int_delayState_IN1 (cbd->modelData[5])
#define PID_der_delay_OUT1 (cbd->modelData[6])
#define PID_prod1_OUT1 (cbd->modelData[7])
#define PID_int_multDelta_IN1 (cbd->modelData[8])
#define PID_der_neg2_IN1 (cbd->modelData[9])
#define PID_OUT (cbd->modelData[10])
#define PID_int_multDelta_IN2 (cbd->modelData[11])
#define PID_int_multDelta_OUT1 (cbd->modelData[12])
#define PID_der_sum2_IN1 (cbd->modelData[13])
#define PID_prod3_OUT1 (cbd->modelData[14])
#define PID_int_sumState_IN2 (cbd->modelData[15])
#define PID_der_multIc_OUT1 (cbd->modelData[16])
#define PID_der_neg1_OUT1 (cbd->modelData[17])
#define PID_prod3_IN2 (cbd->modelData[18])
#define PID_der_inv_OUT1 (cbd->modelData[19])
#define PID_int_zero_OUT1 (cbd->modelData[20])
#define PID_int_sumState_IN1 (cbd->modelData[21])
#define PID_der_neg1_IN1 (cbd->modelData[22])
#define PID_der_neg2_OUT1 (cbd->modelData[23])
#define PID_der_sum2_OUT1 (cbd->modelData[24])
#define PID_der_inv_IN1 (cbd->modelData[25])
#define PID_sum2_OUT1 (cbd->modelData[26])
#define PID_sum1_IN1 (cbd->modelData[27])
#define PID_der_sum1_OUT1 (cbd->modelData[28])
#define PID_zeroCt_OUT1 (cbd->modelData[29])
#define PID_IN (cbd->modelData[30])
#define PID_int_delayIn_IN1 (cbd->modelData[31])
#define PID_int_delta_t_OUT1 (cbd->modelData[32])
#define PID_Kid_OUT1 (cbd->modelData[33])
#define PID_der_delay_IC (cbd->modelData[34])
#define PID_Kp_OUT1 (cbd->modelData[35])
#define PID_int_delayIn_OUT1 (cbd->modelData[36])
#define PID_der_multIc_IN1 (cbd->modelData[37])
#define PID_prod3_IN1 (cbd->modelData[38])
#define PID_sum2_IN1 (cbd->modelData[39])
#define PID_der_mult_IN1 (cbd->modelData[40])
#define PID_int_delayState_IC (cbd->modelData[41])
#define PID_der_sum1_IN2 (cbd->modelData[42])
#define PID_sum1_OUT1 (cbd->modelData[43])
#define PID_sum2_IN2 (cbd->modelData[44])
#define PID_prod2_OUT1 (cbd->modelData[45])
#define PID_der_delay_IN1 (cbd->modelData[46])
#define PID_prod1_IN2 (cbd->modelData[47])
#define PID_der_mult_IN2 (cbd->modelData[48])
#define PID_sum1_IN2 (cbd->modelData[49])
#define PID_der_multIc_IN2 (cbd->modelData[50])
#define PID_der_sum2_IN2 (cbd->modelData[51])
#define PID_int_delayIn_IC (cbd->modelData[52])
#define PID_int_delayState_OUT1 (cbd->modelData[53])
#define PID_der_mult_OUT1 (cbd->modelData[54])
#define PID_int_sumState_OUT1 (cbd->modelData[55])