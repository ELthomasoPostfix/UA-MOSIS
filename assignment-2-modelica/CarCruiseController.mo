package CarCruiseController
    model PlantModel
      // Parameters
      parameter NewtonPerVolt A(start=0, fixed=true) "The forward gain from the control signal";
      parameter Modelica.Units.SI.Mass M(start=0, fixed=true) "The total mass of the plant";
      parameter Real b(start=0, fixed=true) "The plant's drag coefficient";
    
      // Variables
      Modelica.Units.SI.Position x(start=0) "The plant's displacement at time t";
      Modelica.Units.SI.Velocity v(start=0) "The plant's speed at time t";
      Modelica.Units.SI.Acceleration a(start=0) "The plant's acceleration at time t";
      Modelica.Units.SI.Voltage u(start=0, fixed=true) "The control signal at time t";
      //Modelica.Units.SI.Resistance
    equation
      der(x) = v;
      der(v) = a;
      a = M * (A * u - b * v * v);
  end PlantModel;

  type NewtonPerVolt = Real (final quantity="NewtonPerVolt", final unit="N/V");

  type DragResistance = Real (final quantity="DragResistance", final unit="kg/m");
end CarCruiseController;
