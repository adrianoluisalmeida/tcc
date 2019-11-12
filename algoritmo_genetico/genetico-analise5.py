#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from scipy.optimize import minimize
from pandas_datareader import data as wb
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import matplotlib.pyplot as plt
%matplotlib inline
from random import random
import timeit
import datetime
import pymysql

class Ativo():
    def __init__(self, nome):
        self.nome = nome
        
class RetornosTemporais():
    def __init__(self, weights, algoritmo, volatilidade, retorno, sharpe, data_ini, data_fim, retornos_log):
        self.weights = weights
        self.algoritmo = algoritmo
        self.volatilidade = volatilidade
        self.retorno = retorno
        self.sharpe = sharpe
        self.data_ini = data_ini
        self.data_fim = data_fim
        self.retornos_log = retornos_log
        
    def calculos_indicadores(self, weights, retornos_log):
        self.weights = weights
        self.retornos_log = retornos_log
        
        self.retorno = np.sum(self.weights*self.retornos_log.mean())*250
        self.variancia = np.dot(self.weights.T, np.dot(self.retornos_log.cov() * 250, self.weights))
        self.volatilidade = np.sqrt(np.dot(self.weights.T, np.dot(self.retornos_log.cov() * 250, self.weights)))
        self.sharpe = self.retorno / self.volatilidade
        
class Individuo():
    def __init__(self, modelo, lista_ativos, retornos_log, geracao=0):
        self.nota_avaliacao = 0 #cada um vai ter uma nota para comparar se é bom ou não, em relação aos outros #singifica, somatório das rentabilidades
        self.modelo = modelo
        self.geracao = geracao
        self.lista_ativos = lista_ativos
        
        self.cromossomo = []
        self.retornos_log = retornos_log
        self.total = 0
        self.sharpe_min = modelo
        self.retorno = 0
        self.variancia = 0
        self.sharpe = 0
        self.volatilidade = 0
        self.total_ativos = 0
        self.weights = []
        

        for i in (range(len(self.lista_ativos))):
            
            if random() < 0.5: #50% probabilidade de por [1 ou 0]
                self.cromossomo.append("0")
            else:
                self.total_ativos+=1
                self.cromossomo.append("1")
                
        #formação cromossomo aleatorio (pesos)
        weights = self.geracao_pesos()
        
        
        
              
        j = 0
        for i in range(len(self.lista_ativos)):
            if(self.cromossomo[i] == "1"):
                self.weights.append(weights[j])
                j+=1
            else:
                self.weights.append(0)
        
        self.weights = np.array(self.weights)
        
        #print(self.weights)
        #for i in range(len(self.lista_ativos)):
        #   self.cromossomo.append(self.weights[i])
        
        self.calculos_indicadores()
        
           
    def geracao_pesos(self):
            weights = np.random.random(self.total_ativos)
            weights /= np.sum(weights)
            
            return weights
        
    def calculos_indicadores(self):
        
        self.retorno = np.sum(self.weights*self.retornos_log.mean())*250
        self.variancia = np.dot(self.weights.T, np.dot(self.retornos_log.cov() * 250, self.weights))
        self.volatilidade = np.sqrt(np.dot(self.weights.T, np.dot(self.retornos_log.cov() * 250, self.weights)))
        self.sharpe = self.retorno / self.volatilidade
        
   
        
    def avaliacao(self):
        nota = self.sharpe
        
        #somar = 0
        #for i in range(len(self.weights)):
        #    somar += self.weights[i]
            
        
        if nota < self.sharpe_min: #limite riscos
            nota = -1
            
       
        self.nota_avaliacao = nota
         
                
    def crossover(self, outro_individuo):
        corte = round(random() * len(self.cromossomo)) #random de 0 a 1; exemplo 0,45 * len(cromossomo)= 6,13414
         
        outro_individuo.weights = list(outro_individuo.weights)
        self.weights = list(self.weights)
        
        filho1 = outro_individuo.cromossomo[0:corte]+self.cromossomo[corte::] #corte:: => indica que é tudo para frente do corte
        filho1pesos = outro_individuo.weights[0:corte]+self.weights[corte::] #corte:: => indica que é tudo para frente do corte
        
        filho2 = self.cromossomo[0:corte] + outro_individuo.cromossomo[corte::]
        filho2pesos = self.weights[0:corte] + outro_individuo.weights[corte::]
        
        filhos = [Individuo(self.modelo, self.lista_ativos, self.retornos_log, self.geracao+1),
                  Individuo(self.modelo, self.lista_ativos, self.retornos_log, self.geracao+1)]
        
        filhos[0].cromossomo = filho1
        sumWeight = 0
        
        for i in range(len(filho1pesos)):
            sumWeight += filho1pesos[i]
            
        for i in range(len(filho1pesos)):
            if(filho1pesos[i] > 0):
                filho1pesos[i] = (filho1pesos[i]*1/sumWeight)
        
        sumWeight = 0
        for i in range(len(filho2pesos)):
            sumWeight += filho2pesos[i]
            
        for i in range(len(filho2pesos)):
            if(filho2pesos[i] > 0):
                filho2pesos[i] = (filho2pesos[i]*1/sumWeight)
                
        #print(sumWeight)
        filhos[0].weights = np.array(filho1pesos)
        
        filhos[1].cromossomo = filho2
        filhos[1].weights = np.array(filho2pesos)
        
        
        return filhos
    
    def mutacao(self, taxa_de_mutacao):
        temp = 0
        for i in range(len(self.cromossomo)):
            if random() < taxa_de_mutacao:
                if i + 1 < (len(self.cromossomo)-1):
                    
                    temp = self.cromossomo[i]    
                    self.cromossomo[i] = self.cromossomo[i+1]
                    self.cromossomo[i+1] = temp
                    
                else:
                    temp = self.cromossomo[i]
                    self.cromossomo[i] = self.cromossomo[i-1]
                    self.cromossomo[i-1] = temp
                    
                self.calculos_indicadores()
                    
        
        
        return self    
        
