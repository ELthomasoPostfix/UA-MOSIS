package CarCruiseController
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

  type NewtonPerVolt = Real(final quantity = "NewtonPerVolt", final unit = "N/V");
  type DragResistance = Real(final quantity = "DragResistance", final unit = "kg/m");

  model CarCruiseController
    Modelica.Blocks.Tables.CombiTable1Ds alt(extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint, smoothness = Modelica.Blocks.Types.Smoothness.ConstantSegments, table = [0, 1.75; 20, -0.75; 40, 0.5; 60, -3.25; 70, 0]) annotation(
      Placement(visible = true, transformation(origin = {-30, 20}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.ContinuousClock t annotation(
      Placement(visible = true, transformation(origin = {-110, 46}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    CarCruiseController.CarAccToDisplacement lead_car annotation(
      Placement(visible = true, transformation(origin = {10, 24}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant rt(k = 10.0) annotation(
      Placement(visible = true, transformation(origin = {-110, -80}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  car_package.mech_car Plant annotation(
      Placement(visible = true, transformation(origin = {10, -10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  CarCruiseController.PIDController PID annotation(
      Placement(visible = true, transformation(origin = {-30, -10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput Ki annotation(
      Placement(visible = true, transformation(origin = {-122, -26}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-92, -14}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput Kp annotation(
      Placement(visible = true, transformation(origin = {-122, -2}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-116, -56}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput Kd annotation(
      Placement(visible = true, transformation(origin = {-122, -50}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, -80}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Math.Sum sum annotation(
      Placement(visible = true, transformation(origin = {74, 24}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant neg(k = -1)  annotation(
      Placement(visible = true, transformation(origin = {10, -40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Product negate annotation(
      Placement(visible = true, transformation(origin = {44, -22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Sum sum1 annotation(
      Placement(visible = true, transformation(origin = {-50, -50}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Math.Product product annotation(
      Placement(visible = true, transformation(origin = {-68, -86}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(t.y, alt.u) annotation(
      Line(points = {{-99, 46}, {-59.5, 46}, {-59.5, 20}, {-42, 20}}, color = {255, 0, 255}, thickness = 0.5));
    connect(t.y, lead_car.CurrentTime) annotation(
      Line(points = {{-39, 10}, {3, 10}, {3, 0}}, color = {0, 0, 127}));
    connect(alt.y[1], lead_car.Acceleration) annotation(
      Line(points = {{-5, -8}, {3, -8}}, color = {0, 0, 127}));
  connect(Kp, PID.Kp) annotation(
      Line(points = {{-122, -2}, {-42, -2}}, color = {0, 170, 0}, thickness = 0.5));
  connect(Ki, PID.Ki) annotation(
      Line(points = {{-122, -26}, {-87.5, -26}, {-87.5, -7}, {-42, -7}}, color = {255, 170, 0}, thickness = 0.5));
  connect(alt.y[1], lead_car.alt) annotation(
      Line(points = {{-18, 20}, {-2, 20}}, color = {85, 0, 127}, thickness = 0.5));
  connect(t.y, lead_car.t) annotation(
      Line(points = {{-99, 46}, {-2, 46}, {-2, 28}}, color = {255, 0, 255}, thickness = 0.5));
  connect(neg.y, negate.u2) annotation(
      Line(points = {{21, -40}, {32, -40}, {32, -28}}, color = {255, 85, 0}, thickness = 0.5));
  connect(lead_car.xlt, sum.u[1]) annotation(
      Line(points = {{22, 24}, {62, 24}}, color = {0, 255, 255}, thickness = 0.5));
  connect(Kd, PID.Kd) annotation(
      Line(points = {{-122, -50}, {-78, -50}, {-78, -12}, {-42, -12}}, color = {255, 0, 0}, thickness = 0.5));
  connect(negate.y, sum.u[1]) annotation(
      Line(points = {{56, -22}, {62, -22}, {62, 24}}, color = {255, 255, 0}, thickness = 0.5));
  connect(sum1.y, PID.et) annotation(
      Line(points = {{-50, -38}, {-50, -18}, {-42, -18}}, color = {170, 0, 127}, thickness = 0.5));
  connect(rt.y, product.u1) annotation(
      Line(points = {{-98, -80}, {-80, -80}}, color = {0, 0, 127}, thickness = 0.5));
  connect(neg.y, product.u2) annotation(
      Line(points = {{22, -40}, {32, -40}, {32, -100}, {-94, -100}, {-94, -92}, {-80, -92}}, color = {255, 85, 0}, thickness = 0.5));
  connect(product.y, sum1.u[1]) annotation(
      Line(points = {{-56, -86}, {-50, -86}, {-50, -62}}, color = {0, 0, 127}, thickness = 0.5));
  connect(sum.y, sum1.u[1]) annotation(
      Line(points = {{86, 24}, {94, 24}, {94, -86}, {-50, -86}, {-50, -62}}, color = {0, 0, 127}, thickness = 0.5));
  connect(PID.ut, Plant.u) annotation(
      Line(points = {{-18, -10}, {-2, -10}}, color = {0, 0, 127}, thickness = 0.5));
  connect(Plant.y, negate.u1) annotation(
      Line(points = {{22, -10}, {30, -10}, {30, -16}, {32, -16}}, color = {0, 0, 127}, thickness = 0.5));
  protected
  end CarCruiseController;

  block CarAccToDisplacement
    Modelica.Blocks.Continuous.Integrator integrator2(initType = Modelica.Blocks.Types.Init.InitialOutput, y_start = 0) annotation(
      Placement(visible = true, transformation(origin = {6, -28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Integrator integrator1(y_start = 0) annotation(
      Placement(visible = true, transformation(origin = {-26, -28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant vl0(k = 9.0) annotation(
      Placement(visible = true, transformation(origin = {-62, 46}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant xl0(k = 10.0) annotation(
      Placement(visible = true, transformation(origin = {-62, 80}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.MultiSum multiSum(nu = 3) annotation(
      Placement(visible = true, transformation(origin = {40, 32}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
    Modelica.Blocks.Interfaces.RealInput t annotation(
      Placement(visible = true, transformation(origin = {-66, 6}, extent = {{-14, -14}, {14, 14}}, rotation = 0), iconTransformation(origin = {-120, 40}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    Modelica.Blocks.Math.Product product annotation(
      Placement(visible = true, transformation(origin = {-28, 32}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Interfaces.RealInput alt "The acceleration of the lead car in m/s^2" annotation(
      Placement(visible = true, transformation(origin = {-66, -28}, extent = {{-14, -14}, {14, 14}}, rotation = 0), iconTransformation(origin = {-120, -40}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    Modelica.Blocks.Interfaces.RealOutput xlt "Displacement of lead car in m" annotation(
      Placement(visible = true, transformation(origin = {72, 32}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(integrator1.y, integrator2.u) annotation(
      Line(points = {{-15, -28}, {-6, -28}}, color = {0, 0, 127}));
    connect(xl0.y, multiSum.u[1]) annotation(
      Line(points = {{-50, 80}, {34, 80}, {34, 32}}, color = {0, 0, 127}));
    connect(vl0.y, product.u1) annotation(
      Line(points = {{-51, 46}, {-41, 46}, {-41, 38}}, color = {0, 0, 127}));
    connect(t, product.u2) annotation(
      Line(points = {{-66, 6}, {-40, 6}, {-40, 26}}, color = {0, 0, 127}));
    connect(product.y, multiSum.u[2]) annotation(
      Line(points = {{-17, 32}, {34, 32}}, color = {0, 0, 127}));
    connect(integrator2.y, multiSum.u[3]) annotation(
      Line(points = {{17, -28}, {34, -28}, {34, 32}}, color = {0, 0, 127}));
    connect(alt, integrator1.u) annotation(
      Line(points = {{-66, -28}, {-38, -28}}, color = {0, 0, 127}));
    connect(multiSum.y, xlt) annotation(
      Line(points = {{48, 32}, {72, 32}}, color = {0, 0, 127}));
    annotation(
      Diagram);
  end CarAccToDisplacement;

  model PIDController
    parameter Modelica.Blocks.Interfaces.RealInput Kp annotation(
      Placement(visible = true, transformation(origin = {-122, 76}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, 78}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    parameter Modelica.Blocks.Interfaces.RealInput Ki annotation(
      Placement(visible = true, transformation(origin = {-120, 40}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, 28}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    parameter Modelica.Blocks.Interfaces.RealInput Kd annotation(
      Placement(visible = true, transformation(origin = {-120, 8}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, -18}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    parameter Modelica.Blocks.Interfaces.RealInput et annotation(
      Placement(visible = true, transformation(origin = {-120, -58}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, -86}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    Modelica.Blocks.Math.Product P annotation(
      Placement(visible = true, transformation(origin = {-50, 70}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Product I annotation(
      Placement(visible = true, transformation(origin = {18, 24}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.Product D annotation(
      Placement(visible = true, transformation(origin = {30, -70}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.MultiSum multiSum(nu = 3)  annotation(
      Placement(visible = true, transformation(origin = {62, 0}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput ut annotation(
      Placement(visible = true, transformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Continuous.Integrator etInt annotation(
      Placement(visible = true, transformation(origin = {-30, -8}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Continuous.Derivative det annotation(
      Placement(visible = true, transformation(origin = {-10, -60}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(Kp, P.u1) annotation(
      Line(points = {{-122, 76}, {-62, 76}}, color = {0, 170, 0}, thickness = 0.5));
    connect(et, P.u2) annotation(
      Line(points = {{-120, -58}, {-62, -58}, {-62, 64}}, color = {0, 170, 0}, thickness = 0.5));
    connect(P.y, multiSum.u[1]) annotation(
      Line(points = {{-39, 70}, {56, 70}, {56, 0}}, color = {0, 170, 0}, thickness = 0.5));
    connect(I.y, multiSum.u[2]) annotation(
      Line(points = {{29, 24}, {38.5, 24}, {38.5, 0}, {56, 0}}, color = {255, 170, 0}, thickness = 0.5));
    connect(D.y, multiSum.u[3]) annotation(
      Line(points = {{41, -70}, {56, -70}, {56, 0}}, color = {255, 0, 0}, thickness = 0.5));
    connect(et, etInt.u) annotation(
      Line(points = {{-120, -58}, {-42, -58}, {-42, -8}}, color = {255, 170, 0}, thickness = 0.5));
  connect(etInt.y, I.u2) annotation(
      Line(points = {{-18, -8}, {6, -8}, {6, 18}}, color = {255, 170, 0}, thickness = 0.5));
  connect(Ki, I.u1) annotation(
      Line(points = {{-120, 40}, {6, 40}, {6, 30}}, color = {255, 170, 0}, thickness = 0.5));
  connect(det.y, D.u1) annotation(
      Line(points = {{1, -60}, {18, -60}, {18, -64}}, color = {255, 0, 0}, thickness = 0.5));
  connect(et, det.u) annotation(
      Line(points = {{-120, -58}, {-42, -58}, {-42, -60}, {-22, -60}}, color = {255, 0, 0}, thickness = 0.5));
  connect(Kd, D.u2) annotation(
      Line(points = {{-120, 8}, {-54, 8}, {-54, -76}, {18, -76}}, color = {255, 0, 0}, thickness = 0.5));
  connect(multiSum.y, ut) annotation(
      Line(points = {{70, 0}, {110, 0}}, color = {0, 0, 127}, thickness = 0.75));
    annotation(
      Diagram);end PIDController;
  annotation(
    uses(Modelica(version = "4.0.0")));
end CarCruiseController;
