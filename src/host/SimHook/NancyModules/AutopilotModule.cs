using Nancy;
using Nancy.Extensions;

namespace SimHook.NancyModules
{
    public class AutopilotModule : NancyModule
    {
        public AutopilotModule() : base("/autopilot")
        {
            Get["/heading"] = _ => AutopilotState.Heading.ToString();
            Post["/heading"] = _ =>
            {
                var str = Request.Body.AsString();
                var heading = int.Parse(str);
                AutopilotState.Heading = heading;
                AutopilotState.HeadingStale = true;
                
                return "Ok";
            };

            Get["/enabled"] = _ => AutopilotState.Enabled.ToString();
            Post["/enabled"] = _ =>
            {
                var str = Request.Body.AsString();
                var enabled = bool.Parse(str);
                
                if (AutopilotState.Enabled == enabled) 
                    return "Ok";

                AutopilotState.Enabled = enabled;
                AutopilotState.EnabledStale = true;

                return "Ok";
            };

            Get["/headingHold"] = _ => AutopilotState.HeadingHold.ToString();
            Post["/headingHold"] = _ =>
            {
                var str = Request.Body.AsString();
                var headingHold = bool.Parse(str);

                if (AutopilotState.HeadingHold == headingHold)
                    return "Ok";

                AutopilotState.HeadingHold = headingHold;
                AutopilotState.HeadingHoldStale = true;

                return "Ok";
            };
        }
    }
}