class AlgoritmoBruto():
    def __init__(self, tamanho_populacao, lista_ativos, numero_execucoes, retornos_log):
        self.tamanho_populacao = tamanho_populacao
        self.lista_ativos = lista_ativos
        self.numero_execucoes = numero_execucoes 
        self.retornos_log = retornos_log
        
        self.pfolio_returns = []
        self.pfolio_volatilities = []
        self.pfolio_sharpe = []
        self.pfolio_widgets = []
        
        
        
        self.total_pesos = 0
        
    
    def resolver(self):
        
        pfolio_returns = []
        pfolio_volatilities = []
        pfolio_sharpe = []
        pfolio_widgets = []
        pfolio_ativos = []
        total_ativos = 0
                
        for x in range(self.numero_execucoes):
            weights = []
            total_ativos = 0
            pfolio_ativos = []
            for i in range(len(self.lista_ativos)):
            
                if random() < 0.5: #50% probabilidade de por [1 ou 0]
                    pfolio_ativos.append("0")
                else:
                    total_ativos+=1
                    pfolio_ativos.append("1")
                
            #formação cromossomo aleatorio (pesos)
            weightsAtivos = np.random.random(total_ativos)
            weightsAtivos /= np.sum(weightsAtivos)
            
            j = 0
            for i in range(len(self.lista_ativos)):
                if(pfolio_ativos[i] == "1"):
                    weights.append(weightsAtivos[j])
                    j+=1
                else:
                    weights.append(0)
                    
            weights = np.array(weights)
            #weights  = np.random.random(len(self.lista_ativos))
            #weights /= np.sum(weights)
            pfolio_widgets.append(weights)
            pfolio_returns.append(np.sum(weights * self.retornos_log.mean()) * 250)
            pfolio_volatilities.append(np.sqrt(np.dot(weights.T, np.dot(self.retornos_log.cov() * 250, weights))))
            pfolio_sharpe.append(pfolio_returns[x] / pfolio_volatilities[x])
            
            
        self.pfolio_returns = np.array(pfolio_returns)
        self.pfolio_volatilities = np.array(pfolio_volatilities)
        self.pfolio_widgets = np.array(pfolio_widgets)
        self.pfolio_sharpe = np.array(pfolio_sharpe)
        
        print("Sharpe máximo na simulação: {}".format(self.pfolio_sharpe.max()))
        print("Índice sharpe máx: {}".format(self.pfolio_sharpe.argmax()))
        pfolio_index = self.pfolio_sharpe.argmax()
        
        print("Distribuição da carteira:")
        print(self.pfolio_widgets[pfolio_index, :])
        
        
            
        
        print("Volatilidade esperada: {}".format(self.pfolio_volatilities[pfolio_index]))
        print("Retorno esperado: {}".format(self.pfolio_returns[pfolio_index]))
        print("total pesos: {}".format(self.total_pesos))
        
        return True
        #self.pfolio_returns, pfolio_volatilities
    
