using System.Runtime.InteropServices;

namespace SimHook.SimData
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi, Pack = 1)]
    public struct AutopilotData
    {
        public int Heading;
        public bool Enabled { get; set; }
    }
}