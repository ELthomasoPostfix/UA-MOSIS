// "delta" is the time delta since the previous iteration


PID_Kp_OUT1 = 390;
PID_Kid_OUT1 = 20;
PID_prod1_IN2 = PID_IN;
PID_int_delayIn_IN1 = PID_IN;
PID_der_sum1_IN2 = PID_IN;
PID_der_delay_IN1 = PID_IN;
PID_der_sum2_IN2 = PID_IN;
PID_prod1_IN1 = PID_Kp_OUT1;
PID_prod1_IN2 = PID_IN;
PID_prod1_OUT1 = PID_prod1_IN1 * PID_prod1_IN2;
PID_int_zero_OUT1 = 0;
PID_int_delayIn_IN1 = PID_IN;
PID_int_delayIn_OUT1 = PID_int_delayIn_IC;
PID_int_delayIn_IC = PID_int_delayIn_IN1;
PID_int_delta_t_OUT1 = delta;
PID_int_multDelta_IN1 = PID_int_delayIn_OUT1;
PID_int_multDelta_IN2 = PID_int_delta_t_OUT1;
PID_int_multDelta_OUT1 = PID_int_multDelta_IN1 * PID_int_multDelta_IN2;
PID_zeroCt_OUT1 = PID_IN;
PID_int_delayState_IN1 = PID_int_sumState_OUT1;
PID_int_delayState_OUT1 = PID_int_delayState_IC;
PID_int_delayState_IC = PID_int_delayState_IN1;
PID_int_sumState_IN1 = PID_int_multDelta_OUT1;
PID_int_sumState_IN2 = PID_int_delayState_OUT1;
PID_int_sumState_OUT1 = PID_int_sumState_IN1 + PID_int_sumState_IN2;
PID_prod2_IN1 = PID_int_sumState_OUT1;
PID_prod2_IN2 = PID_Kid_OUT1;
PID_prod2_OUT1 = PID_prod2_IN1 * PID_prod2_IN2;
PID_sum1_IN1 = PID_prod1_OUT1;
PID_sum1_IN2 = PID_prod2_OUT1;
PID_sum1_OUT1 = PID_sum1_IN1 + PID_sum1_IN2;
PID_der_delta_t_OUT1 = delta;
PID_der_multIc_IN1 = PID_zeroCt_OUT1;
PID_der_multIc_IN2 = PID_der_delta_t_OUT1;
PID_der_multIc_OUT1 = PID_der_multIc_IN1 * PID_der_multIc_IN2;
PID_der_neg1_IN1 = PID_der_multIc_OUT1;
PID_der_neg1_OUT1 = -PID_der_neg1_IN1;
PID_der_sum1_IN1 = PID_der_neg1_OUT1;
PID_der_sum1_IN2 = PID_IN;
PID_der_sum1_OUT1 = PID_der_sum1_IN1 + PID_der_sum1_IN2;
PID_der_delay_IN1 = PID_IN;
PID_der_delay_OUT1 = PID_der_delay_IC;
PID_der_delay_IC = PID_der_delay_IN1;
PID_der_neg2_IN1 = PID_der_delay_OUT1;
PID_der_neg2_OUT1 = -PID_der_neg2_IN1;
PID_der_sum2_IN1 = PID_der_neg2_OUT1;
PID_der_sum2_IN2 = PID_IN;
PID_der_sum2_OUT1 = PID_der_sum2_IN1 + PID_der_sum2_IN2;
PID_der_inv_IN1 = PID_der_delta_t_OUT1;
PID_der_inv_OUT1 = 1 / PID_der_inv_IN1;
PID_der_mult_IN1 = PID_der_sum2_OUT1;
PID_der_mult_IN2 = PID_der_inv_OUT1;
PID_der_mult_OUT1 = PID_der_mult_IN1 * PID_der_mult_IN2;
PID_prod3_IN1 = PID_Kid_OUT1;
PID_prod3_IN2 = PID_der_mult_OUT1;
PID_prod3_OUT1 = PID_prod3_IN1 * PID_prod3_IN2;
PID_sum2_IN1 = PID_sum1_OUT1;
PID_sum2_IN2 = PID_prod3_OUT1;
PID_sum2_OUT1 = PID_sum2_IN1 + PID_sum2_IN2;
PID_OUT = PID_sum2_OUT1;

