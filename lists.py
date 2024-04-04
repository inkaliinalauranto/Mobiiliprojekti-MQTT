lights_ids = [
    "68_50_1_Value_65537",
    "68_50_2_Value_65537",
    "71_50_1_Value_65537",
    "71_50_2_Value_65537",
    "103_50_1_Value_65537",
    "106_50_1_Value_65537",
    "110_50_1_Value_65537",
    "112_50_1_Value_65537",
    "116_50_1_Value_65537",
    "120_50_1_Value_65537",
    "122_50_1_Value_65537",
    "122_50_2_Value_65537",
    "141_50_1_Value_65537",
    "141_50_2_Value_65537",
    "142_50_1_Value_65537",
    "142_50_2_Value_65537"
]

outlet_ids = [
    "53_50_0_Value_65537",
    "54_50_0_Value_65537",
    "148_50_0_Value_65537",
    "150_50_0_Value_65537",
    "151_50_0_Value_65537",
    "152_50_0_Value_65537",
    "153_50_0_Value_65537",
    "154_50_0_Value_65537",
    "155_50_0_Value_65537",
    "156_50_0_Value_65537",
    "157_50_0_Value_65537",
    "158_50_0_Value_65537",
    "159_50_0_Value_65537",
    "161_50_0_Value_65537",
    "162_50_0_Value_65537",
    "163_50_0_Value_65537",
    "164_50_0_Value_65537",
    "166_50_0_Value_65537",
    "167_50_0_Value_65537",
    "168_50_0_Value_65537",
    "170_50_0_Value_65537",
    "171_50_0_Value_65537",
    "172_50_0_Value_65537",
    "173_50_0_Value_65537",
    "175_50_0_Value_65537",
    "176_50_0_Value_65537",
    "177_50_0_Value_65537"
]

heater_ids = [
    "47_50_1_Value_65537",      # Floorheating 1
    "47_50_2_Value_65537"       # Floorheating 2
]

total_production_ids = [
    "produced_energy",          # Wind
    "yieldtoday"                # Solar
]

# Ei laiteta näitä total_consumptions_fact tauluun,
# koska näiden yhteenlaskettu summa on se mitä koko coolboxi käyttää.
# Tällä hetkellä lasketaan kaikki muut kulutukset yhteen.
# Summa heittää jonkun verran, koska sitä virtaa menee muuallekkin kuin valoihin, lämmitykseen, pistorasioihin
# Voidaan tehdä tarvittaessa oma fact_taulu näille
total_consumption_ids = [
    "189_50_1_Value_65537",     # TB_3Phase
    "energy"                    # Inverter
]

temperature_ids = [
    "190_49_0_AirTemperature",  # Outdoors (mast)
    "144_49_0_AirTemperature",  # Indoors TB
    "35_49_0_AirTemperature",   # Indoors WC
    "145_49_0_AirTemperature",  # Indoors
    "193_49_0_AirTemperature"   # Floor
]

battery_ids = [
    "soc"
]
