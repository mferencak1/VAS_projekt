#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cProfile import run
import datetime
from logging import WARNING
from pickle import TRUE
import time
from pandas import DatetimeIndex

import spade
import random
import asyncio
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
from colorama import Fore
from colorama import Style

hook = ""
agent1rez = 0
agent2rez = 0

ponovoPokretanje1 = False
ponovoPokretanje2 = False

agent1bacanje = 0

agent2bacanje = 0

statistikaPokretanje = False


class FSMAgent(Agent):

    def __init__(self, *args, ime):
        super().__init__(*args)
        self.ime = ime
        
    class PonasanjeBase(FSMBehaviour):
        async def on_start(self):
            print(f"Zapocinje {self.agent.ime}!")

        async def on_end(self):
            print(f"Zavrsava {self.agent.ime}!")

    
    class StanjeZaprima(State):
        async def run(self):

            porukap = await self.receive(timeout=5)
            if porukap:
                if porukap.body == "ponovi":
                    self.set_next_state("StanjePogada")
            else:
                self.set_next_state("StanjePogada")


    class StanjePogada(State):
        async def run(self):

            rand = random.randint(0, 10)
            print(f"{Fore.YELLOW}{self.agent.ime} je bacio {rand}!{Style.RESET_ALL}")
            poruka = Message(to="voditelj@anoxinon.me")
            poruka.set_metadata("performative", "inform")
            poruka.sender = self.agent.ime
            poruka.body = str(rand) 
            await self.send(poruka)


    async def setup(self):

        fsmagent = self.PonasanjeBase()
        template1 = Template()
        template1.set_metadata("performative", "inform")

        fsmagent.add_state(name="StanjeZaprima", state=self.StanjeZaprima(), initial=True)
        fsmagent.add_state(name="StanjePogada", state=self.StanjePogada())
        fsmagent.add_transition(source="StanjeZaprima", dest="StanjePogada")
        self.add_behaviour(fsmagent,template1)         


class AgentVoditelj(Agent):
        
    class PrvojeraRezultata(CyclicBehaviour):
        
        async def run(self):

            global hook
            global agent1rez
            global agent2rez
            global ponovoPokretanje1
            global ponovoPokretanje2
            global agent1bacanje
            global agent2bacanje
            global statistikaPokretanje

            poruka = await self.receive(timeout=10)
            if poruka:
                print(f"{Fore.CYAN}Provjera rezultata!{Style.RESET_ALL}")
                if str(poruka.sender) == "agent 1":
                    agent1bacanje += 1
                    if (poruka.body == hook):
                        agent1rez += 1
                        if agent1rez == 3:
                            print(f"{Fore.GREEN}(Agent 1) {agent1rez} : {agent2rez} (Agent 2){Style.RESET_ALL}")
                            print(f"{Fore.GREEN}Agent 1 je pobjedio!{Style.RESET_ALL}")
                            statistikaPokretanje = True
                            await self.agent.stop()
                        else:
                            print(f"{Fore.CYAN}(Agent 1) {agent1rez} : {agent2rez} (Agent 2){Style.RESET_ALL}")
                            print(f"{Fore.CYAN}Agent 1 je pogodio, red je na Agenta 2!{Style.RESET_ALL}")
                            
                            ponovoPokretanje2 = True
                            await asyncio.sleep(5)
                            poruka1 = Message(to="mferencak1@anoxinon.me")
                            poruka1.set_metadata("performative", "inform")
                            poruka1.sender = "Voditelj"
                            poruka1.body = "ponovi"
                            await self.send(poruka1)
                               
                    else:
                        print(f"{Fore.CYAN}Agent 1 je promašio, red je na Agenta 2!{Style.RESET_ALL}")
                        
                        ponovoPokretanje2 = True
                        await asyncio.sleep(5)
                        poruka2 = Message(to="mferencak1@anoxinon.me")
                        poruka2.set_metadata("performative", "inform")
                        poruka2.sender = "Voditelj"
                        poruka2.body = "ponovi"
                        await self.send(poruka2)
                       
                elif str(poruka.sender) == "agent 2":
                    agent2bacanje += 1
                    if(poruka.body == hook):
                        agent2rez += 1
                        if agent2rez == 3:
                            print(f"{Fore.GREEN}(Agent 1) {agent1rez} : {agent2rez} (Agent 2){Style.RESET_ALL}")
                            print(f"{Fore.GREEN}Agent 2 je pobjedio!{Style.RESET_ALL}")
                            statistikaPokretanje = True
                            await self.agent.stop()
                        else:
                            print(f"{Fore.CYAN}(Agent 1) {agent1rez} : {agent2rez} (Agent 2){Style.RESET_ALL}")
                            print(f"{Fore.CYAN}Agent 2 je pogodio, red je na Agenta 1!{Style.RESET_ALL}")

                            ponovoPokretanje1 = True
                            await asyncio.sleep(5)
                            poruka3 = Message(to="mferencak@anoxinon.me")                           
                            poruka3.set_metadata("performative", "inform")
                            poruka3.sender = "Voditelj"
                            poruka3.body = "ponovi"
                            await self.send(poruka3) 
                    else:
                        print(f"{Fore.CYAN}Agent 2 je promašio, red je na Agenta 1!{Style.RESET_ALL}")

                        ponovoPokretanje1 = True
                        await asyncio.sleep(5)
                        poruka4 = Message(to="mferencak@anoxinon.me")
                        poruka4.set_metadata("performative", "inform")
                        poruka4.sender = "Voditelj"
                        poruka4.body = "ponovi"
                        await self.send(poruka4)


    async def setup(self):

        print(f"{Fore.CYAN}Voditelj se pokrece!{Style.RESET_ALL}")
        self.posiljatelj = ""
        self.brojBacanja = ""

        agent = self.PrvojeraRezultata()
        template1 = Template()
        template1.set_metadata("performative", "inform")
        self.add_behaviour(agent,template1)