class AlgoritmoGenetico():
    def __init__(self, tamanho_populacao, lista_ativos, dataframe, modelo, numero_geracoes, retornos_log):
        self.tamanho_populacao = tamanho_populacao
        self.lista_ativos = lista_ativos
        self.dataframe = dataframe
        self.modelo = modelo
        self.numero_geracoes = numero_geracoes
        self.retornos_log = retornos_log
        
        self.melhor_solucao = 0
        self.lista_solucoes = []
        self.populacao = [] #vai armazenar novos objetos da classe individuos
        self.geracao = 0
        
        self.pfolio_returns = []
        self.pfolio_volatilities = []
        self.pfolio_sharpe = []
        self.pfolio_widgets = []
        
        
    def soma_avaliacoes(self):
        soma = 0
        for individuo in self.populacao:
            soma += individuo.nota_avaliacao
            
        return soma
     
    
    def seleciona_pai(self, soma_avaliacao):
        pai = -1
        valor_sorteado = random() * soma_avaliacao
        print("soma %s" % soma_avaliacao)
        print("valor %s" % valor_sorteado)
        soma = 0
        i = 0
        while i < len(self.populacao) and soma < valor_sorteado:
            soma += self.populacao[i].nota_avaliacao
            pai += 1
            i += 1
            
        return pai
        
    
    def visualiza_geracao(self):
        melhor = self.populacao[0]
        #melhor.carteira.calculos_indicadores(melhor.cromossomo)
        print("G:%s Pesos: %s" % (melhor.geracao, melhor.weights))
        print("G:%s -> sharpe: %s Cromossomo: %s Retorno: %s Volatilidade %s" % (melhor.geracao, melhor.nota_avaliacao, melhor.cromossomo, melhor.retorno, melhor.volatilidade))
        
    def inicializa_populacao(self, modelo, lista_ativos):
        
       # self.retornos_log = np.log(self.dataframe / self.dataframe.shift(1))
        for i in range(self.tamanho_populacao):
            self.populacao.append(Individuo(modelo, lista_ativos, self.retornos_log))
            
        self.melhor_solucao = self.populacao[0]
        
    def orderna_populacao(self):
        #print(self.populacao)
        self.populacao = sorted(self.populacao, key = lambda populacao: populacao.nota_avaliacao, reverse = True)
    
    
        
    def melhor_individuo(self, individuo):
        if individuo.nota_avaliacao > self.melhor_solucao.nota_avaliacao:
            self.melhor_solucao = individuo
            
    def resolver(self, taxa_mutacao):
        self.inicializa_populacao(self.modelo, self.lista_ativos)
        
        for individuo in self.populacao:
            individuo.avaliacao()
        
        
        self.orderna_populacao()
        self.melhor_solucao = self.populacao[0]
        self.lista_solucoes.append(self.melhor_solucao.nota_avaliacao)
        self.visualiza_geracao()
        
        pfolio_returns = []
        pfolio_volatilities = []
        pfolio_sharpe = []
        pfolio_widgets = []
        
    
        for geracao in range(self.numero_geracoes):
            soma_avaliacao = self.soma_avaliacoes()
            nova_populacao = []
            
            
            for individuo_gerados in range(0, self.tamanho_populacao, 2):
                pai1 = self.seleciona_pai(soma_avaliacao)
                #pai1 = 0
                #pai2 = 1
                pai2 = self.seleciona_pai(soma_avaliacao)
                
                #crossover
                filhos = self.populacao[pai1].crossover(self.populacao[pai2])
                
                #print("pais:")
                #print(self.populacao[pai1].cromossomo)
                #print(self.populacao[pai2].cromossomo)
                
                #print("filhos:")
                #print(filhos[0].cromossomo)
                #print(filhos[1].cromossomo)
                
                #mutação
                nova_populacao.append(filhos[0].mutacao(taxa_mutacao))
                nova_populacao.append(filhos[1].mutacao(taxa_mutacao))
            
            self.populacao = list(nova_populacao)
            
            
            for individuo in self.populacao:
                individuo.calculos_indicadores()
                individuo.avaliacao()
            
            self.orderna_populacao()
            self.visualiza_geracao()
            
            melhor = self.populacao[0]
            self.lista_solucoes.append(melhor.nota_avaliacao)
            self.melhor_individuo(melhor)
            
            pfolio_returns.append(melhor.retorno)
            pfolio_volatilities.append(melhor.volatilidade)
            pfolio_sharpe.append(melhor.sharpe)
            pfolio_widgets.append(melhor.weights)
        
            somar = 0
            for i in range(len(melhor.weights)):
                somar += melhor.weights[i]
            
            print("TOTAL PESOS %s" % somar)
        
        for individuo in self.populacao:
            individuo.avaliacao()
        
        
        
        self.pfolio_returns = np.array(pfolio_returns)
        self.pfolio_volatilities = np.array(pfolio_volatilities)
        self.pfolio_sharpe = np.array(pfolio_sharpe)
        self.pfolio_widgets = np.array(pfolio_widgets)
        
        
        
            
        print("\n== Melhor solução == \n G: %s\n Sharpe: %s\n Cromossomo: %s\n Retorno Esperado: %s\n Volatilidade: %s" % (self.melhor_solucao.geracao, self.melhor_solucao.nota_avaliacao, self.melhor_solucao.cromossomo, self.melhor_solucao.retorno, self.melhor_solucao.volatilidade))
        return self.melhor_solucao.cromossomo
                
