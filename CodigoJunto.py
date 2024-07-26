import utime
from machine import Pin, I2C
import sh1106
from max6675 import MAX6675
from machine import Pin
import time

'''Declaración de puertos''' 
#MOTOR
EN = 5     # Define el enable
DIR = 6    # Define la dirección
PUL = 7    # Señal pulsada
#DIRECIONES
DER = 8    # Define la interrupción derecha
IZQ = 9    # Define la interrupción izquierda
PA = 10    # Define la interrupción de pausa
#OLED
i2c = I2C(1, scl=Pin(27), sda=Pin(26))
#TERMOCUPLA
so = Pin(12, Pin.IN)
sck = Pin(14, Pin.OUT)
cs = Pin(16, Pin.OUT)

'''Configuración de pines'''
#MOTOR
button_pin_derecha = Pin(DER, Pin.IN, Pin.PULL_UP)     # Botón Derecha
button_pin_izquierda = Pin(IZQ, Pin.IN, Pin.PULL_UP)   # Botón Izquierda
button_pin_pausa = Pin(PA, Pin.IN, Pin.PULL_UP)        # Botón Pausa
pul_pin = Pin(PUL, Pin.OUT)
dir_pin = Pin(DIR, Pin.OUT)
en_pin = Pin(EN, Pin.OUT)

'''Declaraciones iniciales'''
# Estado inicial y variables de control
paused = True  # Inicia en pausa para modo ahorro de energía
current_direction = None  # Variable para almacenar la dirección actual del movimiento

# Variables para debounce
debounce_delay = 500  # Retardo de debounce en milisegundos
last_interrupt_time = 0  # Variable para almacenar el tiempo de la última interrupción

#Variables de inicio display OLED
oled_width = 128
oled_height = 64
oled = sh1106.SH1106_I2C(oled_width, oled_height, i2c)

max = MAX6675(sck, cs , so)
dirMotor=''

'''FUNCIONES'''
# Función para mostrar texto y la variable en la pantalla
def mostrar_texto():
    temp = max.read()
    oled.fill(0)  # Limpia la pantalla
    oled.text('TEMPERATURA:', 0, 0)
    oled.text(str(temp), 0, 10)
    oled.text('DIRECCION:', 0, 20)
    if paused:
        oled.text('pausa', 0, 30)
    else:
        oled.text(str(dirMotor), 0, 30)
    oled.show()


def button_interrupt_handler_derecha(pin):
    global paused, current_direction, last_interrupt_time, dirMotor
    current_time = utime.ticks_ms()
    if current_time - last_interrupt_time > debounce_delay:
        last_interrupt_time = current_time
        if not paused:
            current_direction = "derecha"
            dirMotor = 'derecha'
            dir_pin.value(0)   # Dirección hacia la derecha
            en_pin.value(1)
            mostrar_texto()
            print("Iniciando movimiento a la derecha")

def button_interrupt_handler_izquierda(pin):
    global paused, current_direction, last_interrupt_time, dirMotor
    current_time = utime.ticks_ms()
    if current_time - last_interrupt_time > debounce_delay:
        last_interrupt_time = current_time
        if not paused:
            current_direction = "izquierda"
            dirMotor = 'izquierda'
            dir_pin.value(1)   # Dirección hacia la izquierda
            en_pin.value(1)
            mostrar_texto()
            print("Iniciando movimiento a la izquierda")

def button_interrupt_handler_pausa(pin):
    global paused, last_interrupt_time
    current_time = utime.ticks_ms()
    if current_time - last_interrupt_time > debounce_delay:
        last_interrupt_time = current_time
        if paused:
            print("Continuar")
            paused = False
            en_pin.value(1)  # Habilitar el motor
        else:
            print("Pausa")
            paused = True
            en_pin.value(0)  # Deshabilitar el motor
        mostrar_texto()

# Configuración de interrupciones
button_pin_derecha.irq(trigger=Pin.IRQ_FALLING, handler=button_interrupt_handler_derecha)
button_pin_izquierda.irq(trigger=Pin.IRQ_FALLING, handler=button_interrupt_handler_izquierda)
button_pin_pausa.irq(trigger=Pin.IRQ_FALLING, handler=button_interrupt_handler_pausa)

# Bucle principal
while True:
    if not paused:
        if current_direction == "derecha":
            dir_pin.value(0)   # Dirección hacia la derecha
            en_pin.value(1)
            while not paused:  # Continuar girando mientras no esté pausado
                mostrar_texto()
                pul_pin.value(1)
                utime.sleep_us(400)
                pul_pin.value(0)
                utime.sleep_us(400)

        elif current_direction == "izquierda":
            dir_pin.value(1)   # Dirección hacia la izquierda
            en_pin.value(1)
            while not paused:  # Continuar girando mientras no esté pausado
                mostrar_texto()
                pul_pin.value(1)
                utime.sleep_us(400)
                pul_pin.value(0)
                utime.sleep_us(400)

    else:
        en_pin.value(0)  # Deshabilitar el motor cuando está en pausa
        mostrar_texto()
        utime.sleep_ms(100)  # Pequeña pausa para reducir el uso de CPU
