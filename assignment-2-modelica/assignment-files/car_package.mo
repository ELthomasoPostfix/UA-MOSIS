package car_package
  block mech_car
    import Modelica.Blocks.Types.Init;
    extends Modelica.Blocks.Interfaces.SISO;
    // Components
    final Modelica.Mechanics.Translational.Components.Vehicle vehicle(m = 8000, J = 0.01, R(displayUnit = "mm") = 0.24765, s(start = 0), v(start = 0), A = 2, Cd = 0.31) annotation(
       Placement(transformation(origin = {16, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Mechanics.Translational.Sensors.PositionSensor positionSensor annotation(
       Placement(transformation(origin = {48, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Mechanics.Rotational.Sources.Torque torque annotation(
       Placement(transformation(origin = {-14, 0}, extent = {{-10, -10}, {10, 10}})));
    final Modelica.Blocks.Math.Gain gain(k = 60) annotation(
       Placement(transformation(origin = {-48, 0}, extent = {{-10, -10}, {10, 10}})));
  // Connections
     Modelica.Mechanics.Translational.Sensors.SpeedSensor speedSensor annotation(
       Placement(transformation(origin = {48, -24}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Translational.Sensors.AccSensor accSensor annotation(
       Placement(transformation(origin = {48, -44}, extent = {{-10, -10}, {10, 10}})));
   equation
    connect(vehicle.flangeT, positionSensor.flange) annotation(
       Line(points = {{26, 0}, {38, 0}}, color = {0, 127, 0}));
    connect(positionSensor.s, y) annotation(
       Line(points = {{59, 0}, {110, 0}}, color = {0, 0, 127}));
    connect(torque.flange, vehicle.flangeR) annotation(
       Line(points = {{-4, 0}, {6, 0}}));
    connect(gain.y, torque.tau) annotation(
       Line(points = {{-37, 0}, {-27, 0}}, color = {0, 0, 127}));
    connect(gain.u, u) annotation(
       Line(points = {{-60, 0}, {-120, 0}}, color = {0, 0, 127}));
  connect(speedSensor.flange, vehicle.flangeT) annotation(
       Line(points = {{38, -24}, {32, -24}, {32, 0}, {26, 0}}, color = {0, 127, 0}));
  connect(accSensor.flange, vehicle.flangeT) annotation(
       Line(points = {{38, -44}, {32, -44}, {32, 0}, {26, 0}}, color = {0, 127, 0}));
  end mech_car;
end car_package;
