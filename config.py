hostname = "ctrlr0"

TCPports = {
    0: {
        'name': 'LopOnGnd',
        'httpReq': 'http://switch0.lan/port/1'
    },
    1: {
        'name': 'MagLp NS',
        'httpReq': 'http://switch0.lan/port/2'
    },
    2: {
        'name': 'MagLp EW',
        'httpReq': 'http://switch0.lan/port/3'
    },
    3: {
        'name': 'MagLp PH',
        'httpReq': 'http://switch0.lan/port/4'
    },
    4: {
        'name': 'All',
        'httpReq': 'http://switch0.lan/port/5'
    },
}

LORAports = {
    0: {
        'name': 'TLopOnGnd',
        'LoRaReq': 'sw0/1'
    },
    1: {
        'name': 'TMagLp NS',
        'LoRaReq': 'sw0/1'
    },
}