class Database():
    
    def __init__(self):
        self.connect = pymysql.connect(host="localhost", user="adriano", passwd="968574", db="tcc")
        
    def getPrice(self, cursor, code, dateStart, dateEnd):
        query = 'select adjclose, date from stock where code="'+code+'" and (date between "'+dateStart+'" and "'+dateEnd+'")'
        return cursor.execute(query)
    
    def getCodes(self, cursor, dateStart, dateEnd, lancamentos):
        
        query = 'select code, count(code) as total from stock where (date between "'+dateStart+'" and "'+dateEnd+'") group by code having total = '+lancamentos
        
        return cursor.execute(query)
    
    def getDates(self, cursor, dateStart, dateEnd):
        query = 'select date from stock where (date between "'+dateStart+'" and "'+dateEnd+'") group by date'
        return cursor.execute(query)
            
class Ativos():
    
    def __init__(self, date_ini, date_fim, lancamentos):
        self.ini = date_ini
        self.fim = date_fim
        self.lista_ativos = []
        self.frameAcoes = {}
        self.lancamentos = lancamentos
        self.dates = []
        self.connect = Database();
        
        cursor = self.connect.connect.cursor()
        self.connect.getCodes(cursor, self.ini, self.fim, self.lancamentos)
        
        for acao in cursor:
            self.lista_ativos.append(Ativo(acao[0]))
            
        cursor.close()
        
        #BUSCA DATAS
        cursor = self.connect.connect.cursor()
        self.connect.getDates(cursor, self.ini, self.fim)
        for date in cursor:
            self.dates.append(date[0])
            

        cursor.close()
        #self.lista_ativos.append(Ativo("ITUB4.SA"))
        #self.lista_ativos.append(Ativo("BBDC4.SA"))
        #self.lista_ativos.append(Ativo("BBAS3.SA"))
        #self.lista_ativos.append(Ativo("ABEV3.SA"))
    
    def setFrame(self, date_start, date_end):
        #self.connect = Database();
        #valores = []
        #cursor = connect.connect.cursor()
        for acao in self.lista_ativos: 
            #cursor.close()
            cursor = self.connect.connect.cursor()
            valores = []    
            
            self.connect.getPrice(cursor, acao.nome, date_start, date_end)
            #BUSCA PREÇO AÇÕES
            for acaoretorno in cursor:
                if(acaoretorno[0] == 0):
                    valores.append(np.nan)
                else:
                    valores.append(acaoretorno[0])
            
        
            self.frameAcoes.update({acao.nome: valores, 'Date': self.dates})
            
            cursor.close()
            
        self.connect.connect.close()
        
        return self.frameAcoes
        
