import folium
import random

def visualization(signs_group):
    sign_map = folium.Map(location=[signs_group[0].x, signs_group[0].y],
                          zoom_start=15,
                          )
    for sign in signs_group:
        color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        size = len(sign.x_arr)
        for i in range(size):
            x = sign.x_arr[i]
            y = sign.y_arr[i]
            folium.PolyLine([(x, y), (sign.x, sign.y)],
                            tooltip=sign.files[i] + "\n" + sign.class_name,
                            color=color,
                            weight=1,
                            opacity=0.8).add_to(sign_map)
        folium.CircleMarker(location=[sign.x, sign.y], radius=1,
                            popup=sign.file + "\n" + sign.class_name + '\n' + '\n'.join(sign.files),
                            color=color,
                            ).add_to(sign_map)

    sign_map.save("C:/Users/user/Documents/IT/ADGRS/project/input_file_for_test/output_file/test_final.html")