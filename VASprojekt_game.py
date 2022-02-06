#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import time
from pipes import Template
from pandas import DatetimeIndex
import spade
import random
from spade.agent import Agent
from spade.behaviour import TimeoutBehaviour, CyclicBehaviour, PeriodicBehaviour
from sqlalchemy import false

template = spade.template.Template(metadata = {"ontology": "hookandring"})
msg_meta = {"ontology": "hookandring", "language": "english", "performative": "inform"}
agent1rez = 0
agent2rez = 0
korisnickiHook = ""

class Igrac1(Agent):
	
	def __init__(self, *args, ime, protivnik, stanje, brojBacanja):
		super().__init__(*args)
		self.ime = ime
		self.protivnik = protivnik
		self.stanje = stanje
		self.brojBacanja = brojBacanja
		
	class StanjeBaca(PeriodicBehaviour):
		async def run(self):
			global msg_meta

			self.agent.brojBacanja = random.randint(0, 10)
			print(f"{self.agent.ime}: je bacio {self.agent.brojBacanja}")
			poruka = spade.message.Message(to = self.agent.protivnik, body = str(self.agent.brojBacanja), metadata=msg_meta)
			await self.send(poruka)
			self.agent.remove_behaviour(self)
			self.agent.add_behaviour(self.agent.StanjeCekaIgraca(period=2), template)
	
	
	class StanjeCekaIgraca(PeriodicBehaviour):
		async def run(self):
			global msg_meta
			global agent1rez
			global agent2rez
			global korisnickiHook

			poruka = await self.receive(timeout=5)

			if poruka is not None:
				if(poruka.body == korisnickiHook):
					agent2rez = agent2rez + 1
					print("Agent2 je pogodio Hook, rezultat je: Agent1:", agent1rez, " Agent2:", agent2rez)
					if (agent2rez == 3):
						print("Agent2 je pobjedio Agenta1!")
					else:
						self.agent.remove_behaviour(self)
						self.agent.add_behaviour(self.agent.StanjeBaca(period = 2), template)
			else:
				self.agent.remove_behaviour(self)
				self.agent.add_behaviour(self.agent.StanjeBaca(period=2), template)
			
	async def setup(self):
		print("Pocinjemo")
		if(self.stanje == True):
			behaviour = self.StanjeBaca(period=2)
		else:
			behaviour = self.StanjeCekaIgraca(period=2)
		self.add_behaviour(behaviour, template)


class Igrac2(Agent):

	def __init__(self, *args, ime, protivnik, stanje, brojBacanja):
		super().__init__(*args)
		self.ime = ime
		self.protivnik = protivnik
		self.stanje = stanje
		self.brojBacanja = brojBacanja
		
	class StanjeBaca(PeriodicBehaviour):
		async def run(self):
			global msg_meta

			self.agent.brojBacanja = random.randint(0, 10)
			print(f"{self.agent.ime}: je bacio {self.agent.brojBacanja}")
			poruka = spade.message.Message(to = self.agent.protivnik, body = str(self.agent.brojBacanja), metadata=msg_meta)
			await self.send(poruka)
			self.agent.remove_behaviour(self)
			self.agent.add_behaviour(self.agent.StanjeCekaIgraca(period=2), template)


	class StanjeCekaIgraca(PeriodicBehaviour):
		async def run(self):
			global msg_meta
			global agent1rez
			global agent2rez
			global korisnickiHook

			poruka = await self.receive(timeout=5)

			if poruka is not None:
				if(poruka.body == korisnickiHook):
					agent1rez = agent1rez + 1
					print("Agent1 je pogodio Hook, rezultat je: Agent1:", agent1rez, " Agent2:", agent2rez)
					if (agent1rez == 3):
						print("Agent1 je pobjedio Agenta2!")
					else:
						self.agent.remove_behaviour(self)
						self.agent.add_behaviour(self.agent.StanjeBaca(period = 2), template)
			else:
				self.agent.remove_behaviour(self)
				self.agent.add_behaviour(self.agent.StanjeBaca(period=2), template)
			
	async def setup(self):
		print("Pocinjemo")
		if(self.stanje == True):
			behaviour = self.StanjeBaca(period=2)
		else:
			behaviour = self.StanjeCekaIgraca(period=2)
		self.add_behaviour(behaviour, template)

if __name__ == '__main__':

	print("Unesite Hook: ")
	korisnickiHook = str(input())

	Agent1 = Igrac1("agent1@localhost", "123", ime = "Agent1", protivnik = "agent2@localhost", stanje = True, brojBacanja = 0)
	Agent2 = Igrac2("agent2@localhost", "321", ime = "Agent2", protivnik = "agent1@localhost", stanje = False, brojBacanja = 0)

	Agent1.start()
	Agent2.start()
	
	input()

	Agent1.stop()
	Agent2.stop()

	spade.quit_spade()