if __name__ == '__main__':
    
    data_inicio = ('2010-1-1', '2014-1-1')
    data_fim = ('2014-1-1', '2018-1-1')
    retornos_temporais = []
    
    ativos = Ativos('2017-1-1', '2018-1-1', '254')
    
    frameAcoes = ativos.setFrame('2017-1-1', '2018-1-1')
    
    dataframe1 = pd.DataFrame(frameAcoes)
    dataframe1 = dataframe1.set_index('Date')
    
    dataframe1
    retornos_log = np.log(dataframe1 / dataframe1.shift(1))
    
    retornos_log.mean()
    ## ALGORITMO GENÉTICO ##
    start = timeit.default_timer()
    
    model = 1
    
    ag = AlgoritmoGenetico(10, ativos.lista_ativos, dataframe1, model, 10, retornos_log)
    resultado = ag.resolver(0.01)
    stop = timeit.default_timer()
    execution_time = stop - start
    print("Program Executed in {}".format(execution_time)) #It returns time in sec
    
    plt.plot(ag.lista_solucoes)
    plt.title("Acompanhamento dos valores")
    plt.show();
    
    max_ret = ag.pfolio_returns[ag.pfolio_sharpe.argmax()]
    max_vol = ag.pfolio_volatilities[ag.pfolio_sharpe.argmax()]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(ag.pfolio_volatilities, ag.pfolio_returns, c = ag.pfolio_sharpe, cmap = 'viridis')
    plt.colorbar(label = 'Índice sharpe')
    plt.xlabel('Volatilidade esperada ')
    plt.ylabel('Retorno esperado ')
    plt.scatter(max_vol, max_ret, c = 'red' , s=50 ) # ponto vermelho
    plt.show()
    
    #FORÇA BRUTA#
    
    start = timeit.default_timer()
        
    ab = AlgoritmoBruto(len(ativos.lista_ativos), ativos.lista_ativos, 1000, retornos_log)
    resultado = ab.resolver()
    
    stop = timeit.default_timer()
    execution_time = stop - start
    
    print("Program Executed in {}".format(execution_time)) #It returns time in sec
    
    max_ret = ab.pfolio_returns[ab.pfolio_sharpe.argmax()]
    max_vol = ab.pfolio_volatilities[ab.pfolio_sharpe.argmax()]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(ab.pfolio_volatilities, ab.pfolio_returns, c = ab.pfolio_sharpe, cmap = 'viridis')
    plt.colorbar(label = 'Índice sharpe')
    plt.xlabel('Volatilidade esperada ')
    plt.ylabel('Retorno esperado ')
    plt.scatter(max_vol, max_ret, c = 'red' , s=50 ) # ponto vermelho
    plt.show()
    
    #volatilidade, retorno, sharpe, data_ini, data_fim
    
    
    