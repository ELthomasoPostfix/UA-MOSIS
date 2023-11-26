// "delta" is the time delta since the previous iteration
//   Because this is the first computation, it will just be a really small value

PID_Kp_OUT1 = 390;
PID_Kid_OUT1 = 20;
PID_zeroCt_OUT1 = 0;
PID_int_IC = PID_zeroCt_OUT1;
PID_int_IN1 = PID_IN;
PID_int_OUT1 = PID_int_IC;
PID_int_IC = PID_int_OUT1;
PID_int_delay = PID_int_IN1;
PID_der_IC = PID_zeroCt_OUT1;
PID_der_IN1 = PID_IN;
PID_der_OUT1 = 0;
PID_der_IC = PID_der_IN1;
PID_prod1_IN1 = PID_Kp_OUT1;
PID_prod1_IN2 = PID_IN;
PID_prod1_OUT1 = PID_prod1_IN1 * PID_prod1_IN2;
PID_prod2_IN1 = PID_int_OUT1;
PID_prod2_IN2 = PID_Kid_OUT1;
PID_prod2_OUT1 = PID_prod2_IN1 * PID_prod2_IN2;
PID_sum1_IN1 = PID_prod1_OUT1;
PID_sum1_IN2 = PID_prod2_OUT1;
PID_sum1_OUT1 = PID_sum1_IN1 + PID_sum1_IN2;
PID_prod3_IN1 = PID_Kid_OUT1;
PID_prod3_IN2 = PID_der_OUT1;
PID_prod3_OUT1 = PID_prod3_IN1 * PID_prod3_IN2;
PID_sum2_IN1 = PID_sum1_OUT1;
PID_sum2_IN2 = PID_prod3_OUT1;
PID_sum2_OUT1 = PID_sum2_IN1 + PID_sum2_IN2;
PID_OUT = PID_sum2_OUT1;