namespace SimHook
{
    public static class AutopilotState
    {
        public static int Heading;
        public static bool HeadingStale { get; set; }
        public static bool Enabled { get; set; }
        public static bool EnabledStale { get; set; }
    }
}