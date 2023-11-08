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
    car_package.mech_car Plant annotation(
      Placement(visible = true, transformation(origin = {50, 56}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Tables.CombiTable1Ds LeadCarMotion(extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint, smoothness = Modelica.Blocks.Types.Smoothness.ConstantSegments, table = [0, 1.75; 20, -0.75; 40, 0.5; 60, -3.25; 70, 0]) annotation(
      Placement(visible = true, transformation(origin = {-16, -8}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.ContinuousClock continuousClock annotation(
      Placement(visible = true, transformation(origin = {-46, 16}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  CarCruiseController.CarAccToDisplacement carAccToDisplacement annotation(
      Placement(visible = true, transformation(origin = {16, -4}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
  connect(continuousClock.y, LeadCarMotion.u) annotation(
      Line(points = {{-35, 16}, {-35, -8}, {-28, -8}}, color = {0, 0, 127}));
  connect(continuousClock.y, carAccToDisplacement.CurrentTime) annotation(
      Line(points = {{-35, 16}, {3, 16}, {3, 0}}, color = {0, 0, 127}));
  connect(LeadCarMotion.y[1], carAccToDisplacement.Acceleration) annotation(
      Line(points = {{-5, -8}, {3, -8}}, color = {0, 0, 127}));
  end CarCruiseController;

  block CarAccToDisplacement
    Modelica.Blocks.Continuous.Integrator integrator2(initType = Modelica.Blocks.Types.Init.InitialOutput, y_start = 0) annotation(
      Placement(visible = true, transformation(origin = {6, -28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Integrator integrator1(y_start = 0) annotation(
      Placement(visible = true, transformation(origin = {-26, -28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant InitialVelocity(k = 9.0) annotation(
      Placement(visible = true, transformation(origin = {-62, 46}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant InitialPosition(k = 10.0) annotation(
      Placement(visible = true, transformation(origin = {-62, 80}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Math.MultiSum multiSum(nu = 3)  annotation(
      Placement(visible = true, transformation(origin = {40, 32}, extent = {{-6, -6}, {6, 6}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput CurrentTime annotation(
      Placement(visible = true, transformation(origin = {-66, 6}, extent = {{-14, -14}, {14, 14}}, rotation = 0), iconTransformation(origin = {-120, 40}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Math.Product product annotation(
      Placement(visible = true, transformation(origin = {-28, 32}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput Acceleration "The acceleration of the lead car in m/s^2" annotation(
      Placement(visible = true, transformation(origin = {-66, -28}, extent = {{-14, -14}, {14, 14}}, rotation = 0), iconTransformation(origin = {-120, -40}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput Displacement "Displacement of lead car in m" annotation(
      Placement(visible = true, transformation(origin = {72, 32}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(integrator1.y, integrator2.u) annotation(
      Line(points = {{-15, -28}, {-6, -28}}, color = {0, 0, 127}));
  connect(InitialPosition.y, multiSum.u[1]) annotation(
      Line(points = {{-50, 80}, {34, 80}, {34, 32}}, color = {0, 0, 127}));
  connect(InitialVelocity.y, product.u1) annotation(
      Line(points = {{-51, 46}, {-41, 46}, {-41, 38}}, color = {0, 0, 127}));
  connect(CurrentTime, product.u2) annotation(
      Line(points = {{-66, 6}, {-40, 6}, {-40, 26}}, color = {0, 0, 127}));
  connect(product.y, multiSum.u[2]) annotation(
      Line(points = {{-17, 32}, {34, 32}}, color = {0, 0, 127}));
  connect(integrator2.y, multiSum.u[3]) annotation(
      Line(points = {{17, -28}, {34, -28}, {34, 32}}, color = {0, 0, 127}));
  connect(Acceleration, integrator1.u) annotation(
      Line(points = {{-66, -28}, {-38, -28}}, color = {0, 0, 127}));
  connect(multiSum.y, Displacement) annotation(
      Line(points = {{48, 32}, {72, 32}}, color = {0, 0, 127}));
  end CarAccToDisplacement;
  annotation(
    uses(Modelica(version = "4.0.0")));
end CarCruiseController;
