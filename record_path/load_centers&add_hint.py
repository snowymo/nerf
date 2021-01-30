def load_centers(data_desc_file):
    with open(data_desc_file, 'r', encoding='utf-8') as file:
        data_desc = json.loads(file.read())
        return data_desc['gaze_centers']


hint = cv2.imread('fovea_hint.png', cv2.IMREAD_UNCHANGED)


def add_hint(img, center):
    fovea_origin = (
        int(center[0]) + 1440 // 2 - hint.shape[1] // 2,
        int(center[1]) + 1600 // 2 - hint.shape[0] // 2
    )
    fovea_region = (
        slice(fovea_origin[1], fovea_origin[1] + hint.shape[0]),
        slice(fovea_origin[0], fovea_origin[0] + hint.shape[1]),
        ...
    )
    img[fovea_region] = (img[fovea_region] * (1 - hint[..., 3:] / 255.0) +
                         hint[..., :3] * (hint[..., 3:] / 255.0)).astype(numpy.uint8)