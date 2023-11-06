package CarCruiseController
  model PlantModel
    // Parameters
    parameter NewtonPerVolt A=60 "The forward gain (N/V) from the control signal";
    parameter Modelica.Units.SI.Mass M=1500 "The total mass (kg) of the plant";
    parameter DragResistance b=0.86 "The plant's drag coefficient(kg/m)";
  
    // Variables
    Modelica.Units.SI.Position x(start=0) "The plant's displacement (m) at time t";
    Modelica.Units.SI.Velocity v(start=Modelica.Units.Conversions.from_kmh(108)) "The plant's velocity (m/s) at time t";
    Modelica.Units.SI.Acceleration a "The plant's acceleration (m/s^2) at time t";
    Modelica.Units.SI.Voltage u(start=0) "The control signal (V) at time t";
  
  equation
    u = 1;
    der(x) = v "Relation between displacement and velocity";
    der(v) = a "Relation between velocity and acceleration";
    M * der(v) = (A * u - b * v * v) "The plant's equation of motion (N)";
  
  end PlantModel;

  type NewtonPerVolt = Real (final quantity="NewtonPerVolt", final unit="N/V");

  type DragResistance = Real (final quantity="DragResistance", final unit="kg/m");
end CarCruiseController;
