package PCarController
  type NewtonPerVolt = Real(final quantity = "NewtonPerVolt", final unit = "N/V");
  type DragResistance = Real(final quantity = "DragResistance", final unit = "kg/m");

  model PlantModel
    // Parameters
    parameter NewtonPerVolt A = 60 "The forward gain (N/V) from the control signal";
    parameter Modelica.Units.SI.Mass M = 1500 "The total mass (kg) of the plant";
    parameter DragResistance b = 0.86 "The plant's drag coefficient(kg/m)";
    parameter Modelica.Units.SI.Voltage u "The control signal (V) at time t";
    // Variables
    Modelica.Units.SI.Position x(start = 0) "The plant's displacement (m) at time t";
    Modelica.Units.SI.Velocity v(start = Modelica.Units.Conversions.from_kmh(108)) "The plant's velocity (m/s) at time t";
    Modelica.Units.SI.Acceleration a "The plant's acceleration (m/s^2) at time t";
  equation
    der(x) = v "Relation between displacement and velocity";
    der(v) = a "Relation between velocity and acceleration";
    M*der(v) = (A*u - b*v*v) "The plant's equation of motion (N)";
  end PlantModel;

  block CarAccToDisplacement
    extends Modelica.Blocks.Interfaces.SISO;
    Modelica.Blocks.Sources.Constant xl0(k = 10.0) annotation(
      Placement(visible = true, transformation(origin = {-70, 70}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant vl0(k = 2.5) annotation(
      Placement(visible = true, transformation(origin = {-70, 30}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Product product annotation(
      Placement(visible = true, transformation(origin = {-32, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Integrator integrator1 annotation(
      Placement(visible = true, transformation(origin = {-54, -40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Integrator integrator2 annotation(
      Placement(visible = true, transformation(origin = {-10, -40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.MultiSum multiSum(nu = 3) annotation(
      Placement(visible = true, transformation(origin = {38, 0}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
    Modelica.Blocks.Sources.ContinuousClock t annotation(
      Placement(visible = true, transformation(origin = {-70, -6}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(integrator1.y, integrator2.u) annotation(
      Line(points = {{-42, -40}, {-22, -40}}, color = {0, 0, 127}));
    connect(product.y, multiSum.u[1]) annotation(
      Line(points = {{-21, 0}, {32, 0}}, color = {0, 0, 127}));
    connect(integrator2.y, multiSum.u[2]) annotation(
      Line(points = {{2, -40}, {32, -40}, {32, 0}}, color = {0, 0, 127}));
    connect(xl0.y, multiSum.u[3]) annotation(
      Line(points = {{-58, 70}, {32, 70}, {32, 0}}, color = {0, 0, 127}));
    connect(vl0.y, product.u1) annotation(
      Line(points = {{-59, 30}, {-44, 30}, {-44, 6}}, color = {0, 0, 127}));
    connect(t.y, product.u2) annotation(
      Line(points = {{-59, -6}, {-44, -6}}, color = {0, 0, 127}));
    connect(multiSum.y, y) annotation(
      Line(points = {{45, 0}, {110, 0}}, color = {0, 0, 127}));
    connect(u, integrator1.u) annotation(
      Line(points = {{-120, 0}, {-94, 0}, {-94, -40}, {-66, -40}}, color = {0, 0, 127}));
    annotation(
      Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}})));
  end CarAccToDisplacement;

  model PIDController
    Modelica.Blocks.Interfaces.RealInput Kd annotation(
      Placement(visible = true, transformation(origin = {-120, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, -12}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    Modelica.Blocks.Interfaces.RealInput Ki annotation(
      Placement(visible = true, transformation(origin = {-120, 40}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, 40}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    Modelica.Blocks.Interfaces.RealInput Kp annotation(
      Placement(visible = true, transformation(origin = {-120, 80}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, 90}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    Modelica.Blocks.Interfaces.RealInput et annotation(
      Placement(visible = true, transformation(origin = {-120, -60}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, -80}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    Modelica.Blocks.Interfaces.RealOutput ut annotation(
      Placement(visible = true, transformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Product P annotation(
      Placement(visible = true, transformation(origin = {-2, 74}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Product I annotation(
      Placement(visible = true, transformation(origin = {-2, 34}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Integrator etInt annotation(
      Placement(visible = true, transformation(origin = {-50, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Derivative det annotation(
      Placement(visible = true, transformation(origin = {-50, -60}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Product D annotation(
      Placement(visible = true, transformation(origin = {-2, -6}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.MultiSum multiSum(nu = 3) annotation(
      Placement(visible = true, transformation(origin = {46, 0}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  equation
    connect(Kp, P.u1) annotation(
      Line(points = {{-120, 80}, {-14, 80}}, color = {0, 170, 0}, thickness = 0.5));
    connect(Ki, I.u1) annotation(
      Line(points = {{-120, 40}, {-14, 40}}, color = {255, 170, 0}, thickness = 0.5));
    connect(et, etInt.u) annotation(
      Line(points = {{-120, -60}, {-76, -60}, {-76, 22}, {-62, 22}}, color = {255, 170, 0}, thickness = 0.5));
    connect(et, P.u2) annotation(
      Line(points = {{-120, -60}, {-84, -60}, {-84, 68}, {-14, 68}}, color = {0, 170, 0}, thickness = 0.5));
    connect(etInt.y, I.u2) annotation(
      Line(points = {{-39, 22}, {-14, 22}, {-14, 28}}, color = {255, 170, 0}, thickness = 0.5));
    connect(et, det.u) annotation(
      Line(points = {{-120, -60}, {-62, -60}}, color = {255, 0, 0}, thickness = 0.5));
    connect(det.y, D.u2) annotation(
      Line(points = {{-39, -60}, {-25, -60}, {-25, -12}, {-14, -12}}, color = {255, 0, 0}, thickness = 0.5));
    connect(Kd, D.u1) annotation(
      Line(points = {{-120, 0}, {-14, 0}}, color = {255, 0, 0}, thickness = 0.5));
    connect(D.y, multiSum.u[1]) annotation(
      Line(points = {{10, -6}, {40, -6}, {40, 0}}, color = {0, 0, 127}));
    connect(I.y, multiSum.u[2]) annotation(
      Line(points = {{10, 34}, {28, 34}, {28, 0}, {40, 0}}, color = {0, 0, 127}));
    connect(P.y, multiSum.u[3]) annotation(
      Line(points = {{10, 74}, {40, 74}, {40, 0}}, color = {0, 0, 127}));
    connect(multiSum.y, ut) annotation(
      Line(points = {{54, 0}, {110, 0}}, color = {0, 0, 127}));
  end PIDController;

  model CarCruiseController
    // parameters
    parameter Real Kp_start=1 "Proportional gain";
    parameter Real Ki_start=1 "Integral gain";
    parameter Real Kd_start=20 "Derivative gain";
    parameter Modelica.Units.SI.Distance rt_start=10 "Target inter-vehicle distance";
    
    
    // blocks
    Modelica.Blocks.Sources.ContinuousClock t annotation(
      Placement(visible = true, transformation(origin = {-110, 60}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Tables.CombiTable1Ds alt(extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint, smoothness = Modelica.Blocks.Types.Smoothness.ConstantSegments, table = [0, 1.75; 20, -0.75; 40, 0.5; 60, -3.25; 70, 0]) annotation(
      Placement(visible = true, transformation(origin = {-70, 60}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    PCarController.CarAccToDisplacement lead_car annotation(
      Placement(visible = true, transformation(origin = {-30, 60}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.MultiSum multiSum(nu = 2) annotation(
      Placement(visible = true, transformation(origin = {72, 28}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
    PCarController.PIDController PID(Kp=Kp_start, Ki=Ki_start, Kd=Kd_start) annotation(
      Placement(visible = true, transformation(origin = {-48, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    car_package.mech_car Plant annotation(
      Placement(visible = true, transformation(origin = {-2, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant rt(k = rt_start) annotation(
      Placement(visible = true, transformation(origin = {-110, -88}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Product product annotation(
      Placement(visible = true, transformation(origin = {-60, -70}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
    Modelica.Blocks.Math.MultiSum et(nu = 2) annotation(
      Placement(visible = true, transformation(origin = {-60, -38}, extent = {{-6, -6}, {6, 6}}, rotation = 90)));
    Modelica.Blocks.Sources.Constant negative(k = -1.0) annotation(
      Placement(visible = true, transformation(origin = {-6, -28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Product negate annotation(
      Placement(visible = true, transformation(origin = {42, 4}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(t.y, alt.u) annotation(
      Line(points = {{-98, 60}, {-82, 60}}, color = {255, 0, 255}, thickness = 0.5));
    connect(alt.y[1], lead_car.u) annotation(
      Line(points = {{-59, 60}, {-42, 60}}, color = {255, 0, 255}, thickness = 0.5));
    connect(lead_car.y, multiSum.u[1]) annotation(
      Line(points = {{-18, 60}, {20, 60}, {20, 28}, {66, 28}}, color = {0, 255, 255}, thickness = 0.5));
    connect(PID.ut, Plant.u) annotation(
      Line(points = {{-37, 10}, {-14, 10}}, color = {0, 0, 127}, thickness = 0.5));
    connect(rt.y, product.u1) annotation(
      Line(points = {{-99, -88}, {-66, -88}, {-66, -82}}, color = {0, 0, 127}, thickness = 0.5));
    connect(product.y, et.u[1]) annotation(
      Line(points = {{-60, -59}, {-60, -44}}, color = {0, 0, 127}, thickness = 0.5));
    connect(et.y, PID.et) annotation(
      Line(points = {{-60, -31}, {-60, 2}}, color = {170, 0, 127}, thickness = 0.5));
    connect(negative.y, product.u2) annotation(
      Line(points = {{6, -28}, {10, -28}, {10, -82}, {-54, -82}}, color = {255, 85, 0}, thickness = 0.5));
    connect(Plant.y, negate.u1) annotation(
      Line(points = {{10, 10}, {30, 10}}, color = {0, 0, 127}, thickness = 0.5));
    connect(negative.y, negate.u2) annotation(
      Line(points = {{5, -28}, {30, -28}, {30, -2}}, color = {255, 85, 0}, thickness = 0.5));
    connect(negate.y, multiSum.u[2]) annotation(
      Line(points = {{54, 4}, {66, 4}, {66, 28}}, color = {255, 255, 0}, thickness = 0.5));
    connect(multiSum.y, et.u[2]) annotation(
      Line(points = {{80, 28}, {90, 28}, {90, -52}, {-60, -52}, {-60, -44}}, color = {0, 0, 127}, thickness = 0.5));
  end CarCruiseController;
  annotation(
    uses(Modelica(version = "4.0.0")));
end PCarController;
