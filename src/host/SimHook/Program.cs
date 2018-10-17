using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;
using Microsoft.FlightSimulator.SimConnect;
using Nancy.Hosting.Self;
using SimHook.SimData;

namespace SimHook
{
    public static class Program
    {
        private static bool _running = true;
        private static SimConnect _simConnect;

        private const int WmUserSimconnect = 0x402;
        
        static void Main(string[] args)
        {
            LogInfo("Connecting to sim...");

            try
            {
                _simConnect = new SimConnect("FlightDeck", 
                    Process.GetCurrentProcess().Handle,
                    WmUserSimconnect,
                    null, 
                    0);
            }
            catch (COMException)
            {
                LogError("Failed to connect to sim. Is FSX definitely running?");
                return;
            }
            
            _simConnect.OnRecvOpen += SimConnectRecvOpen;
            _simConnect.OnRecvSimobjectData += SimConnectRecvObjectData;
            _simConnect.OnRecvException += SimConnectOnOnRecvException;
            _simConnect.OnRecvEvent += SimConnectOnOnRecvEvent;

            //"GPS COURSE TO STEER"
            //"GPS WP NEXT LON"
            //HSI BEARING
            //"AUTOPILOT HEADING LOCK DIR"
            //HSI BEARING VALID
            //"HSI BEARING"
            
            // "HEADING INDICATOR", "Degrees
            
            _simConnect.AddToDataDefinition(DataDefinition.AutopilotDefinition,
                "AUTOPILOT HEADING LOCK DIR", "Degrees", SIMCONNECT_DATATYPE.INT32, 0.001f, SimConnect.SIMCONNECT_UNUSED);
            
            _simConnect.AddToDataDefinition(DataDefinition.AutopilotDefinition,
                "AUTOPILOT MASTER", "Bool", SIMCONNECT_DATATYPE.INT32, 0.001f, SimConnect.SIMCONNECT_UNUSED);
            
            _simConnect.RequestDataOnSimObject(DataRequest.AutopilotData, DataDefinition.AutopilotDefinition,
                SimConnect.SIMCONNECT_OBJECT_ID_USER, SIMCONNECT_PERIOD.SECOND, 0, 0, 0, 0);
            
            _simConnect.RegisterDataDefineStruct<AutopilotData>(DataDefinition.AutopilotDefinition);

            _simConnect.MapClientEventToSimEvent(InputEvent.AutopilotSetHeading, "HEADING_BUG_SET");
            _simConnect.MapClientEventToSimEvent(InputEvent.AutopilotDisable, "AUTOPILOT_OFF");
            _simConnect.MapClientEventToSimEvent(InputEvent.AutopilotEnable, "AUTOPILOT_ON");
            
            _simConnect.AddClientEventToNotificationGroup(Groups.DefaultGroup, InputEvent.AutopilotSetHeading, false);
                                    
            var hostConfigs = new HostConfiguration
            {
                UrlReservations = new UrlReservations
                {
                    CreateAutomatically = true
                },
                RewriteLocalhost = true
            };
            
            using (var host = new NancyHost(hostConfigs, new Uri("http://192.168.1.104:8558")))
            {
                host.Start();
                Console.WriteLine("Running on http://192.168.1.104:8558");
                
                while (_running)
                {
                    _simConnect.ReceiveMessage();
                    Thread.Sleep(250);

                    UpdateAutopilotHeading();
                }
            }
        }

        private static void UpdateAutopilotHeading()
        {
            if (AutopilotState.HeadingStale)
            {
                AutopilotState.HeadingStale = false;
                _simConnect.TransmitClientEvent(
                    SimConnect.SIMCONNECT_OBJECT_ID_USER,
                    InputEvent.AutopilotSetHeading,
                    (uint) AutopilotState.Heading,
                    Groups.DefaultGroup,
                    0);
            }

            if (AutopilotState.EnabledStale)
            {
                AutopilotState.EnabledStale = false;

                if (AutopilotState.Enabled)
                {
                    _simConnect.TransmitClientEvent(
                        SimConnect.SIMCONNECT_OBJECT_ID_USER,
                        InputEvent.AutopilotEnable,
                        0,
                        Groups.DefaultGroup,
                        0);
                }
                else
                {
                    _simConnect.TransmitClientEvent(
                        SimConnect.SIMCONNECT_OBJECT_ID_USER,
                        InputEvent.AutopilotDisable,
                        0,
                        Groups.DefaultGroup,
                        0);
                }
            }
        }

        private static void SimConnectOnOnRecvEvent(SimConnect sender, SIMCONNECT_RECV_EVENT data)
        {
            LogInfo($"Event: {data.dwData}");
        }

        private static void SimConnectOnOnRecvException(SimConnect sender, SIMCONNECT_RECV_EXCEPTION data)
        {
            LogError($"Error: {data.dwException}");
        }

        private static void SimConnectRecvObjectData(SimConnect sender, SIMCONNECT_RECV_SIMOBJECT_DATA data)
        {
            var d = data.dwData[0];

            switch (d)
            {
                case AutopilotData apData:
                    AutopilotState.Heading = apData.Heading;
                    AutopilotState.Enabled = apData.Enabled;
                    LogInfo($"Heading: {apData.Heading}, Enabled:{apData.Enabled}");
                    break;
            }
        }

        private static void LogError(string message)
        {
            var color = Console.ForegroundColor;
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine(message);
            Console.ForegroundColor = color;
        }

        private static void LogInfo(string message)
        {
            var color = Console.ForegroundColor;
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine(message);
            Console.ForegroundColor = color;
        }

        private static void LogSuccess(string message)
        {
            var color = Console.ForegroundColor;
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine(message);
            Console.ForegroundColor = color;
        }

        private static void SimConnectRecvOpen(SimConnect sender, SIMCONNECT_RECV_OPEN data)
        {
            LogSuccess("Recv open");
        }
    }
}