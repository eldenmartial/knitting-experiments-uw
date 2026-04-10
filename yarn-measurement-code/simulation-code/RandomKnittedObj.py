def knitted_object(rows, cols, tube):
    swatch = {key:0 for key in ["knit", "edge-knit", "tuck", "miss", "gap", "xknit", "d1", "d2"]}
    if (not tube):
        swatch["edge-knit"] = (rows-1)*2
        swatch["tuck"] = np.random.randint(0,np.ceil(cols/2))
        remaining_spots = rows*cols - swatch["edge-knit"] - swatch["tuck"]
        swatch["knit"] = np.random.randint(0, remaining_spots)
        swatch["miss"] = remaining_spots - swatch["knit"]
        swatch["gap"] = (cols-1)*rows
    else:
        pass
    return swatch