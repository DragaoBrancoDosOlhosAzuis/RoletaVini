# roleta.py

import random

class Roleta:
    def __init__(self):
        self.nomes = {}

    def adicionar_nome(self, nome):
        """Adiciona um nome à roleta e redistribui as porcentagens"""
        self.nomes[nome] = 0  # Inicializa com 0%
        self._redistribuir_porcentagens()

    def remover_nome(self, nome):
        """Remove um nome da roleta e redistribui as porcentagens"""
        if nome in self.nomes:
            del self.nomes[nome]
            self._redistribuir_porcentagens()

    def _redistribuir_porcentagens(self):
        """Redistribui igualmente as porcentagens entre os nomes"""
        total_nomes = len(self.nomes)
        if total_nomes > 0:
            porcentagem = 100 / total_nomes
            for nome in self.nomes:
                self.nomes[nome] = porcentagem

    def sortear(self):
        """Realiza o sorteio baseado nas porcentagens atuais"""
        if not self.nomes:
            return "Nenhum nome na roleta"
        
        # Cria uma lista com os nomes repetidos conforme sua porcentagem
        roleta = []
        for nome, chance in self.nomes.items():
            roleta.extend([nome] * int(chance))
        
        return random.choice(roleta)
