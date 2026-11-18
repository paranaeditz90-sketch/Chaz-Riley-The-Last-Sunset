"""Gera uma folha de pré-visualização ampliada. Uso: preview.py <chaz|riley|terceiro|all> <saida.png>"""
import sys
from PIL import Image
from pixelkit import *
import characters as C


def frames_for(spec):
    return [C.render(spec, p).image() for p in C.IDLE + C.WALK]


def main():
    which, out = sys.argv[1], sys.argv[2]
    specs = {"chaz": C.CHAZ}
    for n in ("RILEY", "TERCEIRO"):
        if hasattr(C, n):
            specs[n.lower()] = getattr(C, n)
    names = list(specs) if which == "all" else [which]
    Z = 8
    rows = []
    for n in names:
        fr = frames_for(specs[n])
        row = Image.new("RGBA", (len(fr) * (W * Z + 6), H * Z + 6), (34, 30, 48, 255))
        for i, f in enumerate(fr):
            row.alpha_composite(upscale(f, Z), (i * (W * Z + 6) + 3, 3))
        # linha 1x e 3x pra ver o tamanho real
        small = Image.new("RGBA", row.size, (34, 30, 48, 255))
        for i, f in enumerate(fr):
            small.alpha_composite(f, (i * (W * Z + 6) + 3, 3))
            small.alpha_composite(upscale(f, 3), (i * (W * Z + 6) + 60, 3))
        rows.append(row)
        rows.append(small.crop((0, 0, small.width, 3 * H + 6)))
    sheet = Image.new("RGBA", (rows[0].width, sum(r.height for r in rows)), (34, 30, 48, 255))
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y)); y += r.height
    sheet.save(out)
    print(sheet.size)


main()
