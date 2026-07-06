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
                quoted = " ".join(f'"{str(x)}"' for x in entry)
                out_lines.append(f'store_texture [ {quoted} ]')
        else:
            # TEMP: switch out the TTC tunnel until loading this is fixed on the engine side
            if model_path == "phase_4/models/modules/safe_zone_tunnel_TT":
                model_path = "phase_6/models/modules/safe_zone_tunnel_DD"
            if model_path == "phase_3.5/models/modules/safe_zone_entrance_tunnel_TT":
                model_path = "phase_6/models/modules/safe_zone_entrance_tunnel_DD"
            # and this :( i gotta rebuild the engine with c++ changes but i hate that
            if model_path == 'phase_5/models/props/ttht_m_ara_ext_diner_entrance':
                model_path = 'phase_5/models/props/diner_entrance'

            # replace the occluder model with a visible one
            if model_path == "phase_3/models/misc/ttht_m_gen_util_occluder":
                model_path = "resources/ttht_m_gen_util_occluder"
            out_lines.append(f'model "{model_path}" [')

            for entry in entries:
                quoted = " ".join(f'"{str(x)}"' for x in entry)
                out_lines.append(f'\tstore_node [ {quoted} ]')

            out_lines.append("]\n")

    with open(outputFilePath, "w") as f:

        f.write("\n".join(out_lines))
