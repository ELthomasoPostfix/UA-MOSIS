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
    annotation(
      experiment(StartTime = 0, StopTime = 60, Tolerance = 1e-09, Interval = 1));
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
    parameter Modelica.Units.SI.Distance rt_value = 10 "Target inter-vehicle distance";
    parameter Real u_value = 10 "PID control signal";
  // blocks
    Modelica.Blocks.Sources.ContinuousClock t annotation(
      Placement(visible = true, transformation(origin = {-110, 70}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Tables.CombiTable1Ds alt(extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint, smoothness = Modelica.Blocks.Types.Smoothness.ConstantSegments, table = [0, 1.75; 20, -0.75; 40, 0.5; 60, -3.25; 70, 0]) annotation(
      Placement(visible = true, transformation(origin = {-70, 70}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    PCarController.CarAccToDisplacement forward_car annotation(
      Placement(visible = true, transformation(origin = {-30, 70}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.MultiSum multiSum(nu = 2) annotation(
      Placement(visible = true, transformation(origin = {50, -10}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
    car_package.mech_car ego_car annotation(
      Placement(visible = true, transformation(origin = {-30, 30}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant rt(k = rt_value) annotation(
      Placement(visible = true, transformation(origin = {-110, -50}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Product product annotation(
      Placement(visible = true, transformation(origin = {10, -30}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant negative(k = -1.0) annotation(
      Placement(visible = true, transformation(origin = {-110, -10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Product negate annotation(
      Placement(visible = true, transformation(origin = {10, 12}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.MultiSum multiSum1(nu = 2) annotation(
      Placement(visible = true, transformation(origin = {80, -20}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput e annotation(
      Placement(visible = true, transformation(origin = {110, -20}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {110, -20}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant u(k = u_value) annotation(
      Placement(visible = true, transformation(origin = {-110, 30}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(t.y, alt.u) annotation(
      Line(points = {{-99, 70}, {-82, 70}}, color = {255, 0, 255}, thickness = 0.5));
    connect(alt.y[1], forward_car.u) annotation(
      Line(points = {{-59, 70}, {-42, 70}}, color = {255, 0, 255}, thickness = 0.5));
    connect(forward_car.y, multiSum.u[1]) annotation(
      Line(points = {{-19, 70}, {32.5, 70}, {32.5, -10}, {44, -10}}, color = {0, 255, 255}, thickness = 0.5));
    connect(negate.y, multiSum.u[2]) annotation(
      Line(points = {{22, 12}, {32, 12}, {32, -10}, {44, -10}}, color = {0, 255, 255}, thickness = 0.5));
    connect(ego_car.y, negate.u1) annotation(
      Line(points = {{-18, 30}, {-12, 30}, {-12, 18}, {-2, 18}}, color = {0, 0, 255}, thickness = 0.5));
    connect(negative.y, negate.u2) annotation(
      Line(points = {{-98, -10}, {-60, -10}, {-60, 6}, {-2, 6}}, color = {255, 85, 0}, thickness = 0.5));
    connect(negative.y, product.u1) annotation(
      Line(points = {{-98, -10}, {-60, -10}, {-60, -24}, {-2, -24}}, color = {255, 85, 0}, thickness = 0.5));
    connect(rt.y, product.u2) annotation(
      Line(points = {{-98, -50}, {-60, -50}, {-60, -36}, {-2, -36}}, color = {0, 170, 0}, thickness = 0.5));
    connect(multiSum.y, multiSum1.u[1]) annotation(
      Line(points = {{58, -10}, {60, -10}, {60, -20}, {74, -20}}, color = {170, 255, 227}, thickness = 0.5));
    connect(product.y, multiSum1.u[2]) annotation(
      Line(points = {{22, -30}, {60, -30}, {60, -20}, {74, -20}}, color = {158, 255, 207}, thickness = 0.5));
    connect(multiSum1.y, e) annotation(
      Line(points = {{88, -20}, {110, -20}}, color = {255, 224, 98}, thickness = 0.5));
  connect(u.y, ego_car.u) annotation(
      Line(points = {{-98, 30}, {-42, 30}}, color = {85, 0, 255}, thickness = 0.5));
    annotation(
      experiment(StartTime = 0, StopTime = 70, Tolerance = 1e-09, Interval = 0.1),
      Diagram);
  end CarCruiseController;
  annotation(
    uses(Modelica(version = "4.0.0")));
end PCarController;
