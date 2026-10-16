"""Render the final topology of one finished trial (researcher-side; pvbatch from ParaView 6.0.1).
Usage: pvbatch render_topology.py <final_analyze_output.exo> <out.png>
Same view as the E1/E2 preliminary renders: density (Topology) >= 0.5, colored by displacement magnitude."""
import sys
from paraview.simple import *
src, out = sys.argv[1], sys.argv[2]
r = ExodusIIReader(FileName=[src]); r.UpdatePipelineInformation()
pv = [n for n in r.GetProperty("PointVariablesInfo")[::2]]
top = next(n for n in pv if n.strip().lower() == "topology")
disp = next((n for n in pv if n.strip().lower().startswith("displacement")), None)
r.PointVariables = [top] + ([disp] if disp else [])
t = Threshold(Input=r); t.Scalars = ["POINTS", top]; t.LowerThreshold = 0.5; t.UpperThreshold = 1.0e9
v = GetActiveViewOrCreate("RenderView"); v.ViewSize = [1200, 700]; v.Background = [1, 1, 1]
try: v.UseColorPaletteForBackground = 0
except Exception: pass
v.OrientationAxesVisibility = 0
d = Show(t, v)
if disp:
    ColorBy(d, ("POINTS", disp, "Magnitude")); lut = GetColorTransferFunction(disp); lut.ApplyPreset("Viridis (matplotlib)", True)
    d.SetScalarBarVisibility(v, False)
o = Show(r, v); o.Representation = "Outline"; o.AmbientColor = [0.55, 0.55, 0.55]; o.DiffuseColor = [0.55, 0.55, 0.55]; o.ColorArrayName = ["POINTS", ""]
v.CameraPosition = [1, -1.2, 0.9]; v.CameraViewUp = [0, 0, 1]; v.ResetCamera(); v.CameraFocalPoint = list(v.CameraFocalPoint)
ResetCamera(v); Render(v)
SaveScreenshot(out, v, ImageResolution=[1200, 700])
print("rendered", out)