class AgentStatistika(Agent):

    class IspisStatistike(OneShotBehaviour):
        async def run(self):
            promasaji1 = agent1bacanje - agent1rez
            postotak1 = (agent1rez/agent1bacanje)*100
            postotakpro1 = 100-postotak1
            print(f"{Fore.LIGHTMAGENTA_EX}Agent 1 je ukupno bacao: {agent1bacanje}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTMAGENTA_EX}Agent 1 je pogodio: {agent1rez}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTMAGENTA_EX}Agent 1 je promašio: {promasaji1}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTMAGENTA_EX}Postotak pogotka: {round(postotak1,2)}%{Style.RESET_ALL}")
            print(f"{Fore.LIGHTMAGENTA_EX}Postotak promašaja: {round(postotakpro1,2)}%{Style.RESET_ALL}")

            print()

            promasaji2 = agent2bacanje - agent2rez
            postotak2 = (agent2rez/agent2bacanje)*100
            postotakpro2 = 100-postotak2
            print(f"{Fore.LIGHTRED_EX}Agent 2 je ukupno bacao: {agent2bacanje}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}Agent 2 je pogodio: {agent2rez}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}Agent 2 je promašio: {promasaji2}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}Postotak pogotka: {round(postotak2,2)}%{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}Postotak promašaja: {round(postotakpro2,2)}%{Style.RESET_ALL}")

    async def setup(self):
        print(f"{Fore.MAGENTA}Ispis statistike: \n{Style.RESET_ALL}")
        agentStat = self.IspisStatistike()
        self.add_behaviour(agentStat)


if __name__ == '__main__':
    
    pocetak = time.time()
    print("Unesite hook: ")
    hook = str(input())

    #voditelj cyclic
    voditelj = AgentVoditelj("voditelj@anoxinon.me", "12345")

    #agenta 1 i 2 fsm
    agent1 = FSMAgent("mferencak@anoxinon.me", "1234", ime="Agent 1")
    agent2 = FSMAgent("mferencak1@anoxinon.me", "4321", ime="Agent 2")

    #statisticar oneshot
    statisticar = AgentStatistika("statisticar@anoxinon.me", "54321")

    pokretanjeVoditelja = voditelj.start()
    pokretanjeVoditelja.result()

    pokretanjeAgent1 = agent1.start()
    pokretanjeAgent1.result()

    
    while True:
        if ponovoPokretanje1:
            pokretanjeAgent1 = agent1.start()
            ponovoPokretanje1 = False

        elif ponovoPokretanje2:
            pokretanjeAgent2 = agent2.start()
            pokretanjeAgent2.result()
            ponovoPokretanje2 = False

        elif statistikaPokretanje:
            kraj = time.time()
            trajanje = kraj - pocetak
            trajanje1 = time.gmtime(trajanje)
            print("Trajanje igre: ",time.strftime("%H:%M:%S",trajanje1))
            pokretanjeStatisticara = statisticar.start()
            pokretanjeStatisticara.result()
            quit_spade()
            break