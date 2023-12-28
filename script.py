import config
import time
from pybit.unified_trading import HTTP

symbol = ''  # Puedes ajustar el símbolo según tus necesidades
stop_loss = 0  # Valor en USDT
estado = False
capital = 0

session = HTTP(
    testnet=False,
    api_key=config.api_key,
    api_secret=config.api_secret,
)


def qty_step(symbol, price):
    step = session.get_instruments_info(category="linear", symbol=symbol)
    ticksize = float(step['result']['list'][0]['priceFilter']['tickSize'])
    operacion = int(price / ticksize) * ticksize
    result = operacion

    return result


def establecer_stop_loss(symbol, price):
    price = qty_step(symbol, price)

    # PONER ORDEN STOP LOSS
    order = session.set_trading_stop(
        category="linear",
        symbol=symbol,
        stopLoss=price,
        slTriggerB="IndexPrice",
        slOrderType="Market",
        positionIdx=0,
    )

    return order


# Lógica del bot (ejemplo simple: compra y venta cada 60 segundos)
while True:
    try:
        if estado:
            # Posiciones Abiertas
            posiciones = session.get_positions(category="inverse", symbol=symbol)
            if float(posiciones['result']['list'][0]['size']) != 0:
                precio_de_entrada = float(posiciones['result']['list'][0]['avgPrice'])
                USDT = float(posiciones['result']['list'][0]['positionValue'])
                porcentaje = (stop_loss * 100) / USDT
                aumento = precio_de_entrada * (porcentaje / 100)
                if posiciones['result']['list'][0]['side'] == 'Buy':
                    stop_price = precio_de_entrada - aumento
                else:
                    stop_price = precio_de_entrada + aumento
                if stop_price < 0:
                    print('TU STOP LOSS NO ES POSIBLE, SE ENCUENTRA POR DEBAJO DE CERO')
                else:
                    # poner stop loss
                    if USDT != capital:
                        print('MODIFICANDO STOP LOSS')
                        establecer_stop_loss(symbol, stop_price)
                        capital = USDT
            else:
                session.cancel_all_orders(category="linear", settleCoin="USDT")
                estado = False
                capital = 0

        else:
            tick = input('INGRESE EL TICK QUE DESEA OPERAR: ').upper()
            if tick != '':
                tick = tick + 'USDT'
                symbol = tick
                stop = float(input('INGRESE EL VALOR MAXIMO EN USDT QUE DESEA PERDER: '))
                if stop != '':
                    stop_loss = stop
                    # Posiciones Abiertas
                    posiciones = session.get_positions(category="inverse", symbol=symbol)
                    if float(posiciones['result']['list'][0]['size']) != 0:
                        print('POSICION ABIERTA EN ' + symbol)
                        estado = True

                    else:
                        print('NO HAY NINGUNA POSICION ABIERTA EN ' + symbol)
                else:
                    print('EL DATO INGRESADO NO ES VALIDO')
            else:
                print('EL DATO INGRESADO NO ES VALIDO')

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
    time.sleep(1)
