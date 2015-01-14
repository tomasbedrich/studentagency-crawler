#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import requests
from prettytable import PrettyTable
from datetime import datetime
from bs4 import BeautifulSoup


class StudentAgency(object):

    _baseurl = "http://jizdenky.studentagency.cz/m/Booking/from/" \
        "{start}/to/{end}/tarif/{tarif}/departure/{departure}/retdep/{retdep}/return/{ret}/credit/{credit}"

    destinations = {
        "BA": "Bratislava",
        "BB": "Banská Bystrica",
        "BJ": "Bardejov",
        "BR": "Brno",
        "CAD": "Čadca",
        "CB": "České Budějovice",
        "CET": "Český Těšín,",
        "CHEB": "Cheb",
        "CHO": "Chomutov,",
        "CKA": "Český Krumlov-AN",
        "CKS": "Český Krumlov-Špičák",
        "FM": "Frýdek-Místek",
        "HAV": "Havířov",
        "HK": "Hradec Králové",
        "HNM": "Hranice na Moravě",
        "JH": "Jindřichův Hradec",
        "JI": "Jihlava",
        "KE": "Košice",
        "KM": "Kroměříž",
        "KNM": "Kysucké Nové Mesto",
        "KVTE": "Karlovy Vary",
        "KZ": "Kežmarok",
        "LBA": "Liberec-AN",
        "LBF": "Liberec-Fügnerova",
        "LC": "Lučenec",
        "LE": "Levoča",
        "LM": "Liptovský Mikuláš",
        "LNY": "Louny -autobus. nádraží",
        "MON": "Most-1. náměstí",
        "MOR": "Most-Rudolická",
        "NJ": "Nový Jičín",
        "NR": "Nitra",
        "OLH": "Olomouc-hlavní nádraží",
        "OVA": "Ostrava-ÚAN",
        "OVH": "Ostrava-hlavní nádraží",
        "OVS": "Ostrava-Svinov",
        "OVT": "Ostrava-Stodolní",
        "PAR": "Pardubice",
        "PB": "Považská Bystrica",
        "PBR": "Příbor",
        "PCM": "Praha-Černý Most",
        "PD": "Podolínec",
        "PDE": "Praha-Dejvická",
        "PE": "Pelhřimov",
        "PFL": "Praha-Florenc",
        "PHN": "Praha-hlavní nádraží",
        "PI": "Písek",
        "PKN": "Praha-Knížecí",
        "PLA": "Plzeň-CAN",
        "PLB": "Praha-Libeň",
        "PLR": "Plzeň-Rokycanská,",
        "PO": "Prešov",
        "PP": "Poprad",
        "PVH": "Praha-Letiště Václava Havla",
        "PZL": "Praha-Zličín",
        "RK": "Ružomberok",
        "RS": "Rimavská Sobota",
        "RV": "Rožňava",
        "SL": "Stará L'ubovňa",
        "SM": "Staré Město",
        "SOK": "Sokolov-Terminál,",
        "TA": "Tábor",
        "TC": "Telč,",
        "TES": "Sokolov-Těšovice",
        "TN": "Trenčín",
        "TR": "Třebíč",
        "TRI": "Třinec",
        "UH": "Uherské Hradiště",
        "UNO": "Ústí nad Orlicí",
        "VPR": "Vídeň-Lassallestrasse/Praterstern",
        "VR": "Vrútky,",
        "VSW": "Vídeň-letiště Schwechat",
        "ZAA": "Žilina",
        "ZAB": "Zábřeh na Moravě",
        "ZAH": "Žilina, hl. zel. stanica",
        "ZH": "Žiar nad Hronom",
        "ZLN": "Zlín",
        "ZV": "Zvolen"
    }

    tarif = {
        "REGULAR": "Dospělý",
        "CZECH_STUDENT_PASS_26": "Student (žák. průkaz < 26)",
        "CZECH_STUDENT_PASS_15": "Žák (žák. průkaz < 15)",
        "ISIC": "ISIC",
        "CHILD": "Dítě"
    }

    def __init__(self, start, end, tarif, day, credit):
        super(StudentAgency, self).__init__()
        self.start = start
        self.end = end
        self.tarif = tarif
        self.day = day
        self.credit = credit

        self.session = requests.Session()

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        if start in self.destinations:
            self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        if end in self.destinations:
            self._end = end

    @property
    def tarif(self):
        return self._tarif

    @tarif.setter
    def tarif(self, tarif):
        self._tarif = tarif

    @property
    def day(self):
        return self._day

    @day.setter
    def day(self, day):
        self._day = day

    @property
    def credit(self):
        return self._credit

    @credit.setter
    def credit(self, credit):
        self._credit = credit

    def fetch(self):

        if not (self.start and self.end and self.tarif and self.day and self.credit):
            return

        url = self._baseurl.format(
            start=self.start,
            end=self.end,
            tarif=self.tarif,
            departure=self.day,
            retdep=self.day,
            ret=False,
            credit=self.credit
        )
        request = self.session.post(url)
        bs = BeautifulSoup(request.text)
        linesRaw = bs.find("div", "detail-tabs").find_all("div", "select-line")
        busLines = []

        for lineRaw in linesRaw:
            departure = lineRaw.find("span", "departure").text
            arrival = lineRaw.find("span", "arrival").text
            seats = lineRaw.find("span", "free").text
            services = lineRaw.find("span", "type").img.get("title").startswith("Ekonomy") and "economy" or "normal"
            price = lineRaw.find("span", "price").text
            bus = Bus(departure, arrival, seats, services, price)
            busLines.append(bus)

        return busLines

    def printOutput(self, busLines):
        table = PrettyTable(["Type", "Departure", "Arrival", "Seats", "Price"])
        table.align["Seats"] = "r"
        table.align["Price"] = "r"
        for bus in filter(lambda i: isinstance(i, Bus), busLines):
            table.add_row([bus.services, bus.departure, bus.arrival, bus.seats, bus.price])
        print(table)


class Bus(object):

    def __init__(self, departure, arrival, seats, services, price):
        super(Bus, self).__init__()
        self.departure = departure
        self.arrival = arrival
        self.seats = seats
        self.services = services
        self.price = price


if __name__ == "__main__":
    now = datetime.utcnow().strftime("%Y%m%d")
    sa = StudentAgency("PZL", "PLA", "CZECH_STUDENT_PASS_26", now, True)
    sa.printOutput(sa.fetch())
