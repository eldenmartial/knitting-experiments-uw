from generate_swatches import generate

stitch_number = 7

# 105: 25/20
# 106: 26/20
# 107: 27/20
# 108: 28/20
# 109: 29/20
# 110: 30/25
# 111: 31/25
# 112: 32/25
# 113: 33/26
# 114: 34/21
# 115: 35/24
# 116: 36/25
# 117: 37/30
# 118: 38/30
# 119: 39/30
# 120: 40/35
#      65/40

out_fp = "knitout-files/nat-modified.k"

# pattern, dimensions (wxh), gauge, extensions
swatches = [
    ["jersey tube", [10, 476], 1, {"stitchNumber": stitch_number}],  # x-knit
    ["jersey", [18, 530], 1, {"stitchNumber": stitch_number}],  # edge knit
    ["jersey", [114, 82], 1, {"stitchNumber": stitch_number}],  # knit
    ["tuckStitch", [114, 82], 1, {"stitchNumber": stitch_number}],  # tuck
    ["rib_fb", [114, 82], 1, {"stitchNumber": stitch_number}],  # diagonal_1
    ["jersey", [114, 82], 2, {"stitchNumber": stitch_number}],  # miss
    ["rib_fb", [114, 82], 2, {"stitchNumber": stitch_number}],  # diagonal_2
]

generate(swatches, out_fp)
