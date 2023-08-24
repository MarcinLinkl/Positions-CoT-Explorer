positions_types_futures_only = {
    "comm_positions": "Commercial",
    "noncomm_positions": "Non-Commercial",
    "nonrept_positions": "Non-Reportable",
    "tot_rept_positions": "Total Reportable",
}
options_sides = [
    "net",
    "long",
    "short",
]
print()

options = [{"label": i.capitalize(), "value": i} for i in options_sides]
value = [options_sides[0]]
print(options)
print(value)
