# FlightDeck

_Control FSX or P3D with your Raspberry PI!_

A pet project to create various flight deck control systems using custom electronics controlled by a Raspberry PI + Arduinos.

## Contents

- 1x C# flight deck host application (Framework 4.7)
  - Uses SimConnect to connect to the simulation and provide (currently) a RESTful API for reading and writing updates.
- 1x Raspberry PI 2 (or greater) python device controller
  - The project currently uses one Raspberry PI and various breadboards on which the inputs and displays are mounted.
- 1x Arduino
  - Switch panel interface
- Assorted wiring diagrams and pictures
  - Photographs and wiring diagrams!

## Roadmap

- Bendix King C172 radio stack
- Landing gear (with feedback LEDs)
- Interior and exterior lights
- Parking brake

## Useful links

http://www.prepar3d.com/SDKv3/LearningCenter/utilities/variables/event_ids.html
http://www.prepar3d.com/SDKv3/LearningCenter/utilities/variables/simulation_variables.html#Aircraft%20Autopilot%20Variables
https://docs.microsoft.com/en-us/previous-versions/microsoft-esp/cc526983(v%3dmsdn.10)