//// File pointer
//FILE *file;
//
//// Open the file in write mode
//file = fopen("debug.csv", "a");
//
//// Check if the file is successfully opened
//if (file == NULL) {
//    fprintf(stderr, "Error opening file.\n");
//}
//
//// Write every float value with a comma delimiter
//fprintf(file, "%f,", PID_IN);
//fprintf(file, "%f,", PID_Kp_OUT1);
//fprintf(file, "%f,", PID_Kid_OUT1);
//fprintf(file, "%f,", PID_prod1_IN2);
//fprintf(file, "%f,", PID_int_delayIn_IN1);
//fprintf(file, "%f,", PID_der_sum1_IN2);
//fprintf(file, "%f,", PID_der_delay_IN1);
//fprintf(file, "%f,", PID_der_sum2_IN2);
//fprintf(file, "%f,", PID_prod1_IN1);
//fprintf(file, "%f,", PID_prod1_IN2);
//fprintf(file, "%f,", PID_prod1_OUT1);
//fprintf(file, "%f,", PID_int_zero_OUT1);
//fprintf(file, "%f,", PID_int_delayIn_IN1);
//fprintf(file, "%f,", PID_int_delayIn_OUT1);
//fprintf(file, "%f,", PID_int_delayIn_IC);
//fprintf(file, "%f,", PID_int_delta_t_OUT1);
//fprintf(file, "%f,", PID_int_multDelta_IN1);
//fprintf(file, "%f,", PID_int_multDelta_IN2);
//fprintf(file, "%f,", PID_int_multDelta_OUT1);
//fprintf(file, "%f,", PID_zeroCt_OUT1);
//fprintf(file, "%f,", PID_int_delayState_IN1);
//fprintf(file, "%f,", PID_int_delayState_OUT1);
//fprintf(file, "%f,", PID_int_delayState_IC);
//fprintf(file, "%f,", PID_int_sumState_IN1);
//fprintf(file, "%f,", PID_int_sumState_IN2);
//fprintf(file, "%f,", PID_int_sumState_OUT1);
//fprintf(file, "%f,", PID_prod2_IN1);
//fprintf(file, "%f,", PID_prod2_IN2);
//fprintf(file, "%f,", PID_prod2_OUT1);
//fprintf(file, "%f,", PID_sum1_IN1);
//fprintf(file, "%f,", PID_sum1_IN2);
//fprintf(file, "%f,", PID_sum1_OUT1);
//fprintf(file, "%f,", PID_der_delta_t_OUT1);
//fprintf(file, "%f,", PID_der_multIc_IN1);
//fprintf(file, "%f,", PID_der_multIc_IN2);
//fprintf(file, "%f,", PID_der_multIc_OUT1);
//fprintf(file, "%f,", PID_der_neg1_IN1);
//fprintf(file, "%f,", PID_der_neg1_OUT1);
//fprintf(file, "%f,", PID_der_sum1_IN1);
//fprintf(file, "%f,", PID_der_sum1_IN2);
//fprintf(file, "%f,", PID_der_sum1_OUT1);
//fprintf(file, "%f,", PID_der_delay_IN1);
//fprintf(file, "%f,", PID_der_delay_OUT1);
//fprintf(file, "%f,", PID_der_delay_IC);
//fprintf(file, "%f,", PID_der_neg2_IN1);
//fprintf(file, "%f,", PID_der_neg2_OUT1);
//fprintf(file, "%f,", PID_der_sum2_IN1);
//fprintf(file, "%f,", PID_der_sum2_IN2);
//fprintf(file, "%f,", PID_der_sum2_OUT1);
//fprintf(file, "%f,", PID_der_inv_IN1);
//fprintf(file, "%f,", PID_der_inv_OUT1);
//fprintf(file, "%f,", PID_der_mult_IN1);
//fprintf(file, "%f,", PID_der_mult_IN2);
//fprintf(file, "%f,", PID_der_mult_OUT1);
//fprintf(file, "%f,", PID_prod3_IN1);
//fprintf(file, "%f,", PID_prod3_IN2);
//fprintf(file, "%f,", PID_prod3_OUT1);
//fprintf(file, "%f,", PID_sum2_IN1);
//fprintf(file, "%f,", PID_sum2_IN2);
//fprintf(file, "%f,", PID_sum2_OUT1);
//fprintf(file, "%f\n", PID_OUT);
//
//
//// Close the file
//fclose(file);
