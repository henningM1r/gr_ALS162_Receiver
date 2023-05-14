
position_code_dict = {
    "00": ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "01": ( 0,+1,-1, 0, 0, 0,+1,-1, 0, 0, 0, 0, 0, 0, 0,-1,
            0,+2, 0,-2, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0, 0, 0),
    "02": (+1, 0,-2, 0,+2,-1,-1,+1,+1,-1,-1,+1, 0,+1, 0,-2,
           +1, 0, 0,+1,-2, 0,+1, 0,+1,-1,-1,+1, 0, 0, 0, 0),
    "03": (+1,-1, 0, 0,-1,+2, 0,-1,-1, 0,+2,-1,-1,+2, 0,-1,
           -1, 0,+2,-1,-1,+2, 0,-1,-1, 0,+1, 0, 0, 0, 0, 0),
    "04": (+1,-1,-1,+1,+1, 0,-1,-1,+1, 0,-1,+1, 0, 0, 0,+1,
            0,-2,+1,+1,-1,-1, 0,+1,+1,-1,-1,+1, 0, 0, 0, 0),
    "05": (+1,-1, 0,+1,-2, 0,+1, 0,+1, 0,-1,-1, 0,+2, 0,-1,
           -1, 0,+1,+1,-1,-1,+2,-1,-1,+1, 0, 0, 0, 0, 0, 0),
    "06": (+1,-1,-1,+1,+1, 0,-1,-1, 0,+1, 0,+1, 0,-2, 0,+2,
            0,-2,+1,+1,-1,-1, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0),
    "07": ( 0, 0, 0, 0,+1, 0,-1, 0,-1, 0,+1,+1, 0,-1,-1,+1,
            0, 0, 0,-1,+1,+1, 0,-1,-1, 0,+1, 0, 0, 0, 0, 0),
    "08": ( 0, 0,+1, 0,-1, 0, 0, 0, 0,-1, 0,+1, 0, 0, 0, 0,
            0, 0, 0, 0, 0,+1,-1,-1,+2,-1,-1,+1, 0, 0, 0, 0),
    "09": (+1,-1, 0,+1,-2,+1, 0,-1,+1,+1,-1,-1,+1,+1, 0,-1,
           -1, 0,+1,+1, 0,-1,-1, 0,+1, 0, 0, 0, 0, 0, 0, 0),
    "10": ( 0,+1, 0,-1,-1, 0,+1,+1, 0,-1,-1, 0,+2,-1,-1,+1,
           +1, 0,-1,-1,+1,+1,-2, 0,+1, 0, 0, 0, 0, 0, 0, 0),
    "11": ( 0,+1, 0,-1,-1,+1,+1,-2,+1, 0,-1,+1, 0,+1,-1, 0,
           +1,-1, 0,-1, 0,+2,-1, 0, 0,-1,+1, 0, 0, 0, 0, 0),
    "12": ( 0,+1, 0,-1, 0, 0,-1, 0,+2,-1,-1,+1,+1, 0,-1, 0,
           -1, 0,+1, 0, 0, 0, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0),
    "13": (+1,-1,-1,+2, 0,-1,-1, 0,+1,+1,-1, 0,+1,-2, 0,+1,
           +1,-1,-1,+1, 0, 0,+1, 0,-1,-1, 0,+1, 0, 0, 0, 0),
    "14": (+1, 0,-2,+1,+1,-2,+1, 0,-1,+2, 0,-2, 0,+1,+1,-1,
            0, 0,-1,+1,+1,-1,-1,+2, 0,-2, 0,+1, 0, 0, 0, 0),
    "15": ( 0,+1,-1,-1,+1,+1, 0,-1, 0,-1, 0,+2, 0,-1, 0,-1,
            0,+2,-1, 0,+1,-2, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0),
    "16": ( 0, 0,+1, 0,-2,+1,+1,-1, 0, 0,-1,+1, 0,-1,+1, 0,
            0, 0, 0,+1, 0,-2,+1,+1,-1,-1, 0,+1, 0, 0, 0, 0),
    "17": (+1, 0,-2, 0,+2,-1, 0,+1,-1, 0, 0,-1,+1,+1,-1, 0,
            0,-1,+1,+1,-2,+1,+1,-2, 0,+1, 0, 0, 0, 0, 0, 0),
    "18": (+1,-1, 0,+1,-2, 0,+2,-1, 0,+1,-1, 0, 0,-1, 0,+2,
            0,-1, 0,-1,+1, 0,-1,+1, 0, 0, 0, 0, 0, 0, 0, 0),
    "19": (+1, 0,-1, 0,-1, 0,+1,+1,-1, 0,+1,-2, 0,+2,-1,-1,
           +1, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "20": (+1,-1,-1,+1, 0,+1, 0,-2, 0,+1, 0,+1,-1, 0,+1,-2,
            0,+2,-1, 0,+1,-2, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0),
    "21": ( 0, 0,+1,-1,-1,+2,-1, 0,+1,-1, 0,-1, 0,+1,+1,-1,
            0,+1,-2,+1,+1,-1, 0,-1, 0,+1, 0, 0, 0, 0, 0, 0),
    "22": (+1,-1,-1,+2,-1, 0, 0,-1,+1, 0,+1, 0,-1,-1, 0,+2,
            0,-2, 0,+2, 0,-1, 0,-1,+1, 0,-1,+1, 0, 0, 0, 0),
    "23": ( 0, 0, 0, 0,+1, 0,-1, 0, 0, 0, 0, 0,-1,+1,+1,-2,
           +1, 0, 0,+1,-1,-1, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0),
    "24": ( 0, 0, 0, 0,+1,-1, 0, 0, 0,+1,-2,+1, 0,-1,+2, 0,
           -1,-1,+1,+1,-2,+1,+1,-1, 0,-1, 0,+1, 0, 0, 0, 0),
    "25": (+1, 0,-2, 0,+1, 0, 0, 0,+1, 0,-2, 0,+2, 0,-1, 0,
            0,-1,+1, 0, 0,+1,-2,+1,+1,-2, 0,+1, 0, 0, 0, 0),
    "26": (+1,-1, 0,+1,-2, 0,+2,-1, 0, 0, 0,+1,-2, 0,+2,-1,
           -1,+1, 0,+1,-1, 0,+1,-1,-1, 0,+1, 0, 0, 0, 0, 0),
    "27": (+1, 0,-2, 0,+1,+1,-1,-1,+1, 0,+1, 0,-2, 0,+2, 0,
           -1,-1,+1, 0,-1,+1,+1, 0,-2, 0,+1, 0, 0, 0, 0, 0),
    "28": (+1, 0,-1,-1,+1,+1,-2,+1, 0, 0,+1,-2, 0,+1, 0,+1,
           -1,-1,+2, 0,-1, 0,-1,+1,+1,-2, 0,+1, 0, 0, 0, 0),
    "29": ( 0,+1,-1,-1,+2, 0,-2, 0,+2, 0,-1, 0, 0, 0, 0,-1,
            0,+2,-1,-1,+1, 0,+1,-1,-1,+1, 0, 0, 0, 0, 0, 0),
    "30": (+1, 0,-2, 0,+2,-1,-1,+1, 0,+1, 0,-2, 0,+2, 0,-2,
           +1, 0, 0,+1,-2, 0,+1,+1, 0,-2, 0,+1, 0, 0, 0, 0),
    "31": ( 0,+1,-1, 0,+1,-2, 0,+1,+1, 0,-2,+1,+1,-1, 0,-1,
            0,+2, 0,-1,-1, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0, 0),
    "32": ( 0, 0,+1, 0,-2,+1,+1,-1,-1, 0,+1,+1, 0,-2, 0,+1,
            0, 0, 0,+1, 0,-2,+1, 0, 0, 0,-1,+1, 0, 0, 0, 0),
    "33": (+1, 0,-1, 0,-1,+1, 0,-1,+1, 0, 0,+1,-1, 0,+1,-1,
            0, 0, 0,-1, 0,+1,+1, 0,-2, 0,+1, 0, 0, 0, 0, 0),
    "34": ( 0, 0, 0, 0,+1, 0,-2, 0,+2,-1,-1,+2, 0,-1, 0, 0,
            0,-1,+1,+1,-1, 0, 0, 0,-1, 0,+1, 0, 0, 0, 0, 0),
    "35": ( 0, 0, 0,+1, 0,-1, 0, 0,-1, 0,+1, 0,+1, 0,-2,+1,
            0, 0,+1,-1, 0,-1, 0,+1,+1,-1,-1,+1, 0, 0, 0, 0),
    "36": (+1,-1, 0,+1,-1, 0, 0, 0,-1, 0,+2,-1, 0, 0, 0, 0,
           -1,+1, 0, 0, 0,+1,-1, 0, 0,-1,+1, 0, 0, 0, 0, 0),
    "37": (+1,-1,-1,+1, 0,+1,-1,-1,+1,+1,-1,-1,+1, 0,+1, 0,
           -2,+1, 0, 0,+1,-1,-1, 0,+1, 0, 0, 0, 0, 0, 0, 0),
    "38": ( 0,+1, 0,-2,+1,+1,-1, 0, 0, 0,-1, 0,+2,-1,-1,+1,
           +1, 0,-2, 0,+1,+1,-1,-1,+1, 0, 0, 0, 0, 0, 0, 0),
    "39": ( 0,+1, 0,-1,-1,+1,+1,-2, 0,+2,-1,-1,+1,+1,-1, 0,
           +1,-1, 0,-1, 0,+2,-1,-1,+1, 0, 0, 0, 0, 0, 0, 0),
    "40": ( 0,+1, 0,-1, 0, 0,-1, 0,+2,-1,-1,+1,+1,-1,-1,+1,
           +1, 0,-1, 0, 0, 0, 0, 0,-1, 0,+1, 0, 0, 0, 0, 0),
    "41": ( 0,+1, 0,-1,-1,+1,+1,-2,+1,+1,-1, 0,-1, 0,+2,-1,
           -1,+1, 0,+1, 0,-2,+1, 0,-1,+1, 0, 0, 0, 0, 0, 0),
    "42": (+1, 0,-1,-1,+1, 0,-1,+2, 0,-1,-1,+1,+1,-2, 0,+2,
           -1,-1,+2, 0,-2, 0,+2, 0,-1,-1, 0,+1, 0, 0, 0, 0),
    "43": (+1, 0,-1, 0,-1, 0,+2, 0,-2, 0,+2,-1, 0,+1,-1, 0,
            0, 0, 0,-1,+1, 0,-1,+1,+1,-1,-1,+1, 0, 0, 0, 0),
    "44": ( 0,+1,-1,-1,+2, 0,-2, 0,+2,-1, 0, 0, 0, 0, 0,+1,
           -2,+1, 0,-1,+1, 0, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0),
    "45": ( 0,+1, 0,-1, 0, 0,-1,+1,+1,-2,+1, 0,-1,+2, 0,-2,
            0,+1, 0, 0, 0, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0, 0),
    "46": (+1,-1,-1,+1,+1,-1,-1,+2, 0,-2, 0,+2,-1,-1,+1,+1,
            0,-2,+1,+1,-2, 0,+2, 0,-2, 0,+1, 0, 0, 0, 0, 0),
    "47": ( 0, 0,+1, 0,-2, 0,+1, 0,+1, 0,-2,+1, 0,-1,+2,-1,
            0, 1,-1,-1,+1,+1,-2,+1,+1,-2, 0,+1, 0, 0, 0, 0),
    "48": (+1, 0,-1,-1,+1, 0, 0,+1,-2,+1, 0,-1,+2, 0,-2,+1,
            0,-1,+2, 0,-2,+1, 0, 0, 1,-2, 0,+1, 0, 0, 0, 0),
    "49": (+1,-1,-1,+2,-1,-1,+2, 0,-2, 0,+2, 0,-1, 0, 0, 0,
           -1,+1,+1,-2,+1, 0,-1,+1,+1,-1,-1,+1, 0, 0, 0, 0),
    "50": ( 0, 0,+1, 0,-2, 0,+1, 0,+1,-1, 0, 0, 0, 0, 0,+1,
           -1, 0, 0,-1,+1,+1,-1, 0,-1, 0,+1, 0, 0, 0, 0, 0),
    "51": (+1,-1,-1,+1, 0, 0, 0,+1,-1, 0,+1,-1,-1, 0,+2, 0,
           -2,+1, 0, 0, 0,-1,+1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "52": (+1, 0,-1,-1,+1,+1,-1, 0, 0, 0, 0,-1,+1, 0,-1,+2,
           -1,-1,+2, 0,-1,-1,+1,+1,-1,-1, 0,+1, 0, 0, 0, 0),
    "53": ( 0,+1, 0,-1,-1, 0,+2, 0,-2, 0,+1,+1,-1,-1,+1,+1,
            0,-1, 0,-1,+1, 0,-1,+1,+1,-1,-1,+1, 0, 0, 0, 0),
    "54": (+1, 0,-1,-1, 0,+1,+1, 0,-2,+1, 0, 0, 0, 0, 0, 0,
            0,-1,+2,-1, 0, 0, 0, 0,-1,+1, 0, 0, 0, 0, 0, 0),
    "55": ( 0, 0,+1,-1, 0,+1,-2, 0,+2,-1,-1,+2,-1, 0, 0, 0,
            0,-1,+2, 0,-1, 0,-1,+1, 0,-1,+1, 0, 0, 0, 0, 0),
    "56": ( 0, 0, 0, 0, 0, 0, 0,+1,-1,-1,+2, 0,-2, 0,+1, 0,
            0,+1,-1, 0, 0,-1,+2,-1, 0, 0,-1,+1, 0, 0, 0, 0),
    "57": ( 0, 0,+1, 0,-2,+1, 0, 0,+1,-1,-1,+1, 0, 0,+1,-2,
           +1,+1,-1,-1, 0,+1, 0,+1, 0,-2, 0,+1, 0, 0, 0, 0),
    "58": (+1, 0,-1, 0,-1,+1, 0,-1,+2,-1,-1,+2,-1,-1,+2,-1,
            0,+1,-1,-1, 0,+1, 0, 0,+1,-1,-1,+1, 0, 0, 0, 0),
    "59": (+1, 0,-2, 0,+2, 0,-2, 0,+2, 0,-2, 0,+2, 0,-2, 0,
           +2, 0,-2, 0,+1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
}