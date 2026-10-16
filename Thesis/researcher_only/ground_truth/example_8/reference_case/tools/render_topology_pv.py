"""Render the final optimized topology from an analyze Exodus file with ParaView (pvbatch).
Solid material = nodal design density 'Topology' >= 0.5 (clip, undeformed), colored by displacement
magnitude, as in the Examples Manual figures.  With --mirror-z=C a second panel shows the design
reflected across z = C.  With --compare=<other.exo> a second (and third) panel shows the other file.
Usage: pvbatch render_topology_pv.py <final.exo> <out.png> "<title>" ["<title line 2>"] [--mirror-z=0.5] [--compare=other.exo --compare-title="..."]
"""
import sys
from paraview.simple import (Clip, ColorBy, CreateView, ExodusIIReader, GetColorTransferFunction, GetScalarBar,
                             Outline, Transform, AssignViewToLayout, CreateLayout, SaveScreenshot, Show, Text)
exo, png, title = sys.argv[1:4]
extra = [x for x in sys.argv[4:] if not x.startswith("--")]
if extra:
    title += "\n" + extra[0]
mirror = next((float(x.split("=", 1)[1]) for x in sys.argv if x.startswith("--mirror-z=")), None)
compare = next((x.split("=", 1)[1] for x in sys.argv if x.startswith("--compare=")), None)
ctitle = next((x.split("=", 1)[1] for x in sys.argv if x.startswith("--compare-title=")), "comparison")


def load(path):
    r = ExodusIIReader(FileName=[path])
    disp = next(v for v in r.PointVariables if v.strip() == "displacement")
    r.PointVariables = ["Topology", disp]
    r.ApplyDisplacements = 0
    s = Clip(Input=r, ClipType="Scalar", Scalars=["POINTS", "Topology"], Value=0.5, Invert=0)
    r.UpdatePipeline()
    return r, s, disp


reader, solid, DISP = load(exo)
layout = CreateLayout("final")


def mirrored(src):
    t = Transform(Input=src)
    t.Transform.Scale = [1, 1, -1]
    t.Transform.Translate = [0, 0, 2 * mirror]
    return t


panels = [([solid], [reader], "as computed" if (mirror is not None or compare) else None)]
if mirror is not None:
    panels.append(([solid, mirrored(solid)], [reader, mirrored(reader)], f"mirrored across z = {mirror} (full design)"))
if compare:
    r2, s2, _ = load(compare)
    panels.append(([s2], [r2], ctitle))
lut = GetColorTransferFunction(DISP)
lut.VectorMode = "Magnitude"
lut.ApplyPreset("Cool to Warm", True)
umax = reader.PointData[DISP].GetRange(-1)[1]
for k, (bodies, domains, label) in enumerate(panels):
    view = CreateView("RenderView")
    AssignViewToLayout(view=view, layout=layout, hint=0)
    view.OrientationAxesVisibility = 1
    view.Background = [1, 1, 1]
    view.UseColorPaletteForBackground = 0
    for d in domains:
        o = Show(Outline(Input=d), view)
        o.AmbientColor = o.DiffuseColor = [0.6, 0.6, 0.6]
    for b in bodies:
        s = Show(b, view)
        ColorBy(s, ("POINTS", DISP, "Magnitude"))
    lut.RescaleTransferFunction(0.0, umax)
    lut.AutomaticRescaleRangeMode = "Never"
    bar = GetScalarBar(lut, view)
    bar.Title = "Displacement magnitude"
    bar.ComponentTitle = ""
    bar.TitleColor = bar.LabelColor = [0, 0, 0]
    bar.RangeLabelFormat = "%-#.2e"
    bar.WindowLocation = "Any Location"
    bar.Position = [0.80, 0.06]
    bar.ScalarBarLength = 0.4
    bar.TitleFontSize = bar.LabelFontSize = 12
    s.SetScalarBarVisibility(view, k == len(panels) - 1)
    t = Show(Text(Text=title + (f"\n{label}" if label else "")), view)
    t.Color = [0, 0, 0]
    t.FontSize = 11
    t.WindowLocation = "Upper Left Corner"
    view.ResetCamera()
    cam = view.GetActiveCamera()
    fp = cam.GetFocalPoint()
    zc = mirror if (mirror is not None and k == 1) else fp[2]
    cam.SetFocalPoint(fp[0], fp[1], zc)
    cam.SetPosition(fp[0] - 1.6, fp[1] + 1.4, zc + 4.2)
    cam.SetViewUp(0, 1, 0)
    view.ResetCamera()
SaveScreenshot(png, layout, ImageResolution=[800 * len(panels), 800], TransparentBackground=0)
print("wrote", png)
