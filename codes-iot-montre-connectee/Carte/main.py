# Lecture de deux capteurs du shield IKS01A3 et affichage sur le port serie de l'USB USER
# "Casting" RF des mesures avec la radio BLE du STM32WB55 
# Materiel : 
#  - Une carte NUCLEO-WB55
#  - Un shield X-NUCLEO IKS01A3

# Pression corrigee au niveau de la mer (necessite la valeur de l'altitude locale)
alti = 204
def PressionNivMer(pression, altitude):
	return pression * pow(1.0 - (altitude * 2.255808707E-5), -5.255)

from machine import I2C

import HTS221
import LPS22
from time import sleep_ms, time # Pour gÃ©rÃ©r les temporisations et l'horodatage
import ble_sensor # Pour implÃ©menter le protocole GATT pour Blue-ST
import bluetooth # Classes "primitives du BLE" 
# (voir https://docs.micropython.org/en/latest/library/ubluetooth.html)

# On utilise l'I2C n°1 de la carte NUCLEO-WB55 pour communiquer avec les capteurs
i2c = I2C(1)

# Pause d'une seconde pour laisser Ã  l'I2C le temps de s'initialiser
sleep_ms(1000)

# Liste des adresses I2C des peripheriques pesents
print("Adresses I2C utilisees : " + str(i2c.scan()))

# Instances des capteurs
sensor1 = HTS221.HTS221(i2c)
sensor2 = LPS22.LPS22(i2c)

# Instance de la classe BLE
ble = bluetooth.BLE()
ble_device = ble_sensor.BLESensor(ble)

while True:
	# Lecture des capteurs
	temp = sensor1.temperature()
	humi = sensor1.humidity()
	pres = PressionNivMer(sensor2.pressure(), alti)

	# Conversion en texte des valeurs renvoyees par les capteurs 
	stemp = str(round(temp,1))
	shumi = str(int(humi))
	spres = str(int(pres))

	# Affichage sur le port serie de l'USB USER
	print("Temperature : " + stemp + " °C, Humidite relative : " + shumi + " %, Pression : " + spres + " hPa")

	# Preparation des donnees pour envoi en BLE.
	# Le protocole Blue-ST code les temperatures, pressions et humidites sous forme de nombres entiers.
	# Donc on multiplie les diffÃ©rentes mesures par 10 ou par 100 pour conserver des decimales avant
	# d'arrondir a  l'entier le plus proche.
	# Par exemple si temp = 18.45°C => on envoie ble_temp = 184. 
	ble_pres = int(pres*100)
	ble_humi = int(humi*10)
	ble_temp = int(temp*10)
	timestamp = time()

	# Envoie des données en BLE 
	ble_device.set_data_env(timestamp, ble_pres, ble_humi, ble_temp, True) 

	sleep_ms(5000)
