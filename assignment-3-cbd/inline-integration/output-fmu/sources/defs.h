/**
 *  Definition file. M must be set to the total amount of variables.
 *  The other defines may help you for debugging the generations.
 */

#define M 27

// Variable References in-memory

#define PID_prod1_IN1 (cbd->modelData[0])
#define PID_prod1_IN2 (cbd->modelData[1])
#define PID_prod2_OUT1 (cbd->modelData[2])
#define PID_int_IN1 (cbd->modelData[3])
#define PID_sum1_OUT1 (cbd->modelData[4])
#define PID_der_OUT1 (cbd->modelData[5])
#define PID_prod2_IN1 (cbd->modelData[6])
#define PID_der_IN1 (cbd->modelData[7])
#define PID_prod2_IN2 (cbd->modelData[8])
#define PID_sum1_IN1 (cbd->modelData[9])
#define PID_sum1_IN2 (cbd->modelData[10])
#define PID_Kp_OUT1 (cbd->modelData[11])
#define PID_der_IC (cbd->modelData[12])
#define PID_Kid_OUT1 (cbd->modelData[13])
#define PID_int_IC (cbd->modelData[14])
#define PID_prod3_OUT1 (cbd->modelData[15])
#define PID_sum2_OUT1 (cbd->modelData[16])
#define PID_prod3_IN1 (cbd->modelData[17])
#define PID_sum2_IN1 (cbd->modelData[18])
#define PID_sum2_IN2 (cbd->modelData[19])
#define PID_prod3_IN2 (cbd->modelData[20])
#define PID_OUT (cbd->modelData[21])
#define PID_IN (cbd->modelData[22])
#define PID_int_delay (cbd->modelData[23])
#define PID_int_OUT1 (cbd->modelData[24])
#define PID_prod1_OUT1 (cbd->modelData[25])
#define PID_zeroCt_OUT1 (cbd->modelData[26])