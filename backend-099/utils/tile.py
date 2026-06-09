def create_tiles(image, tile_size=640):

    h, w = image.shape[:2]

    tiles = []

    for y in range(0, h, tile_size):

        for x in range(0, w, tile_size):

            crop = image[
                y:y+tile_size,
                x:x+tile_size
            ]

            # supaya tile kosong/tidak valid tidak diproses
            if crop.shape[0] > 100 and crop.shape[1] > 100:

                tiles.append(
                    (
                        crop,
                        x,
                        y
                    )
                )

    return tiles