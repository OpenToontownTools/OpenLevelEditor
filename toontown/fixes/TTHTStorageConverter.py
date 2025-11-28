# TTHTStorageConverter
# Created by drewc Nov 27, 2025
import json
from direct.stdpy.file import open


def convertHostileTakeoverStorage(inputFilePath, outputFilePath):
    """
    converts TTHT's json
    :param inputFilePath:
    :param outputFilePath:
    :return:
    """
    with open(inputFilePath, "r") as f:
        data = json.load(f)

    out_lines = []

    for model_path, entries in data.items():

        if model_path == 'textures':
            for entry in entries:
                quoted = "".join(f'"{str(x)}"' for x in entry)
                out_lines.append(f'\tstore_texture [ {quoted} ]')
        else:
            # TEMP: switch out the TTC tunnel until loading this is fixed on the engine side
            if model_path == "phase_4/models/modules/safe_zone_tunnel_TT":
                model_path = "phase_6/models/modules/safe_zone_tunnel_DD"
            if model_path == "phase_3.5/models/modules/safe_zone_entrance_tunnel_TT":
                model_path = "phase_6/models/modules/safe_zone_entrance_tunnel_DD"
            out_lines.append(f'model "{model_path}" [')

            for entry in entries:
                quoted = " ".join(f'"{str(x)}"' for x in entry)
                out_lines.append(f'\tstore_node [ {quoted} ]')

            out_lines.append("]\n")

    with open(outputFilePath, "w") as f:

        f.write("\n".join(out_lines))
